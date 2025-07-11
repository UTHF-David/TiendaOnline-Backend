# Importaciones estándar de Python
import base64
from decimal import Decimal, InvalidOperation
import logging
from django.db import connection
import pusher

# Importaciones de Django
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

# Importaciones de Django REST Framework
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

# Importaciones locales
from .serializer import ProductoSerializer, PedidoSerializer, PedidoDetalleSerializer, UsuarioSerializer, CarritoTempSerializer
from .models import Producto, Pedido, PedidoDetalle, Usuario, CarritoTemp
from TiendaOnlineBack import settings



# Configuración del logger para registrar eventos
logger = logging.getLogger(__name__)

# Configuración del cliente Pusher para notificaciones en tiempo real
pusher_client = pusher.Pusher(
    app_id=settings.PUSHER_APP_ID,
    key=settings.PUSHER_KEY,
    secret=settings.PUSHER_SECRET,
    cluster=settings.PUSHER_CLUSTER,
    ssl=True
)

@api_view(['POST'])
def actualizar_stock(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)
        cantidad = int(request.data.get('cantidad', 0))
        
        # Actualizar stock
        producto.cantidad_en_stock += cantidad
        producto.save()
        
        # Calcular stock disponible usando la misma lógica que stockvisible
        with connection.cursor() as cursor:
            cursor.callproc('sp_stock_producto', [producto_id])
            stockproducto = cursor.fetchone()

        with connection.cursor() as cursor:        
            cursor.callproc('sp_productotemp_total', [producto_id, 0])
            cursor.execute('SELECT @_sp_productotemp_total_1')
            temptotal = cursor.fetchone()
            stock_disponible = int(stockproducto[0]) - int(temptotal[0])
        
        # Notificar a todos los clientes en tiempo real
        pusher_client.trigger(
            f'producto-{producto_id}',  # Canal específico para este producto
            'stock-updated',            # Evento
            {
                'producto_id': producto_id,
                'stock_actual': stock_disponible,
                'stock_total': int(stockproducto[0]),
                'stock_temporal': int(temptotal[0]),
                'operacion': 'añadir' if cantidad > 0 else 'restar',
                'cantidad_cambiada': abs(cantidad),
                'timestamp': timezone.now().isoformat()
            }
        )
        
        return Response({
            'status': 'success',
            'producto_id': producto_id,
            'stock_disponible': stock_disponible,
            'stock_total': int(stockproducto[0]),
            'stock_temporal': int(temptotal[0]),
            'operacion': 'añadir' if cantidad > 0 else 'restar',
            'cantidad_cambiada': abs(cantidad)
        })
        
    except Producto.DoesNotExist:
        return Response({'error': 'Producto no encontrado'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProductoViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestionar productos con:
    - CRUD de productos
    - Manejo de imágenes en Base64
    - Actualización de stock
    - Parser para formularios multipart
    
    Endpoints:
    - GET /productos/: Listar productos
    - POST /productos/: Crear producto
    - GET /productos/{id}/: Obtener producto específico
    - PUT /productos/{id}/: Actualizar producto
    - DELETE /productos/{id}/: Eliminar producto
    - PUT /productos/{id}/actualizar_cantidad_en_stock/: Actualizar stock
    """
    
    # Configuración inicial
    parser_classes = [MultiPartParser, FormParser]
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo producto con manejo de imagen en Base64
        """
        try:
            data = request.data.copy()
            
            # Procesar imagen si viene en el request
            if 'imagen' in request.FILES:
                imagen_file = request.FILES['imagen']
                imagen_data = imagen_file.read()
                data['image'] = base64.b64encode(imagen_data).decode('utf-8')
            
            # Validar y guardar el producto
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
        """
        Actualiza un producto existente con manejo de imagen
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        data = request.data.copy()
        
        # Procesar imagen si viene en el request
        if 'imagen' in request.FILES:
            imagen_file = request.FILES['imagen']
            imagen_data = imagen_file.read()
            data['image'] = base64.b64encode(imagen_data).decode('utf-8')
        
        # Validar y guardar cambios
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)

    @action(detail=True, methods=['put'], url_path='actualizar_cantidad_en_stock')
    @permission_classes([AllowAny])
    @csrf_exempt
    def update_stock(self, request, pk=None):
        """
        Actualiza el stock de un producto (resta cantidad)
        """
        try:
            producto = get_object_or_404(Producto, id=pk)
            cantidad = request.query_params.get('cantidad')
            
            # Validar cantidad
            if cantidad is None or not cantidad.isdigit():
                return Response({'error': 'Cantidad inválida.'}, status=status.HTTP_400_BAD_REQUEST)

            cantidad = int(cantidad)
            nuevo_stock = producto.cantidad_en_stock - cantidad            
            
            # Verificar stock suficiente
            if nuevo_stock < 1:
                return Response({'error': 'La cantidad excede el stock disponible.'}, status=status.HTTP_400_BAD_REQUEST)

            # Actualizar stock
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
        
    @action(detail=True, methods=['put'], url_path='agregar_en_stock')
    @permission_classes([AllowAny])
    @csrf_exempt
    def add_update_stock(self, request, pk=None):
        """
        Añade cantidad al stock de un producto (suma cantidad)
        """
        try:
            producto = get_object_or_404(Producto, id=pk)
            cantidad = request.query_params.get('cantidad')
            
            # Validar cantidad
            if cantidad is None or not str(cantidad).lstrip('-').isdigit():
                return Response({
                    'error': 'Cantidad inválida.',
                    'detalle': f'Se recibió: {cantidad}',
                    'sugerencia': 'Use ?cantidad=<numero> en la URL'
                }, status=status.HTTP_400_BAD_REQUEST)

            cantidad = int(cantidad)
            nuevo_stock = producto.cantidad_en_stock + cantidad

            # Verificar stock no negativo
            if nuevo_stock < 0:
                return Response({
                    'error': 'La cantidad excede el stock disponible.',
                    'stock_actual': producto.cantidad_en_stock,
                    'intento_de_restar': abs(cantidad) if cantidad < 0 else None
                }, status=status.HTTP_400_BAD_REQUEST)

            # Actualizar stock
            producto.cantidad_en_stock = nuevo_stock
            producto.save()

            return Response({
                'message': 'Stock actualizado correctamente.',
                'producto': {
                    'id': producto.id,
                    'nombre': producto.nombre,
                    'cantidad_en_stock': producto.cantidad_en_stock,
                    'cambio_realizado': cantidad
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error interno del servidor',
                'detalle': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios con:
    - Registro
    - Login
    - Perfil
    - CRUD completo
    
    Endpoints:
    - POST /usuarios/login/: Iniciar sesión
    - POST /usuarios/register/: Registrar nuevo usuario
    - PUT /usuarios/profile/: Actualizar perfil
    """
    
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    @api_view(['POST'])
    @permission_classes([AllowAny])
    def login(request):
        """
        Autentica un usuario y retorna token
        """
        user = get_object_or_404(Usuario, email=request.data['email'])

        if not user.check_password(request.data['password']):
            return Response({"error": "Contraseña Invalida"}, status=status.HTTP_400_BAD_REQUEST)

        token, created = Token.objects.get_or_create(user=user)  
        serializer = UsuarioSerializer(instance=user)  

        return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)
 
    @api_view(['POST'])
    @permission_classes([AllowAny])
    def register(request):
        """
        Registra un nuevo usuario con contraseña hasheada
        """
        try:
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
        """
        Actualiza el perfil del usuario autenticado
        """
        try:
            user = request.user
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
    """
    ViewSet para gestionar detalles de pedidos.
    
    Este ViewSet maneja las operaciones CRUD para detalles de pedidos,
    incluyendo la creación y actualización de detalles individuales.
    
    Endpoints:
        GET /detalles-pedido/ - Lista todos los detalles
        POST /detalles-pedido/ - Crea un nuevo detalle
        GET /detalles-pedido/{id}/ - Obtiene un detalle específico
        PUT /detalles-pedido/{id}/ - Actualiza un detalle
        DELETE /detalles-pedido/{id}/ - Elimina un detalle
    """
    queryset = PedidoDetalle.objects.all()
    serializer_class = PedidoDetalleSerializer

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo detalle de pedido.
        
        Args:
            request: Request con los datos del detalle
            
        Returns:
            Response: Detalle creado o error
        """
        try:
            # Crear una copia mutable de los datos de la request
            data = request.data.copy()
            
            # Verificar que el pedido existe
            pedido = get_object_or_404(Pedido, id_pedido=data.get('pedido'))
            
            # Verificar que el producto existe
            producto = get_object_or_404(Producto, id=data.get('producto'))
            
            # Validar que hay suficiente stock disponible
            cantidad = int(data.get('cantidad_prod', 1))
            if producto.cantidad_en_stock < cantidad:
                return Response({
                    'error': f'No hay suficiente stock disponible para {producto.nombre}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Crear el detalle del pedido con los valores monetarios proporcionados
            detalle = PedidoDetalle.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad_prod=cantidad,
                subtotal=Decimal(str(data.get('subtotal', '0.00'))),
                isv=Decimal(str(data.get('isv', '0.00'))),
                envio=Decimal(str(data.get('envio', '0.00'))),
                total=Decimal(str(data.get('total', '0.00')))
            )

            # Actualizar el stock del producto restando la cantidad comprada
            producto.cantidad_en_stock -= cantidad
            producto.save()

            # Serializar y devolver el detalle creado
            serializer = self.get_serializer(detalle)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Actualiza un detalle de pedido existente.
        
        Args:
            request: Request con los datos actualizados
            
        Returns:
            Response: Detalle actualizado o error
        """
        try:
            # Obtener la instancia actual del detalle
            instance = self.get_object()
            data = request.data.copy()
            
            # Si se está actualizando la cantidad, validar el stock disponible
            if 'cantidad_prod' in data:
                nueva_cantidad = int(data['cantidad_prod'])
                # Calcular la diferencia entre la nueva cantidad y la actual
                diferencia = nueva_cantidad - instance.cantidad_prod
                
                # Verificar si hay suficiente stock para la diferencia
                if instance.producto.cantidad_en_stock < diferencia:
                    return Response({
                        'error': f'No hay suficiente stock disponible para {instance.producto.nombre}'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Actualizar el stock del producto
                instance.producto.cantidad_en_stock -= diferencia
                instance.producto.save()
            
            # Actualizar el detalle con los nuevos datos
            serializer = self.get_serializer(instance, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response(serializer.data)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un detalle de pedido y devuelve el stock.
        
        Args:
            request: Request
            
        Returns:
            Response: Confirmación de eliminación
        """
        try:
            # Obtener la instancia del detalle a eliminar
            instance = self.get_object()
            
            # Devolver el stock al producto
            producto = instance.producto
            #producto.cantidad_en_stock += instance.cantidad_prod
            producto.save()
            
            # Eliminar el detalle
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class PedidoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar pedidos.
    
    Este ViewSet maneja las operaciones CRUD para pedidos,
    incluyendo la creación de pedidos con múltiples productos.
    
    Endpoints:
        GET /pedidos/ - Lista todos los pedidos
        POST /pedidos/ - Crea un nuevo pedido
        GET /pedidos/{id}/ - Obtiene un pedido específico
        PUT /pedidos/{id}/ - Actualiza un pedido
        DELETE /pedidos/{id}/ - Elimina un pedido
        GET /pedidos/{id}/detalles/ - Obtiene los detalles de un pedido
        PUT /pedidos/{id}/actualizar_estado/ - Actualiza el estado de un pedido
    """
    queryset = Pedido.objects.all().select_related('usuario').prefetch_related('detalles__producto')    
    serializer_class = PedidoSerializer

    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo pedido con múltiples productos.
        """
        try:
            # Crear una copia mutable de los datos de la request
            data = request.data.copy()
            
            # Validar que los datos son un diccionario
            if not isinstance(data, dict):
                return Response({
                    'error': 'Formato de datos inválido',
                    'detalles': 'Los datos deben ser enviados como un objeto JSON'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validar que se proporcionaron productos
            productos = data.get('productos', [])
            if not productos:
                return Response({
                    'error': 'Debe proporcionar al menos un producto',
                    'detalles': 'El campo productos es requerido y debe contener al menos un producto'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validar que productos es una lista
            if not isinstance(productos, list):
                return Response({
                    'error': 'Formato de productos inválido',
                    'detalles': 'El campo productos debe ser una lista de productos'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Validar que el usuario existe
            usuario_id = data.get('usuario_id')
            if not usuario_id:
                return Response({
                    'error': 'El ID del usuario es requerido',
                    'detalles': 'El campo usuario_id es requerido'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                usuario = Usuario.objects.get(id=usuario_id)
            except Usuario.DoesNotExist:
                return Response({
                    'error': 'Usuario no encontrado',
                    'detalles': f'No existe un usuario con el ID {usuario_id}'
                }, status=status.HTTP_404_NOT_FOUND)

            # Crear el pedido base
            pedido = Pedido.objects.create(
                usuario=usuario,
                company=data.get('compañia', ''),
                direccion=data.get('direccion', ''),
                pais=data.get('pais', ''),
                estado_pais=data.get('estado_pais', ''),
                ciudad=data.get('ciudad', ''),
                zip=data.get('zip', ''),
                correo=data.get('correo', ''),
                telefono=data.get('telefono', ''),
                estado_compra='Pagado',
                desc_adicional=data.get('desc_adicional', ''),
                es_movimiento_interno=False
            )

            detalles_creados = []
            errores = []

            # Procesar cada producto del pedido
            for producto_data in productos:
                try:
                    # Validar que producto_data es un diccionario
                    if not isinstance(producto_data, dict):
                        errores.append(f'Datos de producto inválidos: {producto_data}')
                        continue

                    # Obtener el ID del producto (puede venir como 'id' o 'producto_id')
                    producto_id = producto_data.get('producto_id') or producto_data.get('id')
                    if not producto_id:
                        errores.append('Cada producto debe tener un ID (producto_id o id)')
                        continue

                    # Validar cantidad
                    cantidad = producto_data.get('cantidad')
                    if not cantidad:
                        errores.append(f'El producto {producto_id} debe tener una cantidad')
                        continue

                    try:
                        cantidad = int(cantidad)
                    except (ValueError, TypeError):
                        errores.append(f'La cantidad del producto {producto_id} debe ser un número entero')
                        continue

                    # Obtener el producto
                    try:
                        producto = Producto.objects.get(id=producto_id)
                    except Producto.DoesNotExist:
                        errores.append(f'Producto con ID {producto_id} no encontrado')
                        continue

                    # Validar stock disponible
                    if producto.cantidad_en_stock < cantidad:
                        errores.append(f'No hay suficiente stock para {producto.nombre} (disponible: {producto.cantidad_en_stock})')
                        continue

                    # Validar y convertir valores monetarios
                    try:
                        subtotal = Decimal(str(producto_data.get('subtotal', '0.00')))
                        isv = Decimal(str(producto_data.get('isv', '0.00')))
                        envio = Decimal(str(producto_data.get('envio', '0.00')))
                        total = Decimal(str(producto_data.get('total', '0.00')))
                    except (ValueError, TypeError, InvalidOperation) as e:
                        errores.append(f'Error en los valores monetarios del producto {producto_id}: {str(e)}')
                        continue

                    # Crear el detalle del pedido
                    detalle = PedidoDetalle.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad_prod=cantidad,
                        subtotal=subtotal,
                        isv=isv,
                        envio=envio,
                        total=total
                    )

                    # Actualizar el stock - eliminar el producto vendido
                    producto.cantidad_en_stock -= cantidad
                    producto.save()

                    detalles_creados.append(detalle)

                except Exception as e:
                    # Usar el ID del producto si está disponible, o un mensaje genérico
                    producto_id = producto_data.get('producto_id') if isinstance(producto_data, dict) else 'desconocido'
                    mensaje_error = f'Error al procesar producto {producto_id}: {str(e)}'
                    errores.append(mensaje_error)

            # Si hubo errores, eliminar el pedido y sus detalles
            if errores:
                pedido.delete()
                return Response({
                    'error': 'Errores al procesar productos',
                    'detalles': errores
                }, status=status.HTTP_400_BAD_REQUEST)

            # Serializar y devolver el pedido con sus detalles
            serializer = self.get_serializer(pedido)
            response_data = serializer.data
            response_data['detalles'] = PedidoDetalleSerializer(detalles_creados, many=True).data

            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            # Asegurarse de que el pedido se elimine si hubo un error general
            if 'pedido' in locals():
                pedido.delete()
            return Response({
                'error': f'Error al crear el pedido: {str(e)}',
                'detalles': 'Ocurrió un error inesperado al procesar la solicitud'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def detalles(self, request, pk=None):
        """
        Obtiene los detalles de un pedido específico.
        
        Args:
            request: Request
            pk: ID del pedido
            
        Returns:
            Response: Lista de detalles del pedido
        """
        # Obtener el pedido y sus detalles
        pedido = self.get_object()
        detalles = pedido.detalles.all()
        # Serializar y devolver los detalles
        serializer = PedidoDetalleSerializer(detalles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def actualizar_estado(self, request, pk=None):
        """
        Actualiza el estado de un pedido.
        
        Args:
            request: Request con el nuevo estado
            pk: ID del pedido
            
        Returns:
            Response: Pedido actualizado
        """
        # Obtener el pedido y el nuevo estado
        pedido = self.get_object()
        nuevo_estado = request.data.get('estado_compra')
        
        # Validar que el estado sea válido
        if nuevo_estado not in dict(Pedido.ESTADO_CHOICES):
            return Response({
                'error': 'Estado inválido'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Actualizar el estado del pedido
        pedido.estado_compra = nuevo_estado
        pedido.save()
        
        # Serializar y devolver el pedido actualizado
        serializer = self.get_serializer(pedido)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un pedido y devuelve el stock de sus detalles.
        
        Args:
            request: Request
            
        Returns:
            Response: Confirmación de eliminación
        """
        try:
            # Obtener la instancia del pedido a eliminar
            instance = self.get_object()
            
            # Devolver el stock de todos los detalles del pedido
            for detalle in instance.detalles.all():
                producto = detalle.producto
                producto.cantidad_en_stock += detalle.cantidad_prod
                producto.save()
            
            # Eliminar el pedido
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class RegistrarMovimientoView(APIView):
    """
    Vista para registrar movimientos internos de stock.
    
    Esta vista maneja la creación de pedidos internos para
    registrar movimientos de stock entre ubicaciones.
    
    Endpoints:
        POST /movimientos/ - Registra un nuevo movimiento
    """
    def post(self, request):
        """
        Registra un nuevo movimiento interno de stock.
        
        Args:
            request: Request con los datos del movimiento
            
        Returns:
            Response: Detalles del movimiento registrado
        """
        try:
            data = request.data.copy()
            admin_user = Usuario.objects.get(id=4)
            
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
                direccion=admin_user.direccion or "Origen no especificado",
                pais=admin_user.pais or "N/A",
                estado_pais=admin_user.estado_pais or "N/A",
                ciudad=admin_user.ciudad or "N/A",
                zip=admin_user.zip or "00000",
                correo=admin_user.email,
                telefono=admin_user.telefono or "00000000",
                estado_compra='Recibido',
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


class CarritoTempViewSet(viewsets.ModelViewSet):
    """
    ViewSet definitivo para gestionar el carrito de compras con:
    - Manejo robusto de stock
    - Transacciones atómicas
    - Prevención de condiciones de carrera
    - Logging detallado
    """
    serializer_class = CarritoTempSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return CarritoTemp.objects.filter(usuario=self.request.user).select_related('producto')

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Crea o actualiza un ítem en el carrito con verificación de stock atómica.
        """
        try:
            producto_id = request.data.get('producto')
            cantidad = int(request.data.get('cantidad_prod', 1))
            
            # Bloqueo selectivo para evitar condiciones de carrera
            producto = Producto.objects.select_for_update().get(id=producto_id)
            
            carrito_existente = CarritoTemp.objects.filter(
                usuario=request.user,
                producto=producto
            ).first()

            if carrito_existente:
                nueva_cantidad = carrito_existente.cantidad_prod + cantidad
                if producto.cantidad_en_stock < nueva_cantidad:
                    return Response(
                        {'error': f'Stock insuficiente. Disponible: {producto.cantidad_en_stock}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                carrito_existente.cantidad_prod = nueva_cantidad
                carrito_existente.save()
                                    
                # Notificar cambio en tiempo real
                pusher_client.trigger(
                    f'producto-{producto_id}',
                    'carrito-updated',
                    {
                        'producto_id': producto_id,
                        'accion': 'actualizado',
                        'cantidad_carrito': nueva_cantidad,
                        'usuario_id': request.user.id
                    }
                )
                
                serializer = self.get_serializer(carrito_existente)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                if producto.cantidad_en_stock < cantidad:
                    return Response(
                        {'error': f'Stock insuficiente. Disponible: {producto.cantidad_en_stock}'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                data = request.data.copy()
                data['usuario'] = request.user.id
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                
                self.perform_create(serializer)
                
                # Notificar cambio en tiempo real
                pusher_client.trigger(
                    f'producto-{producto_id}',
                    'carrito-updated',
                    {
                        'producto_id': producto_id,
                        'accion': 'agregado',
                        'cantidad_carrito': cantidad,
                        'usuario_id': request.user.id
                    }
                )
                
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        except Producto.DoesNotExist:
            return Response(
                {'error': 'Producto no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Error en creación de carrito: {str(e)}', exc_info=True)
            return Response(
                {'error': 'Error interno al agregar al carrito'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un ítem del carrito de forma segura
        """
        try:
            # Bloquear registro para operación atómica
            instance = CarritoTemp.objects.select_for_update().get(
                pk=kwargs['pk'],
                usuario=request.user
            )
            producto_id = instance.producto_id
            cantidad = instance.cantidad_prod
            
            # Eliminar primero el ítem
            self.perform_destroy(instance)
            logger.info(f'Ítem {instance.id} eliminado del carrito')
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except CarritoTemp.DoesNotExist:
            return Response(
                {'error': 'El ítem del carrito no existe'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f'Error crítico al eliminar: {str(e)}', exc_info=True)
            return Response(
                {'error': 'Error interno al eliminar del carrito'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    @action(detail=False, methods=['delete'])
    def limpiar_carrito(self, request):
        """
        Limpia todo el carrito del usuario con manejo de stock
        """
        try:
            items = CarritoTemp.objects.select_for_update().filter(
                usuario=request.user
            ).select_related('producto')
            
            # Agrupar cantidades por producto
            stock_a_devolver = {}
            for item in items:
                if item.producto_id not in stock_a_devolver:
                    stock_a_devolver[item.producto_id] = 0
                stock_a_devolver[item.producto_id] += item.cantidad_prod
            
            # Eliminar todos los ítems
            count = items.count()
            items.delete()
            logger.info(f'Carrito limpiado. {count} ítems eliminados')
            
            # Actualizar stock para productos existentes
            for producto_id, cantidad in stock_a_devolver.items():
                try:
                    producto = Producto.objects.get(id=producto_id)
                    producto.cantidad_en_stock += cantidad
                    producto.save()
                    logger.info(f'Devueltas {cantidad} unidades al producto {producto_id}')
                except Producto.DoesNotExist:
                    logger.warning(f'Producto {producto_id} no existe, no se devolvió stock')
                    continue
            
            return Response({
                'message': f'Carrito limpiado correctamente. {count} ítems eliminados.',
                'items_eliminados': count
            })
            
        except Exception as e:
            logger.error(f'Error al limpiar carrito: {str(e)}', exc_info=True)
            return Response(
                {'error': 'Error interno al limpiar el carrito'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def verificar_expiracion(self, request):
        """
        Verifica productos expirados en el carrito
        """
        expirados = CarritoTemp.verificar_expiracion_carrito(request.user)
        
        if expirados:
            serializer = self.get_serializer(expirados, many=True)
            logger.info(f'Productos expirados encontrados: {len(expirados)}')
            return Response({
                'message': 'Se encontraron productos expirados',
                'productos_expirados': serializer.data
            })
        
        return Response({
            'message': 'No hay productos expirados'
        })
 