from rest_framework.parsers import MultiPartParser, FormParser
from .serializer import ProductoSerializer, PedidoSerializer, PedidoDetalleSerializer, UsuarioSerializer
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework import viewsets, status 
from rest_framework.permissions import AllowAny
from .models import Producto, Pedido, PedidoDetalle
from TiendaOnline.models import Usuario
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import base64
from decimal import Decimal


class ProductoViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser]
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Crear copia mutable de los datos
            data = request.data.copy()
            
            if 'imagen' in request.FILES:
                imagen_file = request.FILES['imagen']
                imagen_data = imagen_file.read()
                data['image'] = base64.b64encode(imagen_data).decode('utf-8')
            
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
        
        # Crear copia mutable de los datos
        data = request.data.copy()
        
        if 'imagen' in request.FILES:
            imagen_file = request.FILES['imagen']
            imagen_data = imagen_file.read()
            data['image'] = base64.b64encode(imagen_data).decode('utf-8')
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='cantidad_en_stock/(?P<cantidad>[0-9]+)')
    def update_stock(self, request, pk=None, cantidad=None):
        try:
            producto = get_object_or_404(Producto, id=pk)

            if cantidad is None or not cantidad.isdigit():
                return Response({'error': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

            cantidad = int(cantidad)
            nuevo_stock = producto.cantidad_en_stock - cantidad

            if nuevo_stock < 0:
                return Response({'error': 'La cantidad excede el stock disponible.'}, status=status.HTTP_400_BAD_REQUEST)

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

            if cantidad is None or not cantidad.lstrip('-').isdigit():
                return Response({'error': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

            cantidad = int(cantidad)
            nuevo_stock = producto.cantidad_en_stock + cantidad

            if nuevo_stock < 0:
                return Response({'error': 'La cantidad excede el stock disponible.'}, status=status.HTTP_400_BAD_REQUEST)

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

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def login(request):
        user = get_object_or_404(Usuario, email=request.data['email'])

        if not user.check_password(request.data['password']):
            return Response({"error": "Contraseña Invalida"}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user)  
        serializer = UsuarioSerializer(instance=user)  

        return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)
 
    @api_view(['POST'])
    @permission_classes([AllowAny])
    def register(request):
        try:
            # Crear copia mutable de los datos
            data = request.data.copy()
            
            serializer = UsuarioSerializer(data=data)
            if serializer.is_valid():
                user = serializer.save()
                user.set_password(data.get('password'))
                user.save()
                
                token = Token.objects.create(user=user)
                return Response({
                    'token': token.key,
                    'user': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
    @api_view(['PUT'])
    @authentication_classes([TokenAuthentication]) 
    @permission_classes([IsAuthenticated])
    def profile(request):
        try:
            user = request.user
            # Crear copia mutable de los datos
            data = request.data.copy()
            
            serializer = UsuarioSerializer(user, data=data, partial=True)
            
            if serializer.is_valid():
                if 'password' in data:
                    user.set_password(data['password'])
                
                serializer.save()
                return Response({
                    'message': 'Perfil actualizado exitosamente',
                    'user': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PedidoDetalleViewSet(viewsets.ModelViewSet):
    queryset = PedidoDetalle.objects.all()
    serializer_class = PedidoDetalleSerializer

class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Crear copia mutable de los datos
            data = request.data.copy()
            
            # Crear el pedido
            pedido = Pedido.objects.create(
                usuario_id=data.get('usuario_id'),
                company=data.get('compañia'),
                direccion=data.get('direccion'),
                pais=data.get('pais'),
                estado_pais=data.get('estado_pais'),
                ciudad=data.get('ciudad'),
                zip=data.get('zip'),
                correo=data.get('correo'),
                telefono=data.get('telefono'),
                estado_compra='Pagado',
                desc_adicional=data.get('desc_adicional'),
                es_movimiento_interno=False
            )

            # Crear el detalle del pedido
            producto = get_object_or_404(Producto, id=data.get('producto'))
            cantidad = int(data.get('cantidad_prod', 1))

            if producto.cantidad_en_stock < cantidad:
                pedido.delete()
                return Response({
                    'error': f'No hay suficiente stock disponible para {producto.nombre}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Crear el detalle del pedido con los valores proporcionados
            detalle = PedidoDetalle.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad_prod=cantidad,
                subtotal=Decimal(data.get('subtotal', 0)),
                isv=Decimal(data.get('isv', 0)),
                envio=Decimal(data.get('envio', 0)),
                total=Decimal(data.get('total', 0))
            )

            # Actualizar el stock del producto
            producto.cantidad_en_stock -= cantidad
            producto.save()

            # Preparar la respuesta
            serializer = self.get_serializer(pedido)
            response_data = serializer.data
            response_data['detalle'] = {
                'producto': producto.nombre,
                'cantidad': cantidad,
                'subtotal': float(detalle.subtotal),
                'isv': float(detalle.isv),
                'envio': float(detalle.envio),
                'total': float(detalle.total)
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        pedido = self.get_object()
        detalles = pedido.detalles.all()
        serializer = PedidoDetalleSerializer(detalles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def actualizar_estado(self, request, pk=None):
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

class RegistrarMovimientoView(APIView):
    def post(self, request):
        try:
            # Crear copia mutable de los datos
            data = request.data.copy()
            admin_user = Usuario.objects.get(id=1)
            
            required_fields = ['producto_id', 'cantidad', 'tipo_salida', 'compania_destino']
            if not all(field in data for field in required_fields):
                return Response({'error': 'Faltan campos requeridos'}, status=status.HTTP_400_BAD_REQUEST)
            
            producto = Producto.objects.get(id=data['producto_id'])
            
            if producto.cantidad_en_stock < data['cantidad']:
                return Response(
                    {'error': f'Stock insuficiente. Disponible: {producto.cantidad_en_stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            pedido = Pedido.objects.create(
                usuario=admin_user,
                company=data['compania_destino'],
                direccion=admin_user.direccion,
                pais=admin_user.pais,
                estado_pais=admin_user.estado_pais,
                ciudad=admin_user.ciudad,
                zip=admin_user.zip,
                correo=admin_user.email,
                telefono=admin_user.telefono,
                estado_compra='Entregado',
                desc_adicional=f"{data['tipo_salida']} - {data.get('descripcion', '')}",
                fecha_entrega=timezone.now(),
                es_movimiento_interno=True
            )
            
            PedidoDetalle.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad_prod=data['cantidad'],
                subtotal=0.00,
                isv=0.00,
                envio=0.00,
                total=0.00
            )
            
            producto.cantidad_en_stock -= data['cantidad']
            producto.save()
            
            return Response({
                'success': True,
                'pedido_id': pedido.id_pedido,
                'stock_actual': producto.cantidad_en_stock,
                'subtotal': 0.00,
                'isv': 0.00,
                'envio': 0.00,
                'total': 0.00
            }, status=status.HTTP_201_CREATED)
            
        except Producto.DoesNotExist:
            return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)