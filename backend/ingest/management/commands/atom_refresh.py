from django.core.management.base import BaseCommand

from ingest.services.atom import AtomService


class Command(BaseCommand):
    help = "Actualiza el árbol ATOM y muestra un resumen de entradas."

    def handle(self, *args, **options):
        service = AtomService()
        entries = service.list_root()
        self.stdout.write(self.style.SUCCESS(f"Raíz ATOM cargada: {len(entries)} entradas."))
