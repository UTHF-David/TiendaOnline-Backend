from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from TiendaOnlineBack import settings
import pusher


pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True
)


@api_view(['GET'])
def stockvisible(request, id=None):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_stock_producto', [id])
            stockproducto = cursor.fetchone()

        with connection.cursor() as cursor:        
            cursor.callproc('sp_productotemp_total', [id, 0])
            cursor.execute('SELECT @_sp_productotemp_total_1')
            temptotal = cursor.fetchone()
            results = int(stockproducto[0]) - int(temptotal[0])
            
            # Notificar a todos los clientes sobre el stock actual
            pusher_client.trigger(
                f'producto-{id}',  # Canal específico para este producto
                'stock-updated',    # Evento
                {
                    'producto_id': id,
                    'stock_actual': results
                }
            )
            
            return Response(results, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': 'Error al consultar el stock',
            'detalle': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    