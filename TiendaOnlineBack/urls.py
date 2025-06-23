# =============================================================================
# CONFIGURACIÓN DE URLs PRINCIPAL DEL PROYECTO
# =============================================================================
"""
URL configuration for TiendaOnlineBack project.

Este archivo define las rutas principales del proyecto Django para la tienda online.
Incluye rutas para administración, APIs, documentación, autenticación y archivos estáticos.

Estructura de URLs:
- /admin/ - Panel de administración de Django
- /api/v1/ - APIs REST de la aplicación principal
- /docs/ - Documentación automática de la API
- /media/ - Archivos multimedia
- /login/, /register/, /profile/ - Endpoints de autenticación
- /stockvisible/ - Consultas de stock en tiempo real

Para más información sobre URLs en Django:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/

Ejemplos de configuración:
Function views:
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')

Class-based views:
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')

Including another URLconf:
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# =============================================================================
# IMPORTS NECESARIOS
# =============================================================================
from django.contrib import admin
from django.urls import path, include
from django.conf import settings  # Importa la configuración de Django
from django.conf.urls.static import static  # Importa la función para servir archivos estáticos
from rest_framework.documentation import include_docs_urls  # Importa la función para incluir la documentación de la API
from django.views.static import serve  # Importa la vista para servir archivos estáticos

# Imports de vistas específicas de la aplicación
from TiendaOnline.views import UsuarioViewSet
from TiendaOnline.conexion import stockvisible
from TiendaOnline.views import actualizar_stock

# =============================================================================
# PATRONES DE URL PRINCIPALES
# =============================================================================
urlpatterns = [
    # =====================================================================
    # ADMINISTRACIÓN Y DOCUMENTACIÓN
    # =====================================================================
    path('admin/', admin.site.urls),  # Panel de administración de Django
    
    # =====================================================================
    # APIs DE LA APLICACIÓN PRINCIPAL
    # =====================================================================
    path('api/v1/', include('TiendaOnline.urls')),  # Incluye las URLs de la aplicación 'TiendaOnline'
    
    # =====================================================================
    # SERVICIO DE ARCHIVOS ESTÁTICOS Y MEDIA
    # =====================================================================
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),  # Servir archivos multimedia
    
    # =====================================================================
    # DOCUMENTACIÓN DE LA API
    # =====================================================================
    path('docs/', include_docs_urls(title='API Documentation')),  # Documentación automática de la API
    
    # =====================================================================
    # ENDPOINTS DE STOCK Y PRODUCTOS
    # =====================================================================
    path('stockvisible/<int:id>/', stockvisible, name='stock-visible'),  # Consulta de stock visible
    path('producto/<int:producto_id>/actualizar-stock/', actualizar_stock, name='actualizar_stock'),  # Actualización de stock
    
    # =====================================================================
    # ENDPOINTS DE AUTENTICACIÓN Y USUARIOS
    # =====================================================================
    path('login/', UsuarioViewSet.login, name='login'),      # Login de usuarios
    path('register/', UsuarioViewSet.register, name='register'),  # Registro de usuarios
    path('profile/', UsuarioViewSet.profile, name='profile'),     # Perfil de usuario
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Configuración para servir archivos estáticos en desarrollo


