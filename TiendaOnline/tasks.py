# =============================================================================
# MÓDULO DE TAREAS PROGRAMADAS
# =============================================================================
"""
Este módulo contiene las tareas que se ejecutan automáticamente por el scheduler.
Estas tareas se encargan del mantenimiento automático del sistema y operaciones
periódicas necesarias para el correcto funcionamiento de la tienda.

Funcionalidades:
- Verificación automática de carritos expirados
- Limpieza de datos temporales
- Mantenimiento de integridad de datos
- Logging de operaciones automáticas
"""

from django.utils import timezone
from .models import CarritoTemp
from django.db.models import Q
import logging

# Configuración del logger para este módulo
logger = logging.getLogger(__name__)

def verificar_carritos_expirados():
    """
    Tarea programada para verificar y actualizar los carritos expirados.
    
    Esta función debe ser llamada periódicamente por el scheduler (cada 3 minutos)
    para mantener la integridad del sistema de carritos temporales.
    
    Funcionalidades:
    - Obtiene todos los carritos no expirados que necesitan verificación
    - Verifica la expiración de cada carrito individualmente
    - Maneja errores de forma individual para no interrumpir el proceso
    - Registra logs de las operaciones realizadas
    
    Lógica:
    1. Filtra carritos no expirados que necesitan verificación
    2. Para cada carrito, verifica si ha expirado por tiempo de inactividad
    3. Si expira, libera el stock reservado y marca como expirado
    4. Registra logs de éxito o error para cada operación
    
    Notas:
    - Se ejecuta en segundo plano sin afectar el rendimiento del sistema
    - Maneja errores de forma individual para evitar interrupciones
    - Optimiza consultas usando select_related para reducir hits a la BD
    """
    try:
        # Obtener todos los carritos no expirados que necesitan verificación
        carritos = CarritoTemp.objects.filter(
            Q(expirado=False)  # Solo carritos no expirados
        ).select_related('producto')  # Optimizar consultas relacionadas
        
        # Si no hay carritos para verificar, terminar la tarea
        if not carritos.exists():
            return
        
        # Registrar inicio de la verificación
        logger.info(f"Verificando {carritos.count()} carritos para expiración")
        
        # Procesar cada carrito individualmente
        for carrito in carritos:
            try:
                # Verificar si el carrito ha expirado
                if carrito.expiracion():
                    logger.info(f"Carrito {carrito.id} expirado correctamente")
            except Exception as e:
                # Manejar errores individuales sin interrumpir el proceso
                logger.error(f"Error al verificar expiración del carrito {carrito.id}: {e}")
                continue
                
    except Exception as e:
        # Manejar errores generales de la tarea
        logger.error(f"Error en verificar_carritos_expirados: {e}")
        raise 