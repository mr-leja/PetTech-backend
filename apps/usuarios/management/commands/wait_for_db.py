import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = 'Espera a que la base de datos este disponible'

    def handle(self, *args, **options):
        self.stdout.write('Esperando base de datos...')
        for attempt in range(60):
            try:
                conn = connections['default']
                conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS('Base de datos lista!'))
                return
            except OperationalError:
                self.stdout.write(f'Intento {attempt + 1}/60: DB no disponible, esperando 2s...')
                time.sleep(2)
        raise SystemExit('No se pudo conectar a la base de datos despues de 60 intentos.')
