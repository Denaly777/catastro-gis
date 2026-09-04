from django.core.management.base import BaseCommand, CommandError

from ingest.services.atom import AtomService


class Command(BaseCommand):
    help = "Busca municipios por nombre o codigo en todas las provincias para un dataset ATOM."

    def add_arguments(self, parser):
        parser.add_argument("municipality_query", help="Nombre o codigo de municipio, por ejemplo Mijares o 05127")
        parser.add_argument(
            "--dataset",
            default="cp",
            choices=("cp", "ad", "bu"),
            help="Dataset ATOM a consultar",
        )
        parser.add_argument(
            "--limit",
            default=20,
            type=int,
            help="Numero maximo de coincidencias a devolver",
        )

    def handle(self, *args, **options):
        municipality_query = options["municipality_query"]
        dataset = options["dataset"]
        limit = options["limit"]

        if not municipality_query:
            raise CommandError("Debes indicar un nombre o codigo de municipio.")

        if limit <= 0:
            raise CommandError("El parametro --limit debe ser mayor que 0.")

        service = AtomService()
        matches = service.find_municipalities_across_regions(
            municipality_query=municipality_query,
            dataset=dataset,
            limit=limit,
        )

        if not matches:
            self.stdout.write(self.style.WARNING(f"No se encontraron municipios para '{municipality_query}'."))
            return

        self.stdout.write(self.style.SUCCESS(f"Coincidencias ({len(matches)}):"))
        for item in matches:
            region_display = item["region_code"] or "--"
            municipality_code = item["municipality_code"] or "-----"
            self.stdout.write(
                f"[{region_display}] {item['region_title']}\t"
                f"[{municipality_code}] {item['municipality_title']}\t"
                f"{item['municipality_href']}"
            )
