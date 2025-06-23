# =============================================================================
# MÓDULO DE PROGRAMACIÓN DE TAREAS AUTOMÁTICAS
# =============================================================================
"""
Este módulo maneja la programación de tareas automáticas usando APScheduler.
Se encarga de ejecutar tareas periódicas como la verificación de carritos expirados
y otras operaciones de mantenimiento del sistema.

Funcionalidades:
- Programación de tareas en segundo plano
- Verificación automática de carritos expirados
- Manejo de errores en tareas programadas
- Logging de eventos del scheduler
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR
from django.conf import settings
from .tasks import verificar_carritos_expirados
import logging

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

def start_scheduler():
    """
    Inicia el scheduler para ejecutar tareas programadas.
    
    Esta función configura y inicia el programador de tareas APScheduler
    con las tareas necesarias para el mantenimiento automático del sistema.
    
    Tareas configuradas:
    - Verificación de carritos expirados cada 3 minutos
    
    Configuración:
    - Usa BackgroundScheduler para ejecutar en segundo plano
    - Almacena jobs en la base de datos Django
    - Usa threadpool para ejecutar tareas
    - Maneja errores con logging
    
    Raises:
        Exception: Si hay error al iniciar el scheduler
    """
    try:
        # Crear instancia del scheduler con configuración del proyecto
        scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
        
        # Programar la verificación de carritos expirados cada 3 minutos
        scheduler.add_job(
            func=verificar_carritos_expirados,           # Función a ejecutar
            trigger=IntervalTrigger(minutes=3),         # Ejecutar cada 3 minutos
            id='verificar_carritos_expirados',          # ID único del job
            name='Verificar carritos expirados cada 3 minutos',  # Nombre descriptivo
            replace_existing=True,                      # Reemplazar si ya existe
            max_instances=1                             # Máximo 1 instancia ejecutándose
        )
        
        # Configurar el manejo de errores para todas las tareas
        scheduler.add_listener(
            lambda event: logger.error(f"Error en el scheduler: {event.exception}"),
            mask=EVENT_JOB_ERROR
        )
        
        # Iniciar el scheduler
        scheduler.start()
        logger.info("Scheduler iniciado correctamente")
        
    except Exception as e:
        logger.error(f"Error al iniciar el scheduler: {e}")
        raise 