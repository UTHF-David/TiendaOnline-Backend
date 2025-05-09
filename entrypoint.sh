#!/usr/bin/env bash
# entrypoint.sh (versión mejorada para producción)

# 1. Crear directorios necesarios
mkdir -p media/productos
mkdir -p static

# 2. Copiar archivos estáticos y media (si existen backups)
[ -d "backup_media" ] && cp -r backup_media/* media/

# 3. Colectar archivos estáticos (para producción)
python manage.py collectstatic --noinput

# 4. Opción A: Usar Waitress (recomendado para producción)
waitress-serve --port=$PORT TiendaOnlineBack.wsgi:application

# O bien Opción B: Usar runserver (solo para desarrollo/testing)
# python manage.py runserver 0.0.0.0:$PORT --nothreading --noreload