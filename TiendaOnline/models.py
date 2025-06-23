from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta # Asegúrate de importar timedelta aquí

# =============================================================================
# MANAGER PERSONALIZADO PARA USUARIOS
# =============================================================================
class UsuarioManager(BaseUserManager):
    """
    Manager personalizado para el modelo Usuario.
    Permite crear usuarios usando email en lugar de username.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Crea y guarda un usuario regular con el email y contraseña dados.
        
        Args:
            email: Email del usuario (obligatorio)
            password: Contraseña del usuario
            **extra_fields: Campos adicionales del usuario
            
        Returns:
            Usuario: Instancia del usuario creado
            
        Raises:
            ValueError: Si el email no se proporciona
        """
        if not email:
            raise ValueError('El Email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con el email y contraseña dados.
        
        Args:
            email: Email del superusuario
            password: Contraseña del superusuario
            **extra_fields: Campos adicionales
            
        Returns:
            Usuario: Instancia del superusuario creado
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)
    
    class Meta:
        verbose_name = 'País con ISV'
        verbose_name_plural = 'Países con ISV'
    
    def __str__(self):
        return f"{self.pais} (Envío: ${self.costo_envio_pais})"

# =============================================================================
# MODELO DE USUARIO PERSONALIZADO
# =============================================================================
class Usuario(AbstractUser):
    """
    Modelo extendido de usuario con todos los campos requeridos para una tienda online.
    
    Características principales:
    - Usa email como campo de autenticación principal
    - Incluye campos adicionales para información de cliente
    - Extiende el modelo AbstractUser de Django
    """
    id = models.AutoField(primary_key=True)

    # Deshabilitamos el campo username para usar email como login
    username = None  
    
    # Campo principal de autenticación
    email = models.EmailField(
        verbose_name='Correo Electrónico',
        unique=True,
        null=False
    )
    
    # Información personal del cliente
    nombre_cliente = models.CharField(
        max_length=100,
        verbose_name='Nombre del Cliente',
        null=True
    )
    apellido_cliente = models.CharField(
        max_length=100,
        verbose_name='Apellido del Cliente',
        null=True
    )
    
    # Información de dirección
    direccion = models.TextField(
        verbose_name='Dirección',
        null=True
    )
    pais = models.CharField(                
        max_length=100,
        null=True,
        verbose_name='País'
    )
    estado_pais = models.CharField(
        max_length=100,
        verbose_name='Estado/Provincia',
        null=True
    )
    ciudad = models.CharField(
        max_length=100,
        verbose_name='Ciudad',
        null=True
    )
    zip = models.CharField(
        max_length=20,
        verbose_name='Código Postal',
        null=True
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name='Teléfono',
        null=True
    )

    # Relaciones con grupos y permisos (heredadas de AbstractUser)
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="tienda_usuario_set",  # Nombre único para evitar conflictos
        related_query_name="tienda_usuario",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="tienda_usuario_set",  # Nombre único para evitar conflictos
        related_query_name="tienda_usuario",
    )

    # Usamos nuestro manager personalizado
    objects = UsuarioManager()

    # Configuración de autenticación
    USERNAME_FIELD = 'email'  # Campo usado para login
    REQUIRED_FIELDS = ['nombre_cliente', 'apellido_cliente']  # Campos requeridos para crear superusuario

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        """Representación en string del usuario"""
        return f"{self.nombre_cliente} {self.apellido_cliente} ({self.email})"

# =============================================================================
# MODELO DE PRODUCTO
# =============================================================================
class Producto(models.Model):
    """
    Modelo para productos con color hexadecimal único.
    
    Características:
    - Categorías por género (Mujeres, Hombres, Unisex)
    - Tamaños disponibles (S, M, L, XL, XXL)
    - Colores en formato hexadecimal
    - Imágenes almacenadas en Base64
    - Control de stock
    """
    
    # Opciones para categorías de productos
    CATEGORIA_CHOICES = [
        ('M', 'Mujeres'),
        ('H', 'Hombres'),
        ('U', 'Unisex')
    ]
    
    # Opciones para tamaños de productos
    TAMANO_CHOICES = [
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL')
    ]
    
    # Campos básicos del producto
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre del Producto',
        null=False
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio',
        validators=[MinValueValidator(0.01)],  # Precio mínimo de 0.01
        null=False
    )
    cantidad_en_stock = models.PositiveIntegerField(
        verbose_name='Stock',
        help_text='Cantidad disponible en inventario',
        validators=[MinValueValidator(0)],  # Stock no puede ser negativo
        null=False
    )
    desc_prod = models.TextField(
        verbose_name='Descripción del Producto',
        blank=True,
        null=True
    )
    
    # Imagen almacenada como Base64 (para evitar dependencias de archivos)
    image = models.TextField(
        verbose_name='Imagen en Base64',
        help_text='Imagen del producto codificada en Base64',
        blank=True,
        null=True
    )
    
    # Categorización del producto
    categoria = models.CharField(
        max_length=3,
        choices=CATEGORIA_CHOICES,
        verbose_name='Categoría',
        null=False
    )
    tamano = models.CharField(
        max_length=3,
        choices=TAMANO_CHOICES,
        verbose_name='tamano',
        help_text='Tamaño del producto',
        blank=True,
        null=True
    )
    
    # Color en formato hexadecimal con validación
    colores = models.CharField(
        max_length=7,
        verbose_name='Color Hexadecimal',
        help_text='Color en formato hexadecimal (ej. #FF0000)',
        default='#FFFFFF',
        validators=[
            RegexValidator(
                regex='^#[0-9A-Fa-f]{6}$',
                message='Formato hexadecimal inválido. Debe ser como #RRGGBB'
            )
        ],
        null=False,
        blank=False
    )
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
    
    def clean(self):
        """Validación adicional para asegurar que el color es válido"""
        super().clean()
        if not self.colores.startswith('#'):
            raise ValidationError({'colores': 'El color debe comenzar con #'})
    
    def formatted_price(self):
        """Devuelve el precio formateado como cadena"""
        return f"${self.precio:.2f}"
    
    def __str__(self):
        return f"{self.nombre} ({self.get_categoria_display()}) - Color: {self.colores}"

# =============================================================================
# MODELO DE PEDIDO
# =============================================================================
class Pedido(models.Model):
    """
    Modelo para pedidos con relación a usuario y país ISV.
    
    Características:
    - Gestión completa de pedidos de clientes
    - Estados de pedido (Pagado, En Camino, Recibido, Cancelado)
    - Información de envío completa
    - Cálculo automático de totales
    - Soporte para movimientos internos
    """
    
    # Estados posibles de un pedido
    ESTADO_CHOICES = [
        ('Pagado', 'Pagado'),
        ('En Camino', 'En Camino'),
        ('Recibido', 'Recibido'),
        ('Cancelado', 'Cancelado')
    ]
    
    # Identificador único del pedido
    id_pedido = models.AutoField(primary_key=True)
    
    # Relación con el usuario que realizó el pedido
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='pedidos',
        verbose_name='Usuario',
        null=True,  # Temporalmente permitimos nulos para pedidos sin usuario
        blank=True  # Temporalmente permitimos en blanco
    )
    
    # Información de la empresa (opcional)
    company = models.CharField(
        max_length=255,
        verbose_name='Compañía',
        blank=True,
        null=True
    )
    
    # Información de dirección de envío
    direccion = models.TextField(
        verbose_name='Dirección de Envío',
        null=False
    )
    pais = models.CharField(
        max_length=100,        
        null=True,
        verbose_name='País'
    )
    estado_pais = models.CharField(
        max_length=100,
        verbose_name='Estado/Provincia',
        null=False        
    )
    ciudad = models.CharField(
        max_length=100,
        verbose_name='Ciudad',
        null=False
    )
    zip = models.CharField(
        max_length=20,
        verbose_name='Código Postal',
        null=False
    )
    
    # Información de contacto
    correo = models.EmailField(
        verbose_name='Correo Electrónico',
        null=False
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name='Teléfono',
        null=False
    )
    
    # Estado actual del pedido
    estado_compra = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='Pagado',
        verbose_name='Estado del Pedido'        
    )
    
    # Información adicional del pedido
    desc_adicional = models.TextField(
        verbose_name='Descripción Adicional',
        blank=True,
        null=True
    )
    
    # Fechas importantes
    fecha_compra = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación',
        null=False
    )
    fecha_entrega = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Entrega'
    )
    
    # Flag para identificar movimientos internos (no comerciales)
    es_movimiento_interno = models.BooleanField(
        default=False,
        verbose_name='Movimiento interno (no comercial)')
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_compra']  # Ordenar por fecha de compra descendente
    
    def save(self, *args, **kwargs):
        """
        Autocompleta datos del usuario si no se especifican.
        Solo se ejecuta para nuevos pedidos.
        """
        if not self.pk:  # Solo para nuevos pedidos
            if not all([self.direccion, self.ciudad, self.zip, self.telefono, self.correo]):
                # Si faltan datos de envío, usar los del usuario
                self.direccion = self.usuario.direccion
                self.ciudad = self.usuario.ciudad
                self.zip = self.usuario.zip
                self.telefono = self.usuario.telefono
                self.correo = self.usuario.email
                if self.usuario.pais:
                    self.pais = self.usuario.pais
                    self.estado_pais = self.usuario.estado_pais
        super().save(*args, **kwargs)
    
    @property
    def total_pedido(self):
        """Calcula el total sumando todos los detalles del pedido"""
        return sum(detalle.total for detalle in self.detalles.all())
    
    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.usuario.nombre_cliente}"

# =============================================================================
# MODELO DE DETALLE DE PEDIDO
# =============================================================================
class PedidoDetalle(models.Model):
    """
    Modelo para detalles de pedido con cálculos automáticos.
    
    Características:
    - Relación con pedido y producto
    - Cálculo automático de subtotales, ISV, envío y total
    - Validaciones de cantidades y precios
    - Gestión de impuestos por país
    """
    
    # Relación con el pedido principal
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Pedido',
        null=False
    )
    
    # Producto incluido en el detalle
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        verbose_name='Producto',
        null=False
    )
    
    # Cantidad del producto
    cantidad_prod = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],  # Mínimo 1 producto
        verbose_name='Cantidad',
        null=False
    )
    
    # Campos de cálculo financiero
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],  # Subtotal no puede ser negativo
        null=False
    )
    isv = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='ISV',
        validators=[MinValueValidator(0)],  # ISV no puede ser negativo
        null=False
    )
    envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Envío',
        validators=[MinValueValidator(0)],  # Envío no puede ser negativo
        null=False
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],  # Total no puede ser negativo
        null=False
    )
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'
    
    def save(self, *args, **kwargs):
        """
        Calcula automáticamente los valores antes de guardar.
        
        Lógica:
        - Para movimientos internos: todos los valores monetarios son 0.00
        - Para pedidos regulares: calcula subtotal, ISV, envío y total
        - El envío se mantiene si ya fue proporcionado por el frontend
        """
        from decimal import Decimal
        
        # Si es un movimiento interno, todos los valores monetarios son 0.00
        if self.pedido.es_movimiento_interno:
            self.subtotal = Decimal('0.00')
            self.isv = Decimal('0.00')
            self.envio = Decimal('0.00')
            self.total = Decimal('0.00')
        else:
            # Cálculos normales para pedidos regulares
            self.subtotal = self.producto.precio * Decimal(str(self.cantidad_prod))
            self.isv = self.subtotal * Decimal('0.15')  # 15% de ISV
            
            # Mantener el valor de envío que viene del frontend si ya existe
            if not hasattr(self, 'envio') or self.envio is None:
                # Solo calcular envío si no se proporcionó uno
                costos_envio = {
                    'Honduras': Decimal('5.00'),
                    'Guatemala': Decimal('7.00'),
                    # Agrega más países según necesites
                }
                self.envio = costos_envio.get(self.pedido.pais, Decimal('0')) if self.pedido.pais else Decimal('0')
            
            self.total = self.subtotal + self.isv + self.envio
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Detalle #{self.id} - {self.cantidad_prod}x {self.producto.nombre}"

# =============================================================================
# MODELO DE CARRITO TEMPORAL
# =============================================================================
class CarritoTemp(models.Model):
    """
    Modelo para el carrito temporal de compras.
    
    Características principales:
    - Gestión de carrito de compras temporal
    - Reserva de stock automática
    - Sistema de expiración de carritos
    - Verificación de disponibilidad de stock
    - Notificaciones en tiempo real
    
    Funcionalidades:
    - Reserva temporal de productos en el carrito
    - Verificación automática de stock disponible
    - Expiración automática después de inactividad
    - Liberación automática de stock reservado
    """
    
    # Identificador único del carrito temporal
    id = models.AutoField(primary_key=True)
    
    # Relación con el usuario propietario del carrito
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='carritos_temp',
        verbose_name='Usuario'
    )
    
    # Producto en el carrito
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='carritos_temp',
        verbose_name='Producto'
    )
    
    # Cantidad que el usuario quiere comprar
    cantidad_prod = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],  # Mínimo 1 producto
        verbose_name='Cantidad en Carrito'
    )
    
    # Cantidad temporalmente reservada del stock
    cantidad_temp = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],  # Mínimo 1 producto reservado
        verbose_name='Cantidad Temporal (reservado)'
    )
    
    # Fechas de control
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,  # Se actualiza automáticamente en cada modificación
        verbose_name='Fecha de Actualización'
    )
    
    # Estado de expiración del carrito
    expirado = models.BooleanField(
        default=False,
        verbose_name='¿Expirado?'
    )
    
    # Campo comentado - se prefiere usar fecha_actualizacion
    # ultima_verificacion = models.DateTimeField(
    #    auto_now_add=True,
    #    verbose_name='Última Verificación'
    # )

    class Meta:
        verbose_name = 'Carrito Temporal'
        verbose_name_plural = 'Carritos Temporales'
        unique_together = ['usuario', 'producto']  # Un usuario solo puede tener un carrito por producto
        ordering = ['-fecha_actualizacion']  # Ordenar por fecha de actualización descendente

    def save(self, *args, **kwargs):
        """
        Maneja la lógica de reserva de stock al guardar.
        
        Lógica:
        - Para nuevos registros: verifica stock y reserva cantidad
        - Para actualizaciones: ajusta la reserva según la diferencia
        - Valida que haya suficiente stock disponible
        """
        # Si es un nuevo registro
        if not self.pk:
            # Verificar stock disponible
            if self.producto.cantidad_en_stock < self.cantidad_prod:
                raise ValidationError('No hay suficiente stock disponible')
            
            # Reservar el stock temporalmente
            self.cantidad_temp = self.cantidad_prod
            # Nota: El stock no se reduce físicamente, solo se reserva lógicamente
            self.producto.save()
        else:
            # Si es una actualización
            old_instance = CarritoTemp.objects.get(pk=self.pk)
            diferencia = self.cantidad_prod - old_instance.cantidad_prod
            
            if diferencia > 0:
                # Si se aumenta la cantidad
                if self.producto.cantidad_en_stock < diferencia:
                    raise ValidationError('No hay suficiente stock disponible')
                # Nota: El stock no se reduce físicamente
                self.cantidad_temp = self.cantidad_prod
            elif diferencia < 0:
                # Si se reduce la cantidad
                # Nota: El stock no se incrementa físicamente
                self.cantidad_temp = self.cantidad_prod
            
            self.producto.save()
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Devuelve el stock al eliminar el registro.
        
        Nota: Actualmente comentado para evitar problemas de concurrencia.
        El stock se libera automáticamente por el sistema de expiración.
        """
        # Solo devolver el stock si no está expirado y hay cantidad temporal
        # if not self.expirado and self.cantidad_temp > 0:
        #     self.producto.cantidad_en_stock += self.cantidad_temp
        #     self.producto.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        """Representación en string del carrito temporal"""
        return f"Carrito de {self.usuario.nombre_cliente} - {self.producto.nombre}"

    def verificar_carrito(self):
        """
        Verifica el estado del carrito y ajusta la cantidad si excede el stock disponible.
        
        Returns:
            bool: True si el item es válido y ajustado, False si el producto no existe o está sin stock.
        
        Lógica:
        - Verifica si el producto existe
        - Ajusta cantidad si excede el stock disponible
        - Marca como expirado si no hay stock
        - Libera stock reservado si es necesario
        """
        if not self.producto:
            self.expirado = True
            self.save()
            return False  # Producto no existe, marcar como no válido

        if self.cantidad_prod > self.producto.cantidad_en_stock:
            # Si la cantidad en carrito es mayor que el stock disponible
            if self.producto.cantidad_en_stock > 0:
                # Ajustar cantidad al stock disponible
                self.cantidad_prod = self.producto.cantidad_en_stock
                self.cantidad_temp = self.cantidad_prod
                self.expirado = False  # Asegurarse de que no esté marcado como expirado si se ajustó
                self.save()
                return True  # Válido con cantidad ajustada
            else:
                # Stock es 0, el producto está completamente sin stock
                self.expirado = True
                if self.cantidad_temp > 0:  # Devuelve cualquier stock reservado si lo había
                    self.producto.cantidad_en_stock += self.cantidad_temp
                    self.producto.save()
                self.cantidad_temp = 0
                self.save()
                return False  # No válido (sin stock)
        
        # Si cantidad_prod es <= stock disponible, es válido.
        # Asegurarse que cantidad_temp sea igual a cantidad_prod y no esté expirado.
        if self.cantidad_temp != self.cantidad_prod or self.expirado:
            self.cantidad_temp = self.cantidad_prod
            self.expirado = False

    def expiracion(self):
        """
        Verifica si el carrito ha expirado por inactividad (ej. 180 segundos)
        y devuelve el stock al producto si expira.
        
        Returns:
            bool: True si el carrito ha expirado, False si aún es válido
            
        Lógica:
        - Verifica si ya está marcado como expirado
        - Calcula el tiempo de inactividad desde la última actualización
        - Marca como expirado si supera el tiempo límite
        - Libera el stock reservado si expira
        """
        # Si ya está expirado, no hacer nada
        if self.expirado:
            return True  # Ya está expirado

        # Definir el tiempo de inactividad permitido (180 segundos = 3 minutos)
        tiempo_inactividad_permitida = timedelta(seconds=180) 
        
        # Comprobar si ha pasado el tiempo de inactividad desde la última actualización
        if (timezone.now() - self.fecha_actualizacion) > tiempo_inactividad_permitida:
            # Si el carrito ha estado inactivo por más del tiempo permitido
            self.expirado = True
            
            # Devolver el stock reservado al producto
            if self.cantidad_temp > 0:
                # Nota: Comentado para evitar problemas de concurrencia
                # self.producto.cantidad_en_stock += self.cantidad_temp
                self.producto.save()
                self.cantidad_temp = 0  # Resetear cantidad temporal después de devolver stock

            self.save()  # Guardar la instancia de CarritoTemp para marcarla como expirada
            return True  # Ha expirado
            
        return False  # No ha expirado por tiempo

    @classmethod
    def verificar_expiracion_carrito(cls, usuario):
        """
        Verifica la expiración y stock de todos los productos en el carrito de un usuario.
        
        Args:
            usuario: Instancia del usuario cuyo carrito se va a verificar
            
        Returns:
            list: Lista de diccionarios con información de productos expirados o ajustados
            
        Lógica:
        - Obtiene todos los carritos del usuario
        - Verifica stock disponible para cada producto
        - Verifica expiración por tiempo de inactividad
        - Retorna lista con cambios realizados
        """
        carritos_actuales = cls.objects.filter(usuario=usuario)
        productos_expirados_o_ajustados = []
        
        for carrito_item in carritos_actuales:
            # Guardar valores originales para comparación
            original_cantidad_prod = carrito_item.cantidad_prod
            original_expirado = carrito_item.expirado

            # Primero, verificar y ajustar el stock
            is_valid_after_stock_check = carrito_item.verificar_carrito()
            
            # Si después de verificar stock, no es válido (ej. producto eliminado o sin stock)
            if not is_valid_after_stock_check:
                productos_expirados_o_ajustados.append({
                    'id': carrito_item.id,
                    'producto_id': carrito_item.producto.id if carrito_item.producto else None,
                    'cantidad_original': original_cantidad_prod,
                    'cantidad_actual': carrito_item.cantidad_prod,
                    'motivo': 'sin_stock_o_producto_no_existe'
                })
                continue  # Pasar al siguiente item si ya se manejó

            # Luego, verificar la expiración por inactividad
            if carrito_item.expiracion():
                productos_expirados_o_ajustados.append({
                    'id': carrito_item.id,
                    'producto_id': carrito_item.producto.id,
                    'cantidad_original': original_cantidad_prod,
                    'cantidad_actual': carrito_item.cantidad_prod,
                    'motivo': 'expirado_por_tiempo'
                })
            elif original_cantidad_prod != carrito_item.cantidad_prod:
                 # Si la cantidad cambió debido a stock, reportarlo
                 productos_expirados_o_ajustados.append({
                    'id': carrito_item.id,
                    'producto_id': carrito_item.producto.id,
                    'cantidad_original': original_cantidad_prod,
                    'cantidad_actual': carrito_item.cantidad_prod,
                    'motivo': 'cantidad_ajustada_por_stock'
                })

        return productos_expirados_o_ajustados