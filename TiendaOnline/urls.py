# =============================================================================
# CONFIGURACIÓN DE URLs DE LA APLICACIÓN TIENDAONLINE
# =============================================================================
"""
Este archivo define las rutas de la API REST para la aplicación TiendaOnline.
Utiliza Django REST Framework con ViewSets y routers para generar automáticamente
las URLs CRUD para cada modelo.

Estructura de la API:
- /api/v1/productos/ - Gestión de productos
- /api/v1/pedidos/ - Gestión de pedidos
- /api/v1/usuarios/ - Gestión de usuarios
- /api/v1/detalles-pedido/ - Gestión de detalles de pedidos
- /api/v1/carrito/ - Gestión del carrito temporal
- /api/v1/movimientos/ - Registro de movimientos internos

Cada endpoint incluye automáticamente:
- GET / - Listar todos los elementos
- POST / - Crear nuevo elemento
- GET /{id}/ - Obtener elemento específico
- PUT /{id}/ - Actualizar elemento completo
- PATCH /{id}/ - Actualizar elemento parcialmente
- DELETE /{id}/ - Eliminar elemento
"""

# =============================================================================
# IMPORTS NECESARIOS
# =============================================================================
from django.urls import path, include
from django.contrib import admin
from .views import ProductoViewSet, PedidoViewSet, UsuarioViewSet, PedidoDetalleViewSet, CarritoTempViewSet
from .views import RegistrarMovimientoView
from rest_framework.routers import DefaultRouter
#from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView


# =============================================================================
# CONFIGURACIÓN DEL ROUTER PRINCIPAL
# =============================================================================
# Creación del router de Django REST Framework
# El router genera automáticamente las URLs CRUD para cada ViewSet
router = DefaultRouter()

# Registro de ViewSets en el router
router.register(r'productos', ProductoViewSet)           # CRUD para productos
router.register(r'pedidos', PedidoViewSet)               # CRUD para pedidos
router.register(r'usuarios', UsuarioViewSet)             # CRUD para usuarios
router.register(r'detalles-pedido', PedidoDetalleViewSet)  # CRUD para detalles de pedidos
router.register(r'carrito', CarritoTempViewSet, basename='carrito')  # CRUD para carrito temporal


# r'tareas' es la ruta de la api
# TareasView es la vista de las tareas



# =============================================================================
# PATRONES DE URL DE LA APLICACIÓN
# =============================================================================
# Creación de las rutas de la API
urlpatterns = [
    # =====================================================================
    # RUTAS PRINCIPALES DE LA API
    # =====================================================================
    path('', include(router.urls)),  # Incluye todas las rutas generadas por el router
    
    # =====================================================================
    # ADMINISTRACIÓN
    # =====================================================================
    path('admin/', admin.site.urls),  # Ruta del panel de administración
    
    # =====================================================================
    # ENDPOINTS ESPECIALES
    # =====================================================================
    path('movimientos/', RegistrarMovimientoView.as_view(), name='registrar_movimiento'),  # Registro de movimientos internos

    # =====================================================================
    # ENDPOINTS DE AUTENTICACIÓN JWT (COMENTADOS)
    # =====================================================================
    # Configuración alternativa de autenticación con JWT
    # path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]