from pydantic import BaseModel
import os


class Settings(BaseModel):
	telegram_bot_token: str
	openai_api_key: str
	app_base_url: str
	secret_token: str | None = None

	class Config:
		arbitrary_types_allowed = True


def get_settings() -> Settings:
	return Settings(
		telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
		openai_api_key=os.getenv("OPENAI_API_KEY", ""),
		app_base_url=os.getenv("APP_BASE_URL", ""),
		secret_token=os.getenv("WEBHOOK_SECRET", None),
	)