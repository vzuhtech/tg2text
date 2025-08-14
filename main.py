import os
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.telegram import TelegramAPI
from app.transcribe import OpenAITranscriber

app = FastAPI()


@app.get("/health")
async def health() -> Dict[str, str]:
	return {"status": "ok"}


@app.on_event("startup")
async def on_startup() -> None:
	settings = get_settings()
	if not settings.telegram_bot_token or not settings.openai_api_key:
		# Fail-fast if config missing
		raise RuntimeError("TELEGRAM_BOT_TOKEN and OPENAI_API_KEY must be set")
	app.state.tg = TelegramAPI(settings.telegram_bot_token)
	app.state.asr = OpenAITranscriber(settings.openai_api_key)
	# Auto-set webhook if APP_BASE_URL provided
	if settings.app_base_url:
		url = settings.app_base_url.rstrip("/") + "/webhook/telegram"
		try:
			await app.state.tg.set_webhook(url, settings.secret_token)
		except Exception:
			# Ignore webhook failures during local dev
			pass


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
		# not a voice - prompt user
		await app.state.tg.send_message(chat_id, "Пожалуйста, пришли голосовое сообщение (voice).", reply_to_message_id=message_id)
		return JSONResponse({"ok": True})

	file_id = voice.get("file_id")
	if not file_id:
		return JSONResponse({"ok": True})

	# Fetch and download file
	file_info = await app.state.tg.get_file(file_id)
	file_path = (file_info.get("result") or {}).get("file_path")
	if not file_path:
		await app.state.tg.send_message(chat_id, "Не смог получить файл от Telegram.", reply_to_message_id=message_id)
		return JSONResponse({"ok": True})

	data = await app.state.tg.download_file_bytes(file_path)

	# Transcribe via OpenAI
	try:
		transcript = await app.state.asr.transcribe_ogg_bytes(data)
		if not transcript:
			transcript = "Не получилось распознать голос."
	except Exception:
		transcript = "Произошла ошибка распознавания. Попробуйте ещё раз."

	await app.state.tg.send_message(chat_id, transcript, reply_to_message_id=message_id)
	return JSONResponse({"ok": True})