from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Producto, Pedido
from .serializer import ProductoSerializer, PedidoSerializer

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, 
                status=status.HTTP_201_CREATED, 
                headers=headers
            )
        except Exception as e:
            error_data = {
                'error': str(e),
                'received_data': request.data,
                'validation_errors': serializer.errors
            }
            return Response(
                error_data,
                status=status.HTTP_400_BAD_REQUEST
            )

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer