import os
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging

from app.config import get_settings
from app.telegram import TelegramAPI
from app.transcribe import OpenAITranscriber
from app.vosk_asr import VoskTranscriber
from app.vosk_download import ensure_vosk_model

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tg2text")

app = FastAPI()


@app.get("/health")
async def health() -> Dict[str, str]:
	return {"status": "ok"}


@app.on_event("startup")
async def on_startup() -> None:
	settings = get_settings()
	if not settings.telegram_bot_token:
		raise RuntimeError("TELEGRAM_BOT_TOKEN must be set")
	app.state.tg = TelegramAPI(settings.telegram_bot_token)
	# Select STT provider
	if settings.stt_provider == "vosk":
		# decide model directory
		model_dir = settings.vosk_model_path or os.path.join(settings.vosk_storage_dir, "vosk-model")
		try:
			model_dir = await ensure_vosk_model(model_dir, settings.vosk_model_url, settings.vosk_model_sha256)
			logger.info("Vosk model ready at %s", model_dir)
		except Exception as e:
			logger.exception("Failed to prepare Vosk model: %s", e)
			raise
		app.state.asr = VoskTranscriber(model_dir, ffmpeg_bin=settings.ffmpeg_bin)
	else:
		if not settings.openai_api_key:
			raise RuntimeError("OPENAI_API_KEY must be set for OpenAI STT")
		app.state.asr = OpenAITranscriber(
			settings.openai_api_key,
			organization=settings.openai_org_id,
			project=settings.openai_project_id,
		)
	if settings.app_base_url:
		url = settings.app_base_url.rstrip("/") + "/webhook/telegram"
		try:
			await app.state.tg.set_webhook(url, settings.secret_token)
			logger.info("Webhook set to %s", url)
		except Exception as e:
			logger.exception("Failed to set webhook: %s", e)


@app.on_event("shutdown")
async def on_shutdown() -> None:
	tg: TelegramAPI = app.state.tg
	await tg.close()


async def _verify_secret(request: Request) -> None:
	settings = get_settings()
	if settings.secret_token:
		recv = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
		if recv != settings.secret_token:
			raise HTTPException(status_code=403, detail="invalid secret token")


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request) -> JSONResponse:
	await _verify_secret(request)
	update: Dict[str, Any] = await request.json()
	message: Optional[Dict[str, Any]] = update.get("message") or update.get("edited_message")
	if not message:
		return JSONResponse({"ok": True})

	chat = message.get("chat", {})
	chat_id = chat.get("id")
	message_id = message.get("message_id")

	text = message.get("text")
	if text and text.strip().lower() in ("/start", "start"):
		await app.state.tg.send_message(chat_id, "Отправь голосовое сообщение, я пришлю текст.", reply_to_message_id=message_id)
		return JSONResponse({"ok": True})

	voice = message.get("voice") or message.get("audio") or message.get("video_note")
	if not voice:
		await app.state.tg.send_message(chat_id, "Пожалуйста, пришли голосовое сообщение (voice).", reply_to_message_id=message_id)
		return JSONResponse({"ok": True})

	file_id = voice.get("file_id")
	if not file_id:
		return JSONResponse({"ok": True})

	try:
		file_info = await app.state.tg.get_file(file_id)
		file_path = (file_info.get("result") or {}).get("file_path")
		if not file_path:
			await app.state.tg.send_message(chat_id, "Не смог получить файл от Telegram.", reply_to_message_id=message_id)
			return JSONResponse({"ok": True})
		data = await app.state.tg.download_file_bytes(file_path)
		logger.info("Downloaded voice file %s (%d bytes)", file_path, len(data))
	except Exception as e:
		logger.exception("Failed to download voice: %s", e)
		await app.state.tg.send_message(chat_id, "Ошибка получения файла от Telegram.", reply_to_message_id=message_id)
		return JSONResponse({"ok": True})

	settings = get_settings()
	try:
		transcript = await app.state.asr.transcribe_ogg_bytes(data)
		if not transcript:
			transcript = "Не получилось распознать голос."
	except Exception as e:
		logger.exception("Transcription error: %s", e)
		msg = str(e)
		if "insufficient_quota" in msg or "You exceeded your current quota" in msg:
			user_text = "Лимит OpenAI исчерпан. Проверь план и биллинг аккаунта."
		elif settings.debug:
			user_text = f"Ошибка распознавания: {e}"
		else:
			user_text = "Произошла ошибка распознавания. Попробуйте ещё раз."
		await app.state.tg.send_message(chat_id, user_text, reply_to_message_id=message_id)
		return JSONResponse({"ok": True})

	await app.state.tg.send_message(chat_id, transcript, reply_to_message_id=message_id)
	return JSONResponse({"ok": True})