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
	app_base_url: str
	secret_token: str | None = None
	debug: bool = False

	class Config:
		arbitrary_types_allowed = True


def get_settings() -> Settings:
	return Settings(
		telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
		openai_api_key=os.getenv("OPENAI_API_KEY", ""),
		app_base_url=os.getenv("APP_BASE_URL", ""),
		secret_token=os.getenv("WEBHOOK_SECRET", None),
		debug=_env_bool("DEBUG", False),
	)