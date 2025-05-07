from rest_framework import serializers
from .models import Producto, Pedido

# Serializador para Producto
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'  # Todos los campos del modelo Producto

               
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Asegura que la URL de la imagen sea absoluta
        if instance.imagen:
            data['imagen'] = self.context['request'].build_absolute_uri(instance.imagen.url)
        return data

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

    from rest_framework import serializers

