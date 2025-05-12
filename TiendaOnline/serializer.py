from rest_framework import serializers
from .models import Producto, Pedido

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

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'