from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from ingest.services.atom import AtomService
from ingest.services.downloader import DownloaderService


class Command(BaseCommand):
    help = "Descarga uno o varios ZIP reales del municipio desde su enlace ATOM."

    def add_arguments(self, parser):
        parser.add_argument("region_query", help="Código o nombre de provincia, por ejemplo 05 o Ávila")
        parser.add_argument("municipality_query", help="Código o nombre de municipio, por ejemplo 05127 o Mijares")
        parser.add_argument(
            "--dataset",
            default="all",
            choices=("cp", "ad", "bu", "all"),
            help="Dataset ATOM a descargar: cp, ad, bu o all",
        )

    def handle(self, *args, **options):
        region_query = options["region_query"]
        municipality_query = options["municipality_query"]
        dataset = options["dataset"]
        if not region_query or not municipality_query:
            raise CommandError("Debes indicar una provincia y un municipio.")

        service = AtomService()
        if dataset == "all":
            entries = service.find_all_downloads(region_query, municipality_query)
        else:
            entries = [(dataset, service.find_municipality_entry(region_query, municipality_query, dataset))]

        if not entries:
            self.stdout.write(self.style.WARNING(f"No se encontraron descargas para el municipio {municipality_query}."))
            return

        downloads_dir = Path.cwd() / "downloads"
        downloader = DownloaderService()
        for item_dataset, municipality_entry in entries:
            output_name = service.build_download_filename(municipality_entry, item_dataset)
            output_path = downloads_dir / output_name
            saved_file = downloader.download(municipality_entry.href, output_path)
            self.stdout.write(self.style.SUCCESS(f"{item_dataset.upper()} descargado en: {saved_file}"))
