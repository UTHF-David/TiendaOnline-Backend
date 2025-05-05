from django.shortcuts import render
from rest_framework import viewsets
from .models import Producto, Pedido
from .serializer import ProductoSerializer, PedidoSerializer  # Importa ambos serializadores

# ViewSet para Producto
class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()  # Consulta TODOS los productos
    serializer_class = ProductoSerializer  # Usa el serializador de Producto

# ViewSet para Pedido
class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()  # Consulta TODOS los pedidos
    serializer_class = PedidoSerializer  # Usa el serializador de Pedido