from django.shortcuts import render
from rest_framework import viewsets
from .models import Producto, Pedido
from .serializer import TiendaSerializer

class TiendaView(viewsets.ModelViewSet):
    queryset = Producto.objects.all() #esta es la consulta a la base de datos, devuelve todos los objetos de la tabla
    queryset = Pedido.objects.all() 
    serializer_class = TiendaSerializer #esta es la clase que se encarga de serializar los datos, convierte los objetos de la base de datos en JSON y viceversa
