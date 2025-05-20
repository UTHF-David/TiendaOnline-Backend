from rest_framework.parsers import MultiPartParser, FormParser
from .serializer import ProductoSerializer, PedidoSerializer, PedidoDetalleSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status

from .models import Producto, Pedido, PedidoDetalle

import base64

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

    @action(detail=True, methods=['put'], url_path='cantidad_en_stock/(?P<cantidad>[0-9]+)')
    def update_stock(self, request, pk=None, cantidad=None):
        try:
            producto = get_object_or_404(Producto, id=pk)

            # Validar que la cantidad sea un número válido
            if cantidad is None or not cantidad.isdigit():
                return Response({'error': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

            cantidad = int(cantidad)
            nuevo_stock = producto.cantidad_en_stock - cantidad

            # Validar que el stock no sea negativo
            if nuevo_stock < 0:
                return Response({'error': 'La cantidad excede el stock disponible.'}, status=status.HTTP_400_BAD_REQUEST)

            # Actualizar el stock
            producto.cantidad_en_stock = nuevo_stock
            producto.save()

            return Response({
                'message': 'Stock actualizado correctamente.',
                'producto': {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'cantidad_en_stock': producto.cantidad_en_stock,
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=True, methods=['put'], url_path='cantidad_en_stock/(?P<cantidad>[0-9-]+)')
    def add_update_stock(self, request, pk=None, cantidad=None):
        try:
            producto = get_object_or_404(Producto, id=pk)

            # Validar que la cantidad sea un número válido
            if cantidad is None or not cantidad.lstrip('-').isdigit():
                return Response({'error': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

            cantidad = int(cantidad)
            nuevo_stock = producto.cantidad_en_stock + cantidad

            # Validar que el stock no sea negativo
            if nuevo_stock < 0:
                return Response({'error': 'La cantidad excede el stock disponible.'}, status=status.HTTP_400_BAD_REQUEST)

            # Actualizar el stock
            producto.cantidad_en_stock = nuevo_stock
            producto.save()

            return Response({
                'message': 'Stock actualizado correctamente.',
                'producto': {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'cantidad_en_stock': producto.cantidad_en_stock,
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Obtener los datos del request
            data = request.data
            productos_data = data.pop('productos', [])  # Lista de productos a comprar
            
            # Crear el pedido base
            pedido = Pedido.objects.create(
                usuario_id=data.get('usuario'),
                company=data.get('company'),
                direccion=data.get('direccion'),
                pais_id=data.get('pais'),
                estado_pais=data.get('estado_pais'),
                ciudad=data.get('ciudad'),
                zip=data.get('zip'),
                correo=data.get('correo'),
                telefono=data.get('telefono'),
                estado_compra='Pagado',
                desc_adicional=data.get('desc_adicional')
            )

            # Procesar cada producto en el pedido
            for producto_data in productos_data:
                producto = get_object_or_404(Producto, id=producto_data['id'])
                cantidad = producto_data['cantidad']

                # Validar stock disponible
                if producto.cantidad_en_stock < cantidad:
                    pedido.delete()  # Eliminar el pedido si no hay stock
                    return Response({
                        'error': f'No hay suficiente stock disponible para {producto.nombre}'
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Crear el detalle del pedido
                PedidoDetalle.objects.create(
                    pedido=pedido,
                    producto=producto,
                    cantidad_prod=cantidad
                )

                # Actualizar stock del producto
                producto.cantidad_en_stock -= cantidad
                producto.save()

            # Serializar y retornar respuesta
            serializer = self.get_serializer(pedido)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        """Obtener los detalles de un pedido específico"""
        pedido = self.get_object()
        detalles = pedido.detalles.all()
        serializer = PedidoDetalleSerializer(detalles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def actualizar_estado(self, request, pk=None):
        """Actualizar el estado de un pedido"""
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado_compra')
        
        if nuevo_estado not in dict(Pedido.ESTADO_CHOICES):
            return Response({
                'error': 'Estado inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        pedido.estado_compra = nuevo_estado
        pedido.save()
        
        serializer = self.get_serializer(pedido)
        return Response(serializer.data)

    

