"""Descarga de ZIP."""

from __future__ import annotations

from pathlib import Path

import requests


class DownloaderService:
	"""Download remote files to disk."""

	def __init__(self, session: requests.Session | None = None):
		self.session = session or requests.Session()

	def download(self, url: str, output_path: str | Path, chunk_size: int = 1024 * 1024) -> Path:
		destination = Path(output_path)
		destination.parent.mkdir(parents=True, exist_ok=True)

		response = self.session.get(url, stream=True, timeout=60)
		response.raise_for_status()

		with destination.open("wb") as target:
			for chunk in response.iter_content(chunk_size=chunk_size):
				if chunk:
					target.write(chunk)

		return destination
