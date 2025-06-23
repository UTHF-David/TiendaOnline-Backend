# 🛒 TiendaOnline Backend

## 📋 Descripción del Proyecto

Backend completo para una tienda online desarrollado con Django y Django REST Framework. Este sistema incluye gestión de usuarios, productos, pedidos, carrito de compras temporal, y notificaciones en tiempo real.

## 🚀 Tecnologías Utilizadas

### **Lenguajes y Frameworks**
- **Python 3.x** - Lenguaje principal
- **Django 4.2.3** - Framework web
- **Django REST Framework 3.14.0** - Framework para APIs REST

### **Base de Datos**
- **MySQL** - Base de datos relacional
- **Railway** - Hosting de base de datos

### **APIs y Comunicación**
- **Pusher 3.3.3** - Comunicación en tiempo real
- **CoreAPI 2.3.3** - Documentación automática de APIs
- **CORS Headers 4.3.1** - Manejo de Cross-Origin Resource Sharing

### **Procesamiento de Imágenes**
- **Pillow 10.3.0** - Procesamiento de imágenes
- **Cloudinary 1.32.0** - Almacenamiento en la nube
- **django-cloudinary-storage 0.3.0** - Integración con Cloudinary

### **Programación de Tareas**
- **django-apscheduler 0.7.0** - Programador de tareas
- **APScheduler** - Framework de tareas en segundo plano

### **Despliegue**
- **Waitress 2.1.2** - Servidor WSGI para producción
- **Render** - Plataforma de hosting
- **python-dotenv 1.0.0** - Variables de entorno

## 🏗️ Arquitectura del Sistema

### **Modelos Principales**

#### 1. **Usuario (Usuario)**
- Extensión del modelo AbstractUser de Django
- Autenticación por email en lugar de username
- Campos adicionales: nombre, apellido, dirección, país, etc.
- Manager personalizado para creación de usuarios

#### 2. **Producto (Producto)**
- Gestión completa de productos
- Categorías por género (Mujeres, Hombres, Unisex)
- Tamaños disponibles (S, M, L, XL, XXL)
- Colores en formato hexadecimal
- Imágenes almacenadas en Base64
- Control de stock en tiempo real

#### 3. **Pedido (Pedido)**
- Gestión completa de pedidos de clientes
- Estados: Pagado, En Camino, Recibido, Cancelado
- Información de envío completa
- Cálculo automático de totales
- Soporte para movimientos internos

#### 4. **Detalle de Pedido (PedidoDetalle)**
- Relación con pedido y producto
- Cálculo automático de subtotales, ISV, envío y total
- Validaciones de cantidades y precios
- Gestión de impuestos por país

#### 5. **Carrito Temporal (CarritoTemp)**
- Gestión de carrito de compras temporal
- Reserva automática de stock
- Sistema de expiración (3 minutos de inactividad)
- Verificación de disponibilidad de stock
- Notificaciones en tiempo real

### **Funcionalidades Principales**

#### 🔐 **Sistema de Autenticación**
- Registro de usuarios con email
- Login con tokens
- Perfil de usuario personalizable
- Validación de contraseñas robusta

#### 📦 **Gestión de Productos**
- CRUD completo de productos
- Categorización por género y tamaño
- Control de stock en tiempo real
- Imágenes en Base64
- Colores hexadecimales

#### 🛒 **Carrito de Compras**
- Carrito temporal con expiración automática
- Reserva de stock automática
- Verificación de disponibilidad
- Notificaciones push en tiempo real
- Liberación automática de stock expirado

#### 📋 **Sistema de Pedidos**
- Creación y gestión de pedidos
- Cálculo automático de impuestos (ISV)
- Gestión de costos de envío por país
- Estados de pedido configurables
- Movimientos internos

#### ⏰ **Tareas Programadas**
- Verificación automática de carritos expirados
- Limpieza de datos temporales
- Mantenimiento de integridad de datos
- Logging de operaciones automáticas

#### 🔔 **Notificaciones en Tiempo Real**
- Actualizaciones de stock en tiempo real
- Notificaciones push con Pusher
- Canales específicos por producto
- Eventos de actualización de carrito

## 📁 Estructura del Proyecto

```
TiendaOnline-Backend/
├── TiendaOnlineBack/          # Configuración principal del proyecto
│   ├── settings.py            # Configuración de Django
│   ├── urls.py                # URLs principales
│   ├── wsgi.py                # Configuración WSGI
│   └── asgi.py                # Configuración ASGI
├── TiendaOnline/              # Aplicación principal
│   ├── models.py              # Modelos de datos
│   ├── views.py               # Vistas y ViewSets
│   ├── serializer.py          # Serializers para APIs
│   ├── urls.py                # URLs de la aplicación
│   ├── conexion.py            # Conexiones y procedimientos almacenados
│   ├── scheduler.py           # Configuración de tareas programadas
│   ├── tasks.py               # Tareas automáticas
│   ├── admin.py               # Configuración del admin
│   └── migrations/            # Migraciones de base de datos
├── requirements.txt           # Dependencias del proyecto
└── README.md                  # Documentación
```

## 🚀 Instalación y Configuración

### **Prerrequisitos**
- Python 3.8 o superior
- MySQL 5.7 o superior
- pip (gestor de paquetes de Python)

### **Pasos de Instalación**

1. **Clonar el repositorio**
   ```bash
   git clone <url-del-repositorio>
   cd TiendaOnline-Backend
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**
   - Crear base de datos MySQL
   - Actualizar configuración en `TiendaOnlineBack/settings.py`

5. **Ejecutar migraciones**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

7. **Ejecutar el servidor**
   ```bash
   python manage.py runserver
   ```

## 🔧 Configuración de Variables de Entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
# Configuración de Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Configuración de base de datos
DB_NAME=nombre_base_datos
DB_USER=usuario_base_datos
DB_PASSWORD=contraseña_base_datos
DB_HOST=host_base_datos
DB_PORT=puerto_base_datos

# Configuración de Pusher
PUSHER_APP_ID=tu-app-id
PUSHER_KEY=tu-key
PUSHER_SECRET=tu-secret
PUSHER_CLUSTER=tu-cluster
```

## 📚 Documentación de la API

### **Endpoints Principales**

#### **Autenticación**
- `POST /login/` - Login de usuario
- `POST /register/` - Registro de usuario
- `GET /profile/` - Perfil de usuario

#### **Productos**
- `GET /api/v1/productos/` - Listar productos
- `POST /api/v1/productos/` - Crear producto
- `GET /api/v1/productos/{id}/` - Obtener producto
- `PUT /api/v1/productos/{id}/` - Actualizar producto
- `DELETE /api/v1/productos/{id}/` - Eliminar producto

#### **Pedidos**
- `GET /api/v1/pedidos/` - Listar pedidos
- `POST /api/v1/pedidos/` - Crear pedido
- `GET /api/v1/pedidos/{id}/` - Obtener pedido
- `PUT /api/v1/pedidos/{id}/` - Actualizar pedido

#### **Carrito**
- `GET /api/v1/carrito/` - Obtener carrito del usuario
- `POST /api/v1/carrito/` - Agregar producto al carrito
- `PUT /api/v1/carrito/{id}/` - Actualizar cantidad
- `DELETE /api/v1/carrito/{id}/` - Eliminar del carrito

#### **Stock**
- `GET /stockvisible/{id}/` - Consultar stock visible
- `POST /producto/{id}/actualizar-stock/` - Actualizar stock

### **Documentación Automática**
- Acceder a `/docs/` para ver la documentación interactiva de la API

## 🔄 Tareas Programadas

El sistema incluye tareas automáticas que se ejecutan cada 3 minutos:

- **Verificación de carritos expirados**: Libera stock de carritos inactivos
- **Limpieza de datos temporales**: Mantiene la integridad de la base de datos
- **Logging de operaciones**: Registra todas las operaciones automáticas

## 🔔 Notificaciones en Tiempo Real

El sistema utiliza Pusher para notificaciones en tiempo real:

- **Actualizaciones de stock**: Notifica cambios en disponibilidad
- **Expiración de carrito**: Alerta sobre productos que expiran
- **Canal por producto**: Cada producto tiene su propio canal de notificaciones

## 🛡️ Seguridad

### **Configuraciones Implementadas**
- CORS configurado para dominios específicos
- CSRF protection habilitado
- Validación de contraseñas robusta
- Autenticación por tokens
- Cookies seguras para HTTPS

### **Recomendaciones de Producción**
- Cambiar `SECRET_KEY` en producción
- Deshabilitar `DEBUG` en producción
- Configurar `ALLOWED_HOSTS` específicos
- Usar HTTPS en producción
- Configurar variables de entorno

## 🚀 Despliegue

### **Render (Recomendado)**
1. Conectar repositorio a Render
2. Configurar variables de entorno
3. Configurar base de datos MySQL
4. Desplegar automáticamente

### **Otras Plataformas**
- **Heroku**: Configurar buildpacks y variables de entorno
- **DigitalOcean**: Usar App Platform o Droplets
- **AWS**: Usar Elastic Beanstalk o EC2

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama para nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👥 Autores

- **Desarrollador Principal** - [Tu Nombre]
- **Contribuidores** - [Lista de contribuidores]

## 📞 Soporte

Para soporte técnico o preguntas:
- Email: [igyt2015@gmail.com]
- Issues: [Crear issue en GitHub]
- Documentación: `/docs/` en el servidor

---

**¡Gracias por usar TiendaOnline Backend! 🎉**

