from pathlib import Path
import shutil
import zipfile

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Descomprime los ZIP descargados"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Sobrescribe carpetas existentes sin preguntar",
        )

    def handle(self, *args, **options):

        downloads_dir = Path("/app/backend/downloads")

        zip_files = sorted(downloads_dir.glob("*.zip"))

        for zip_file in zip_files:

            dest_dir = downloads_dir / zip_file.stem

            if dest_dir.exists():

                if not options["force"]:

                    respuesta = input(
                        f"\nLa carpeta '{dest_dir.name}' ya existe.\n"
                        "¿Sobrescribir? [s/N]: "
                    ).strip().lower()

                    if respuesta not in ("s", "si", "sí"):
                        self.stdout.write(
                            self.style.WARNING(
                                f"Saltando {zip_file.name}"
                            )
                        )
                        continue

                shutil.rmtree(dest_dir)

            dest_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_file, "r") as zip_ref:
                zip_ref.extractall(dest_dir)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Descomprimido: {zip_file.name}"
                )
            )