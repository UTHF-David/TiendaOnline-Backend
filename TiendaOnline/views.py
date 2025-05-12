from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Producto, Pedido
from .serializer import ProductoSerializer, PedidoSerializer
import base64
from rest_framework.parsers import MultiPartParser, FormParser

class ProductoViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Obtener el archivo de imagen
            imagen_file = request.FILES.get('imagen')
            
            # Convertir a base64 si existe la imagen
            imagen_base64 = None
            if imagen_file:
                imagen_data = imagen_file.read()
                imagen_base64 = base64.b64encode(imagen_data).decode('utf-8')
            
            # Crear copia mutable de los datos
            data = request.data.copy()
            data['imagen_base64'] = imagen_base64
            
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            return Response(
                {"error": str(e), "received_data": request.data, "files": list(request.FILES.keys())},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Manejar la imagen en Base64
        imagen_file = request.FILES.get('imagen')
        if imagen_file:
            imagen_data = imagen_file.read()
            request.data['imagen_base64'] = base64.b64encode(imagen_data).decode('utf-8')
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
        

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer