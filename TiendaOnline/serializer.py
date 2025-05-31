from rest_framework import serializers
from .models import Producto, Pedido, PedidoDetalle, Usuario
from django.contrib.auth.models import User
from decimal import Decimal # Importar Decimal si se usa en algún serializer (aunque en PedidoDetalle.save es donde se usa principalmente)


#Con este serializer se puede crear un usuario con un pais
class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Usuario.
    
    Este serializer maneja la serialización y deserialización de usuarios,
    incluyendo el manejo seguro de contraseñas.
    
    Campos:
        Todos los campos del modelo Usuario
        password: Campo de solo escritura para manejar contraseñas de forma segura
    """
    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Crea un nuevo usuario con contraseña encriptada.
        
        Args:
            validated_data (dict): Datos validados del usuario
            
        Returns:
            Usuario: Instancia del usuario creado
        """
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        """
        Actualiza un usuario existente, manejando la contraseña de forma segura.
        
        Args:
            instance (Usuario): Instancia del usuario a actualizar
            validated_data (dict): Datos validados para la actualización
            
        Returns:
            Usuario: Instancia del usuario actualizado
        """
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class ProductoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Producto.
    
    Este serializer maneja la serialización de productos, incluyendo
    la validación de imágenes en formato Base64.
    
    Campos:
        Todos los campos del modelo Producto
        imagen_base64: Campo opcional para manejar imágenes en Base64
    """
    class Meta:
        model = Producto
        fields = '__all__'
        extra_kwargs = {
            'imagen_base64': {'required': False}
        }

    def create(self, validated_data):
        """
        Crea un nuevo producto.
        
        Args:
            validated_data (dict): Datos validados del producto
            
        Returns:
            Producto: Instancia del producto creado
        """
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Actualiza un producto existente.
        
        Args:
            instance (Producto): Instancia del producto a actualizar
            validated_data (dict): Datos validados para la actualización
            
        Returns:
            Producto: Instancia del producto actualizado
        """
        return super().update(instance, validated_data)

    def validate_imagen_base64(self, value):
        """
        Valida que el valor proporcionado sea una imagen válida en formato Base64.
        
        Args:
            value (str): Cadena Base64 de la imagen
            
        Returns:
            str: Cadena Base64 validada
            
        Raises:
            ValidationError: Si el valor no es una imagen válida en Base64
        """
        try:
            if value:
                import base64
                import imghdr
                decoded_file = base64.b64decode(value)
                image_type = imghdr.what(None, decoded_file)
                if not image_type:
                    raise serializers.ValidationError("El archivo no es una imagen válida")
            return value
        except Exception as e:
            raise serializers.ValidationError(f"Error al procesar la imagen: {str(e)}")


class PedidoDetalleSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo PedidoDetalle.
    
    Este serializer maneja la serialización de detalles de pedido,
    incluyendo información adicional del producto.
    
    Campos:
        id: Identificador del detalle
        pedido: Referencia al pedido
        producto: Referencia al producto
        producto_nombre: Nombre del producto (solo lectura)
        producto_precio: Precio del producto (solo lectura)
        cantidad_prod: Cantidad de productos
        subtotal: Subtotal del detalle
        isv: Impuesto sobre ventas
        envio: Costo de envío
        total: Total del detalle
    """
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_precio = serializers.DecimalField(source='producto.precio', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = PedidoDetalle
        fields = ['id', 'pedido', 'producto', 'producto_nombre', 'producto_precio',
                 'cantidad_prod', 'subtotal', 'isv', 'envio', 'total']
        read_only_fields = ['id', 'subtotal', 'isv', 'envio', 'total']


class PedidoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Pedido.
    
    Este serializer maneja la serialización de pedidos,
    incluyendo sus detalles y totales.
    
    Campos:
        id_pedido: Identificador del pedido
        usuario: Referencia al usuario
        usuario_nombre: Nombre del usuario (solo lectura)
        company: Compañía
        direccion: Dirección de envío
        pais: País
        pais_nombre: Nombre del país (solo lectura)
        estado_pais: Estado/Provincia
        ciudad: Ciudad
        zip: Código postal
        correo: Correo electrónico
        telefono: Teléfono
        estado_compra: Estado del pedido
        desc_adicional: Descripción adicional
        fecha_compra: Fecha de creación
        fecha_entrega: Fecha de entrega
        detalles: Lista de detalles del pedido
        total_pedido: Total del pedido (solo lectura)
        es_movimiento_interno: Indica si es un movimiento interno
    """
    detalles = PedidoDetalleSerializer(many=True, read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre_cliente', read_only=True)
    pais_nombre = serializers.CharField(source='pais', read_only=True)
    total_pedido = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id_pedido', 'usuario', 'usuario_nombre', 'company', 'direccion',
                 'pais', 'pais_nombre', 'estado_pais', 'ciudad', 'zip', 'correo',
                 'telefono', 'estado_compra', 'desc_adicional', 'fecha_compra',
                 'fecha_entrega', 'detalles', 'total_pedido', 'es_movimiento_interno']
        read_only_fields = ['id_pedido', 'fecha_compra', 'total_pedido', 'usuario_nombre', 'pais_nombre', 'es_movimiento_interno']


class PedidoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para la creación de pedidos.
    
    Este serializer maneja la creación de pedidos con múltiples productos.
    
    Campos:
        usuario: Referencia al usuario
        company: Compañía
        direccion: Dirección de envío
        pais: País
        estado_pais: Estado/Provincia
        ciudad: Ciudad
        zip: Código postal
        correo: Correo electrónico
        telefono: Teléfono
        desc_adicional: Descripción adicional
        productos: Lista de productos a incluir en el pedido
        estado_compra: Estado del pedido
    """
    productos = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = Pedido
        fields = ['usuario', 'company', 'direccion', 'pais', 'estado_pais',
                 'ciudad', 'zip', 'correo', 'telefono', 'desc_adicional', 'productos', 'estado_compra']


class UsersSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo User de Django.
    
    Este serializer maneja la serialización de usuarios del sistema.
    
    Campos:
        username: Nombre de usuario
        first_name: Nombre
        last_name: Apellido
        email: Correo electrónico
    """
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']






