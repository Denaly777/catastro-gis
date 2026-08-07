from django.core.management.base import BaseCommand

from ingest.services.atom import AtomService


class Command(BaseCommand):
    help = "Lista la raíz del ATOM catastral."

    def handle(self, *args, **kwargs):
        service = AtomService()
        entries = service.list_root()

        if not entries:
            self.stdout.write(self.style.WARNING("Sin entradas ATOM."))
            return

        for entry in entries:
            self.stdout.write(f"{entry.title}\t{entry.href}")