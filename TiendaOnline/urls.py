from django.urls import path, include
from django.contrib import admin
from .views import ProductoViewSet, PedidoViewSet # Importa los viewsets de Producto y Pedido
from rest_framework.routers import DefaultRouter #importacion del router
from .views import ProductoViewSet, PedidoViewSet  # Importa la vista personalizada

# Importa el viewset de Producto y Pedido
router = DefaultRouter() #creacion del router
router.register(r'productos', ProductoViewSet)  # /api/productos/
router.register(r'pedidos', PedidoViewSet)     # /api/pedidos/

# r'tareas' es la ruta de la api
# TareasView es la vista de las tareas



#Creacion de las rutas de la api
urlpatterns = [
    path('', include(router.urls)), #ruta de la api url base
    path('admin/', admin.site.urls), #ruta del admin    

    
    
    
    
]