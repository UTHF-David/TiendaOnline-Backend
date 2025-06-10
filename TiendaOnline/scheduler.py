from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.events import EVENT_JOB_ERROR
from django.conf import settings
from .tasks import verificar_carritos_expirados
import logging

logger = logging.getLogger(__name__)

def start_scheduler():
    """
    Inicia el scheduler para ejecutar tareas programadas.
    """
    try:
        scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)
        
        # Programar la verificación de carritos expirados cada minuto
        scheduler.add_job(
            verificar_carritos_expirados,
            trigger=IntervalTrigger(minutes=1),
            id='verificar_carritos_expirados',
            name='Verificar carritos expirados cada minuto',
            replace_existing=True,
            max_instances=1  # Evitar múltiples instancias de la misma tarea
        )
        
        # Configurar el manejo de errores
        scheduler.add_listener(
            lambda event: logger.error(f"Error en el scheduler: {event.exception}"),
            mask=EVENT_JOB_ERROR
        )
        
        scheduler.start()
        logger.info("Scheduler iniciado correctamente")
        
    except Exception as e:
        logger.error(f"Error al iniciar el scheduler: {e}")
        raise 