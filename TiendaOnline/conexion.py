from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from TiendaOnline.models import Producto
from TiendaOnline.serializer import ProductoSerializer


@api_view(['GET'])
def stockvisible(request,id=None):
    try:
        with connection.cursor() as cursor:
            cursor.callproc('sp_stock_productos', [id])
            stockproducto = cursor.fetchone()

        with connection.cursor() as cursor:        
            cursor.callproc('sp_productotemp_total', [id,0])
            cursor.execute('SELECT @_sp_productotemp_total_1')
            temptotal = cursor.fetchone()
            # Convertimos a enteros y realizamos la operación
            results = int(stockproducto[0]) - int(temptotal[0])
                
            return Response(results, status=status.HTTP_200_OK)
            
    
    except Exception as e:
        return Response({
            'error': 'Error al consultar el stock',
            'detalle': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    