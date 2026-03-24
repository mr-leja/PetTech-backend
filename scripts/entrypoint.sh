#!/bin/sh
set -e

echo "Esperando a que PostgreSQL este listo..."
until python manage.py migrate --noinput 2>&1; do
  echo "Base de datos no disponible, reintentando en 3 segundos..."
  sleep 3
done

echo "Migraciones aplicadas. Iniciando servidor Django..."
exec python manage.py runserver 0.0.0.0:8000
