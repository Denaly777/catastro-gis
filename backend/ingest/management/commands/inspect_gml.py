from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Genera inventario de GML"

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
                f"Se encontraron {len(gml_files)} GML\n\n"
            )

            for gml_file in gml_files:

                output.write(
                    f"{gml_file}\n"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Informe generado: {output_file}"
            )
        )