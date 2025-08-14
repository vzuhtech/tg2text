import asyncio
import hashlib
import os
import zipfile
import tarfile
from typing import Optional

import httpx


async def ensure_vosk_model(model_dir: str, download_url: str, sha256_hex: Optional[str] = None) -> str:
	"""Ensure Vosk model exists at model_dir. If missing, download and extract from download_url.

	Returns the path to the model directory.
	"""
	# If directory looks valid (non-empty), reuse
	if os.path.isdir(model_dir) and any(os.scandir(model_dir)):
		return model_dir

	parent_dir = os.path.dirname(model_dir) or "."
	os.makedirs(parent_dir, exist_ok=True)

	# Download archive
	archive_path = os.path.join(parent_dir, "vosk-model-download.tmp")
	async with httpx.AsyncClient(timeout=120) as client:
		async with client.stream("GET", download_url) as resp:
			resp.raise_for_status()
			hasher = hashlib.sha256()
			with open(archive_path, "wb") as f:
				async for chunk in resp.aiter_bytes():
					if not chunk:
						continue
					hasher.update(chunk)
					f.write(chunk)
			computed = hasher.hexdigest()
			if sha256_hex and computed.lower() != sha256_hex.lower():
				raise RuntimeError(f"Vosk model checksum mismatch: expected {sha256_hex}, got {computed}")

	# Extract
	extracted_root = None
	if zipfile.is_zipfile(archive_path):
		with zipfile.ZipFile(archive_path) as zf:
			# Determine top-level directory name
			names = zf.namelist()
			root = names[0].split("/")[0] if names else "vosk-model"
			extracted_root = os.path.join(parent_dir, root)
			zf.extractall(parent_dir)
	elif tarfile.is_tarfile(archive_path):
		with tarfile.open(archive_path) as tf:
			members = tf.getmembers()
			root = members[0].name.split("/")[0] if members else "vosk-model"
			extracted_root = os.path.join(parent_dir, root)
			tf.extractall(parent_dir)
	else:
		raise RuntimeError("Unsupported archive format for Vosk model (expected .zip or .tar.*)")

	# Move/rename extracted dir to desired model_dir if different
	if extracted_root and os.path.abspath(extracted_root) != os.path.abspath(model_dir):
		# If target exists (race), skip move
		if not os.path.exists(model_dir):
			os.replace(extracted_root, model_dir)

	# Cleanup archive
	try:
		os.remove(archive_path)
	except Exception:
		pass

	# Final check
	if not (os.path.isdir(model_dir) and any(os.scandir(model_dir))):
		raise RuntimeError("Vosk model extraction failed or directory is empty")
	return model_dir