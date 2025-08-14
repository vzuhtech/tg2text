import json
import shutil
import subprocess
import tempfile
from typing import Optional

import vosk


class VoskTranscriber:
	def __init__(self, model_path: str, ffmpeg_bin: str = "ffmpeg") -> None:
		if not shutil.which(ffmpeg_bin):
			raise RuntimeError("ffmpeg not found. Set FFMPEG_BIN or install ffmpeg.")
		self.ffmpeg_bin = ffmpeg_bin
		self.model = vosk.Model(model_path)

	def _ogg_to_pcm16le(self, ogg_bytes: bytes) -> bytes:
		# Convert to 16kHz, mono, 16-bit little endian PCM via ffmpeg
		proc = subprocess.Popen(
			[
				self.ffmpeg_bin,
				"-loglevel",
				"error",
				"-i",
				"pipe:0",
				"-ac",
				"1",
				"-ar",
				"16000",
				"-f",
				"s16le",
				"pipe:1",
			],
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE,
		)
		stdout, stderr = proc.communicate(input=ogg_bytes, timeout=60)
		if proc.returncode != 0:
			raise RuntimeError(f"ffmpeg failed: {stderr.decode('utf-8', 'ignore')}")
		return stdout

	async def transcribe_ogg_bytes(self, audio_bytes: bytes, language: Optional[str] = None) -> str:
		pcm = self._ogg_to_pcm16le(audio_bytes)
		rec = vosk.KaldiRecognizer(self.model, 16000)
		# Feed in chunks to avoid large memory spikes
		chunk_size = 4000
		for i in range(0, len(pcm), chunk_size):
			rec.AcceptWaveform(pcm[i : i + chunk_size])
		final = rec.FinalResult()
		try:
			data = json.loads(final)
			text = (data.get("text") or "").strip()
			return text
		except Exception:
			return ""