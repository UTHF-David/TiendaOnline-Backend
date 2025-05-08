from rest_framework import serializers
from .models import Producto, Pedido

# Serializador para Producto
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'  # Todos los campos del modelo Producto

               
    def get_imagen(self, obj):
        if obj.imagen:
            return self.context['request'].build_absolute_uri(obj.imagen.url)
        return None

# Serializador para Pedido (con Producto anidado si lo necesitas)
class PedidoSerializer(serializers.ModelSerializer):
    # Opción 1: Solo muestra el ID del Producto (por defecto)
    class Meta:
        model = Pedido
        fields = '__all__'

    # Opción 2: Si quieres incluir los datos completos del Producto en el Pedido
    # producto = ProductoSerializer()  # Descomenta esta línea si lo necesitas
    # class Meta:
    #     model = Pedido
    #     fields = '__all__'

    

