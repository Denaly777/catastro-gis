from pathlib import Path
from subprocess import run

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Obtiene ejemplos reales de registros GML"

    def handle(self, *args, **options):

        downloads_dir = Path("/app/backend/downloads")

        output_file = downloads_dir / "features_inspection.txt"

        gml_files = sorted(
            downloads_dir.rglob("*.gml")
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as output:

            for gml_file in gml_files:

                output.write("\n")
                output.write("=" * 100 + "\n")
                output.write(f"FICHERO: {gml_file.name}\n")
                output.write(f"RUTA: {gml_file}\n")
                output.write("=" * 100 + "\n")

                try:

                    layers_result = run(
                        [
                            "ogrinfo",
                            str(gml_file)
                        ],
                        capture_output=True,
                        text=True,
                    )

                    layers = []

                    for line in layers_result.stdout.splitlines():

                        line = line.strip()

                        if (
                            len(line) > 3
                            and line[0].isdigit()
                            and ":" in line
                        ):

                            layer_name = (
                                line.split(":", 1)[1]
                                .split("(")[0]
                                .strip()
                            )

                            layers.append(layer_name)

                    for layer in layers:

                        output.write("\n")
                        output.write(f"CAPA: {layer}\n")
                        output.write("-" * 80 + "\n")

                        feature_result = run(
                            [
                                "ogrinfo",
                                str(gml_file),
                                layer,
                                "-al"
                            ],
                            capture_output=True,
                            text=True,
                        )

                        lines = feature_result.stdout.splitlines()

                        for line in lines[:150]:

                            output.write(line + "\n")

                        output.write("\n")

                except Exception as exc:

                    output.write(
                        f"ERROR: {exc}\n"
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f"Informe generado: {output_file}"
            )
        )