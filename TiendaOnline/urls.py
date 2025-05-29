from django.urls import path, include
from django.contrib import admin
from .views import ProductoViewSet, PedidoViewSet, UsuarioViewSet, PedidoDetalleViewSet
from .views import RegistrarMovimientoView, CarritoTempViewSet
from rest_framework.routers import DefaultRouter
#from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


# Creación del router
router = DefaultRouter()
router.register(r'productos', ProductoViewSet)
router.register(r'pedidos', PedidoViewSet)
router.register(r'usuarios', UsuarioViewSet)
router.register(r'detalles-pedido', PedidoDetalleViewSet)
router.register(r'carrito', CarritoTempViewSet, basename='carrito')


# r'tareas' es la ruta de la api
# TareasView es la vista de las tareas



#Creacion de las rutas de la api
urlpatterns = [
    path('', include(router.urls)), #ruta de la api url base
    path('admin/', admin.site.urls), #ruta del admin            
    path('movimientos/', RegistrarMovimientoView.as_view(), name='registrar_movimiento'),

    #path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    #path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
        
]