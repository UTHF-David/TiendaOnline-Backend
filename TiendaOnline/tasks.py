from django.utils import timezone
from .models import CarritoTemp
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

def verificar_carritos_expirados():
    """
    Tarea programada para verificar y actualizar los carritos expirados.
    Esta función debe ser llamada periódicamente por un cron job o scheduler.
    """
    try:
        # Obtener todos los carritos no expirados que necesitan verificación
        carritos = CarritoTemp.objects.filter(
            Q(expirado=False) 
        ).select_related('producto')  # Optimizar consultas relacionadas
        
        if not carritos.exists():
            return
        
        logger.info(f"Verificando {carritos.count()} carritos para expiración")
        
        for carrito in carritos:
            try:
                if carrito.expiracion():
                    logger.info(f"Carrito {carrito.id} expirado correctamente")
            except Exception as e:
                logger.error(f"Error al verificar expiración del carrito {carrito.id}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error en verificar_carritos_expirados: {e}")
        raise 