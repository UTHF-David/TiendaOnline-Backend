from rest_framework import serializers
from .models import Producto, Pedido
import base64
import imghdr
from django.core.files.base import ContentFile
from django.utils.text import slugify
import uuid

class Base64ImageField(serializers.Field):
    def to_internal_value(self, data):
        try:
            # Si ya es solo base64 (sin prefijo data:image)
            if isinstance(data, str) and not data.startswith('data:image'):
                return data
            
            # Si viene con prefijo data:image
            if isinstance(data, str) and data.startswith('data:image'):
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                
                # Validar que sea una imagen válida
                decoded_file = base64.b64decode(imgstr)
                image_type = imghdr.what(None, decoded_file)
                if not image_type:
                    raise serializers.ValidationError("El archivo no es una imagen válida")
                
                return imgstr
            
            return None
        except Exception as e:
            raise serializers.ValidationError(f"Error al procesar la imagen: {str(e)}")

    def to_representation(self, value):
        if value:
            return f"data:image/jpeg;base64,{value}"
        return None

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'
        extra_kwargs = {
            'imagen_base64': {'required': False}
        }

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor a cero")
        return value

    def validate_cantidad_en_stock(self, value):
        if value < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa")
        return value

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = '__all__'