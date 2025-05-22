from rest_framework import serializers
from .models import Producto, Pedido, PedidoDetalle, Usuario, ISVPais
from django.contrib.auth.models import User


class ISVPaisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ISVPais
        fields = '__all__'


#Con este serializer se puede crear un usuario con un pais
class UsuarioSerializer(serializers.ModelSerializer):
    pais = serializers.PrimaryKeyRelatedField(
        queryset=ISVPais.objects.all(),
        required=False,
        allow_null=True
    )   

    class Meta:
        model = Usuario
        fields = '__all__'
        read_only_fields = ['id']


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
        fields = ['id', 'producto', 'producto_nombre', 'producto_precio', 
                 'cantidad_prod', 'subtotal', 'isv', 'envio', 'total']
        read_only_fields = ['subtotal', 'isv', 'envio', 'total']


class PedidoSerializer(serializers.ModelSerializer):
    detalles = PedidoDetalleSerializer(many=True, read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre_cliente', read_only=True)
    pais_nombre = serializers.CharField(source='pais.pais', read_only=True)
    total_pedido = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Pedido
        fields = ['id_pedido', 'usuario', 'usuario_nombre', 'company', 'direccion',
                 'pais', 'pais_nombre', 'estado_pais', 'ciudad', 'zip', 'correo',
                 'telefono', 'estado_compra', 'desc_adicional', 'fecha_compra',
                 'fecha_entrega', 'detalles', 'total_pedido']
        read_only_fields = ['id_pedido', 'fecha_compra', 'total_pedido']


class PedidoCreateSerializer(serializers.ModelSerializer):
    productos = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    class Meta:
        model = Pedido
        fields = ['usuario', 'company', 'direccion', 'pais', 'estado_pais',
                 'ciudad', 'zip', 'correo', 'telefono', 'desc_adicional', 'productos']


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'middle_name', 'last_name', 'email']
