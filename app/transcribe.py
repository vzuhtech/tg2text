import io
from typing import Optional
from openai import AsyncOpenAI


class OpenAITranscriber:
	def __init__(self, api_key: str) -> None:
		self.client = AsyncOpenAI(api_key=api_key)

	async def transcribe_ogg_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> str:
		file_like = io.BytesIO(audio_bytes)
		file_like.name = "voice.ogg"
		params = {"model": "whisper-1"}
		if language:
			params["language"] = language
		result = await self.client.audio.transcriptions.create(
			file=file_like,
			**params,
		)
		return (result.text or "").strip()