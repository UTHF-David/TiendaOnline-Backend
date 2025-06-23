# =============================================================================
# MÓDULO DE CONEXIÓN Y PROCEDIMIENTOS ALMACENADOS
# =============================================================================
"""
Este módulo maneja las conexiones directas a la base de datos y procedimientos
almacenados. Se utiliza para operaciones complejas que requieren consultas SQL directas
o procedimientos almacenados específicos.

Funcionalidades:
- Consulta de stock en tiempo real
- Notificaciones push con Pusher
- Manejo de errores de base de datos
"""

from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from TiendaOnlineBack import settings
import pusher

# =============================================================================
# CONFIGURACIÓN DE PUSHER PARA NOTIFICACIONES EN TIEMPO REAL
# =============================================================================
# Cliente de Pusher configurado con las credenciales del proyecto
pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True
)

# =============================================================================
# ENDPOINT PARA CONSULTA DE STOCK VISIBLE
# =============================================================================
@api_view(['GET'])
def stockvisible(request, id=None):
    """
    Endpoint para consultar el stock visible de un producto.
    
    Este endpoint utiliza procedimientos almacenados para calcular el stock real
    disponible, considerando las reservas temporales en carritos.
    
    Args:
        request: Request HTTP de Django
        id: ID del producto a consultar
        
    Returns:
        Response: Stock disponible del producto
        
    Lógica:
        1. Ejecuta procedimiento almacenado para obtener stock total
        2. Ejecuta procedimiento para obtener cantidad temporal reservada
        3. Calcula stock visible = stock_total - cantidad_reservada
        4. Envía notificación push con el stock actualizado
        5. Retorna el stock visible
    """
    try:
        # Ejecutar procedimiento almacenado para obtener stock total del producto
        with connection.cursor() as cursor:
            cursor.callproc('sp_stock_producto', [id])
            stockproducto = cursor.fetchone()

        # Ejecutar procedimiento para obtener cantidad temporal reservada
        with connection.cursor() as cursor:        
            cursor.callproc('sp_productotemp_total', [id, 0])
            cursor.execute('SELECT @_sp_productotemp_total_1')
            temptotal = cursor.fetchone()
            
            # Calcular stock visible: stock total - cantidad reservada temporalmente
            results = int(stockproducto[0]) - int(temptotal[0])
            
            # Notificar a todos los clientes sobre el stock actualizado en tiempo real
            pusher_client.trigger(
                f'producto-{id}',      # Canal específico para este producto
                'stock-updated',       # Evento de actualización de stock
                {
                    'producto_id': id,
                    'stock_actual': results
                }
            )
            
            return Response(results, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Manejo de errores con respuesta detallada
        return Response({
            'error': 'Error al consultar el stock',
            'detalle': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    