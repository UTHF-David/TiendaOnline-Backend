#!/usr/bin/env bash

# 1. Crea la estructura de directorios necesaria
mkdir -p media/productos

# 2. Aplica migraciones
python manage.py migrate

# 3. Opcional: Carga datos iniciales (si necesitas imágenes por defecto)
# python manage.py loaddata initial_images.json

# 4. Inicia el servidor
python manage.py runserver 0.0.0.0:$PORT