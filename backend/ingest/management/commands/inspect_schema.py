from pathlib import Path
from subprocess import run

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Inspecciona el esquema de los GML usando ogrinfo"

    def handle(self, *args, **options):

        downloads_dir = Path("/app/backend/downloads")

        output_file = downloads_dir / "schema_inspection.txt"

        gml_files = sorted(
            downloads_dir.rglob("*.gml")
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as output:

            output.write(
                f"Se encontraron {len(gml_files)} GML\n\n"
            )

            for gml_file in gml_files:

                output.write("\n")
                output.write("=" * 100 + "\n")
                output.write(f"FICHERO: {gml_file.name}\n")
                output.write(f"RUTA: {gml_file}\n")
                output.write("=" * 100 + "\n\n")

                try:

                    result = run(
                        [
                            "ogrinfo",
                            "-so",
                            str(gml_file)
                        ],
                        capture_output=True,
                        text=True,
                    )

                    output.write(result.stdout)

                    if result.stderr:
                        output.write("\nSTDERR:\n")
                        output.write(result.stderr)

                except Exception as exc:

                    output.write(
                        f"\nERROR: {exc}\n"
                    )

                output.write("\n\n")

        self.stdout.write(
            self.style.SUCCESS(
                f"Informe generado: {output_file}"
            )
        )