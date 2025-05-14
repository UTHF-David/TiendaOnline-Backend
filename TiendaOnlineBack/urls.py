"""
URL configuration for TiendaOnlineBack project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings # Importa la configuración de Django
from django.conf.urls.static import static # Importa la función para servir archivos estáticos
from rest_framework.documentation import include_docs_urls # Importa la función para incluir la documentación de la API
from django.views.static import serve # Importa la vista para servir archivos estáticos



urlpatterns = [
    path('admin/', admin.site.urls),        
    path('api/v1/', include('TiendaOnline.urls')), # Incluye las URLs de la aplicación 'tienda'
    path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    path('docs/', include_docs_urls(title='API Documentation')), # Incluye la documentación de la API
    
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Para servir archivos estáticos en desarrollo


