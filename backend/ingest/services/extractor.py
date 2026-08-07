"""Descompresión de ZIP."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile


class ExtractorService:
	"""Extract ZIP files."""

	def extract(self, zip_path: str | Path, output_dir: str | Path) -> Path:
		zip_file = Path(zip_path)
		destination = Path(output_dir)
		destination.mkdir(parents=True, exist_ok=True)

		with ZipFile(zip_file) as archive:
			archive.extractall(destination)

		return destination
