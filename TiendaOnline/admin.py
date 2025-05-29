from django.contrib import admin
from .models import Producto, Pedido, Usuario, PedidoDetalle, CarritoTemp


# Reegister los modelos en el admin de Django
# Esto permite que los modelos sean administrados a través de la interfaz de administración de Django
admin.site.register(Producto)
admin.site.register(Pedido)
admin.site.register(Usuario)
admin.site.register(PedidoDetalle)
admin.site.register(CarritoTemp) 
