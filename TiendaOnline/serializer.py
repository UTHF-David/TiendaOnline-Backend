from rest_framework import serializers
from .models import Producto, Pedido, PedidoDetalle, Usuario, CarritoTemp
from django.contrib.auth.models import User
from decimal import Decimal # Importar Decimal si se usa en algún serializer (aunque en PedidoDetalle.save es donde se usa principalmente)





#Con este serializer se puede crear un usuario con un pais
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
        extra_kwargs = {
            'imagen_base64': {'required': False}
        }

    def create(self, validated_data):
        # Guardar directamente la cadena Base64 en la base de datos
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Actualizar directamente la cadena Base64 en la base de datos
        return super().update(instance, validated_data)

    def validate_imagen_base64(self, value):
        # Validar que el valor sea una imagen válida en formato Base64
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
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_precio = serializers.DecimalField(source='producto.precio', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = PedidoDetalle
        fields = ['id', 'pedido', 'producto', 'producto_nombre', 'producto_precio',
                 'cantidad_prod', 'subtotal', 'isv', 'envio', 'total']
        # Se elimina 'envio' de read_only_fields para permitir que se escriba
        read_only_fields = ['id', 'subtotal', 'isv', 'envio', 'total']


class PedidoSerializer(serializers.ModelSerializer):
    detalles = PedidoDetalleSerializer(many=True, read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre_cliente', read_only=True)
    # pais_nombre: si pais en modelo Pedido es CharField, no puedes usar source='pais.pais'
    # Si pais en modelo Pedido fuera ForeignKey a un modelo Pais con campo 'pais', esto estaría bien
    # Si es CharField y guarda el ID, quizás necesites un SerializerMethodField para mostrar el nombre
    # Si es CharField y guarda el nombre, source='pais' podría funcionar si el campo es solo 'pais'
    # Por ahora, dejo pais_nombre como read_only=True y asumo que el frontend maneja la visualización del nombre.
    pais_nombre = serializers.CharField(source='pais', read_only=True) # Ajustado a source='pais' si pais es CharField

    total_pedido = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id_pedido', 'usuario', 'usuario_nombre', 'company', 'direccion',
                 'pais', 'pais_nombre', 'estado_pais', 'ciudad', 'zip', 'correo',
                 'telefono', 'estado_compra', 'desc_adicional', 'fecha_compra',
                 'fecha_entrega', 'detalles', 'total_pedido','es_movimiento_interno']
        read_only_fields = ['id_pedido', 'fecha_compra', 'total_pedido', 'usuario_nombre', 'pais_nombre','es_movimiento_interno'] # usuario_nombre y pais_nombre son read_only

class PedidoCreateSerializer(serializers.ModelSerializer):
    productos = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )
    # Asegúrate de que 'pais' aquí corresponda al tipo de datos que esperas recibir
    # Si esperas el ID numérico del frontend y el modelo Pedido.pais es CharField,
    # quizás necesites validar y guardar el ID como cadena o convertirlo a nombre si lo prefieres.
    # Por simplicidad, asumimos que recibes algo que puedes asignar directamente al CharField 'pais'.


    class Meta:
        model = Pedido
        fields = ['usuario', 'company', 'direccion', 'pais', 'estado_pais',
                 'ciudad', 'zip', 'correo', 'telefono', 'desc_adicional', 'productos', 'estado_compra'] # Incluir estado_compra si el backend lo establece o lo recibe

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User # O Usuario si este serializer es para el modelo Usuario principal
        fields = ['username', 'first_name', 'last_name', 'email'] # Middle_name no está en AbstractUser por defecto

class CarritoTempSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source='producto.nombre', read_only=True)
    producto_precio = serializers.DecimalField(source='producto.precio', max_digits=10, decimal_places=2, read_only=True)
    stock_disponible = serializers.IntegerField(source='producto.cantidad_en_stock', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre_cliente', read_only=True)

    class Meta:
        model = CarritoTemp
        fields = ['id', 'usuario', 'usuario_nombre', 'producto', 'producto_nombre', 
                  'cantidad_prod', 'cantidad_temp', 'stock_disponible']
        read_only_fields = ['id', 'usuario_nombre', 'producto_nombre', 'stock_disponible']

    def validate(self, data):
        # Validar que la cantidad no exceda el stock disponible
        if data.get('cantidad_prod', 0) > data['producto'].cantidad_en_stock:
            raise serializers.ValidationError(
                f'La cantidad excede el stock disponible ({data["producto"].cantidad_en_stock} unidades)'
            )
        return data

