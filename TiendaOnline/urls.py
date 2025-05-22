from django.urls import path, include
from django.contrib import admin
from .views import ProductoViewSet, PedidoViewSet, ISVPaisViewSet, UsuarioViewSet, PedidoDetalleViewSet # Importa los viewsets de Producto y Pedido
from rest_framework.routers import DefaultRouter #importacion del router
#from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


# Importa el viewset de Producto y Pedido
router = DefaultRouter() #creacion del router
router.register(r'productos', ProductoViewSet)  # /api/productos/
router.register(r'pedidos', PedidoViewSet)     # /api/pedidos/
router.register(r'paises', ISVPaisViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'detalles-pedido', PedidoDetalleViewSet)

# r'tareas' es la ruta de la api
# TareasView es la vista de las tareas



#Creacion de las rutas de la api
urlpatterns = [
    path('', include(router.urls)), #ruta de la api url base
    path('admin/', admin.site.urls), #ruta del admin    
    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    #path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        
]