#!/usr/bin/env bash

# Crea directorios necesarios
mkdir -p media/productos

# Si tienes imágenes por defecto, cópialas desde un directorio de respaldo
if [ -d "backup_media" ]; then
    cp -r backup_media/* media/
fi

# Migraciones y inicio del servidor
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:$PORT