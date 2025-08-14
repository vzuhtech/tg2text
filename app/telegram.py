import httpx
from typing import Any, Dict, Optional


class TelegramAPI:
	def __init__(self, bot_token: str) -> None:
		self.base_url = f"https://api.telegram.org/bot{bot_token}"
		self.file_url = f"https://api.telegram.org/file/bot{bot_token}"
		self.client = httpx.AsyncClient(timeout=30)

	async def set_webhook(self, url: str, secret_token: Optional[str] = None) -> Dict[str, Any]:
		payload: Dict[str, Any] = {"url": url}
		if secret_token:
			payload["secret_token"] = secret_token
		resp = await self.client.post(f"{self.base_url}/setWebhook", json=payload)
		resp.raise_for_status()
		return resp.json()

	async def send_message(self, chat_id: int, text: str, reply_to_message_id: Optional[int] = None) -> Dict[str, Any]:
		payload: Dict[str, Any] = {"chat_id": chat_id, "text": text}
		if reply_to_message_id:
			payload["reply_to_message_id"] = reply_to_message_id
		resp = await self.client.post(f"{self.base_url}/sendMessage", json=payload)
		resp.raise_for_status()
		return resp.json()

	async def get_file(self, file_id: str) -> Dict[str, Any]:
		resp = await self.client.get(f"{self.base_url}/getFile", params={"file_id": file_id})
		resp.raise_for_status()
		return resp.json()

	async def download_file_bytes(self, file_path: str) -> bytes:
		resp = await self.client.get(f"{self.file_url}/{file_path}")
		resp.raise_for_status()
		return resp.content

	async def close(self) -> None:
		await self.client.aclose()