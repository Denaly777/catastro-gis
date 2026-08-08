# from django.core.management.base import BaseCommand

# from ingest.services.atom import AtomService


# class Command(BaseCommand):
#     help = "Lista la raíz del ATOM catastral."

#     def handle(self, *args, **kwargs):
#         service = AtomService()
#         entries = service.list_root()

#         if not entries:
#             self.stdout.write(self.style.WARNING("Sin entradas ATOM."))
#             return

#         for entry in entries:
#             self.stdout.write(f"{entry.title}\t{entry.href}")

from django.core.management.base import BaseCommand

from ingest.services.atom import AtomService


class Command(BaseCommand):
    help = "Lista la raíz del ATOM catastral."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dataset",
            choices=["cp", "ad", "bu", "all"],
            default="cp",
            help="Dataset ATOM a consultar.",
        )

    def handle(self, *args, **options):
        service = AtomService()

        dataset = options["dataset"]

        datasets = (
            ["cp", "ad", "bu"]
            if dataset == "all"
            else [dataset]
        )

        for ds in datasets:
            self.stdout.write(
                self.style.SUCCESS(f"\n=== DATASET {ds.upper()} ===")
            )

            entries = service.list_root(ds)

            if not entries:
                self.stdout.write(
                    self.style.WARNING("Sin entradas ATOM.")
                )
                continue

            for entry in entries:
                self.stdout.write(
                    f"{entry.title}\t{entry.href}"
                )