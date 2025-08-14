from pydantic import BaseModel
import os


def _env_bool(name: str, default: bool = False) -> bool:
	val = os.getenv(name)
	if val is None:
		return default
	val_lower = val.strip().lower()
	return val_lower in ("1", "true", "yes", "on")


class Settings(BaseModel):
	telegram_bot_token: str
	openai_api_key: str
	openai_org_id: str | None = None
	openai_project_id: str | None = None
	app_base_url: str
	secret_token: str | None = None
	debug: bool = False
	stt_provider: str = "openai"  # "openai" or "vosk"
	vosk_model_path: str | None = None
	ffmpeg_bin: str = os.getenv("FFMPEG_BIN", "ffmpeg")

	class Config:
		arbitrary_types_allowed = True


def get_settings() -> Settings:
	return Settings(
		telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
		openai_api_key=os.getenv("OPENAI_API_KEY", ""),
		openai_org_id=os.getenv("OPENAI_ORG_ID", None),
		openai_project_id=os.getenv("OPENAI_PROJECT_ID", None),
		app_base_url=os.getenv("APP_BASE_URL", ""),
		secret_token=os.getenv("WEBHOOK_SECRET", None),
		debug=_env_bool("DEBUG", False),
		stt_provider=os.getenv("STT_PROVIDER", "openai").strip().lower(),
		vosk_model_path=os.getenv("VOSK_MODEL_PATH", None),
		ffmpeg_bin=os.getenv("FFMPEG_BIN", "ffmpeg"),
	)