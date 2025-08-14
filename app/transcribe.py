import io
from typing import Optional
from openai import AsyncOpenAI


class OpenAITranscriber:
	def __init__(self, api_key: str, organization: Optional[str] = None, project: Optional[str] = None) -> None:
		client_kwargs = {"api_key": api_key}
		if organization:
			client_kwargs["organization"] = organization
		if project:
			client_kwargs["project"] = project
		self.client = AsyncOpenAI(**client_kwargs)

	async def transcribe_ogg_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> str:
		file_like = io.BytesIO(audio_bytes)
		file_like.name = "voice.ogg"
		models = ("whisper-1", "gpt-4o-mini-transcribe")
		last_err: Exception | None = None
		for model_name in models:
			file_like.seek(0)
			params = {"model": model_name}
			if language:
				params["language"] = language
			try:
				result = await self.client.audio.transcriptions.create(
					file=file_like,
					**params,
				)
				text = (getattr(result, "text", None) or "").strip()
				if text:
					return text
			except Exception as e:  # noqa: BLE001
				last_err = e
		if last_err:
			raise last_err
		return ""