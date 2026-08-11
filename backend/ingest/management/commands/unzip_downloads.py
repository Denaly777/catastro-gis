from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Inspecciona los GML y genera un informe en TXT"

    def handle(self, *args, **options):

        downloads_dir = Path("/app/backend/downloads")

        output_file = downloads_dir / "gml_inspection.txt"

        gml_files = sorted(
            downloads_dir.rglob("*.gml")
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as output:

            output.write(
                f"Se encontraron {len(gml_files)} archivos GML\n\n"
            )

            for gml_file in gml_files:

                output.write("\n")
                output.write("=" * 80 + "\n")
                output.write(f"Fichero: {gml_file.name}\n")
                output.write(f"Ruta: {gml_file}\n")
                output.write("=" * 80 + "\n")

                try:

                    with open(
                        gml_file,
                        "r",
                        encoding="utf-8",
                        errors="ignore"
                    ) as fichero:

                        for _ in range(50):

                            linea = fichero.readline()

                            if not linea:
                                break

                            output.write(linea)

                        output.write("\n\n")

                except Exception as exc:

                    output.write(
                        f"ERROR: {exc}\n\n"
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Informe generado: {output_file}"
            )
        )