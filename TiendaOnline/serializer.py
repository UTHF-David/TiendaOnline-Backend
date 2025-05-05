from rest_framework import serializers
from .models import Producto, Pedido

class TiendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto,Pedido  # Indica el modelo que se va a serializar
        fields = '__all__' # Indica que se deben incluir todos los campos del modelo



