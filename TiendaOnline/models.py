from django.db import models
from django.core.validators import MinValueValidator, RegexValidator
from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.core.exceptions import ValidationError
from decimal import Decimal

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El Email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)
    
    class Meta:
        verbose_name = 'País con ISV'
        verbose_name_plural = 'Países con ISV'
    
    def __str__(self):
        return f"{self.pais} (Envío: ${self.costo_envio_pais})"


##USUARIO
#se usa abstract para cuando se utiliza el email como login,campos_adicionales,etc
class Usuario(AbstractUser):
    """Modelo extendido de usuario con todos los campos requeridos"""
    id = models.AutoField(primary_key=True)

    username = None  # Deshabilitamos el campo username
    email = models.EmailField(
        verbose_name='Correo Electrónico',
        unique=True,
        null=False
    )
    
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

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name="tienda_usuario_set",  # Nombre único
        related_query_name="tienda_usuario",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="tienda_usuario_set",  # Nombre único
        related_query_name="tienda_usuario",
    )

    objects = UsuarioManager()  # Usamos nuestro manager personalizado

    # Campos de autenticación
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nombre_cliente', 'apellido_cliente']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre_cliente} {self.apellido_cliente} ({self.email})"

    ###Productos

class Producto(models.Model):
    """Modelo para productos con color hexadecimal único"""
    CATEGORIA_CHOICES = [
        ('M', 'Mujeres'),
        ('H', 'Hombres'),
        ('U', 'Unisex')
    ]
    
    TAMANO_CHOICES = [
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
        ('XXL', 'XXL')
    ]
    
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
        validators=[MinValueValidator(0.01)],
        null=False
    )
    cantidad_en_stock = models.PositiveIntegerField(
        verbose_name='Stock',
        help_text='Cantidad disponible en inventario',
        validators=[MinValueValidator(0)],
        null=False
    )
    desc_prod = models.TextField(
        verbose_name='Descripción del Producto',
        blank=True,
        null=True
    )
    image = models.TextField(
        verbose_name='Imagen en Base64',
        help_text='Imagen del producto codificada en Base64',
        blank=True,
        null=True
    )
    categoria = models.CharField(
        max_length=3,
        choices=CATEGORIA_CHOICES,
        verbose_name='Categoría',
        null=False
    )
    tamaño  = models.CharField(
        max_length=3,
        choices=TAMANO_CHOICES,
        verbose_name='Tamaño',
        help_text='Tamaño del producto',
        blank=True,
        null=True
    )
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

    ###Pedido

class Pedido(models.Model):
    """Modelo para pedidos con relación a usuario y país ISV"""
    ESTADO_CHOICES = [
        ('Pagado', 'Pagado'),
        ('En Camino', 'En Camino'),
        ('Recibido', 'Recibido'),
        ('Cancelado', 'Cancelado')
    ]
    
    id_pedido = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='pedidos',
        verbose_name='Usuario',
        null=True,  # Temporalmente permitimos nulos
        blank=True  # Temporalmente permitimos en blanco
    )
    company = models.CharField(
        max_length=255,
        verbose_name='Compañía',
        blank=True,
        null=True
    )
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
    correo = models.EmailField(
        verbose_name='Correo Electrónico',
        null=False
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name='Teléfono',
        null=False
    )
    estado_compra = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='Pagado',
        verbose_name='Estado del Pedido'        
    )
    desc_adicional = models.TextField(
        verbose_name='Descripción Adicional',
        blank=True,
        null=True
    )
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
    es_movimiento_interno = models.BooleanField(
        default=False,
        verbose_name='Movimiento interno (no comercial)')
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-fecha_compra']
    
    def save(self, *args, **kwargs):
        """Autocompleta datos del usuario si no se especifican"""
        if not self.pk:  # Solo para nuevos pedidos
            if not all([self.direccion, self.ciudad, self.zip, self.telefono, self.correo]):
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
        """Calcula el total sumando todos los detalles"""
        return sum(detalle.total for detalle in self.detalles.all())
    
    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.usuario.nombre_cliente}"


##PEDIDO DETALLE

class PedidoDetalle(models.Model):
    """Modelo para detalles de pedido con cálculos automáticos"""
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name='Pedido',
        null=False
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        verbose_name='Producto',
        null=False
    )
    cantidad_prod = models.PositiveIntegerField(
        verbose_name='Cantidad',
        validators=[MinValueValidator(1)],
        null=False
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=False
    )
    isv = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='ISV',
        validators=[MinValueValidator(0)],
        null=False
    )
    envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Envío',
        validators=[MinValueValidator(0)],
        null=False
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=False
    )
    
    class Meta:
        verbose_name = 'Detalle de Pedido'
        verbose_name_plural = 'Detalles de Pedido'
    
    def save(self, *args, **kwargs):
        """Calcula automáticamente los valores antes de guardar"""
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
            self.isv = self.subtotal * Decimal('0.15')
            
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
    
    ##Nuevo manejo de stock con tabla de registros temporal

class CarritoTemp(models.Model):
    """Modelo para el carrito temporal de compras con gestión de stock reservado"""
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='carritos_temp',
        verbose_name='Usuario',
        null=False
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='carritos_temp',
        verbose_name='Producto',
        null=False
    )
    cantidad_prod = models.PositiveIntegerField(
        verbose_name='Cantidad en Carrito',
        validators=[MinValueValidator(1)],
        null=False,
        default=1
    )
    cantidad_temp = models.PositiveIntegerField(
        verbose_name='Cantidad Temporal (reservado)',
        validators=[MinValueValidator(1)],
        null=False,
        default=1
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación',
        null=True,
        blank=True,

    )
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de última actualización',
        null=True,
        blank=True,
    )
    limite_compra = models.PositiveIntegerField(
        verbose_name='Límite de compra por usuario',
        default=10,
        help_text='Cantidad máxima que un usuario puede comprar de este producto'
    )

    class Meta:
        verbose_name = 'Carrito Temporal'
        verbose_name_plural = 'Carritos Temporales'
        unique_together = ['usuario', 'producto']
        ordering = ['-fecha_actualizacion']

    def __str__(self):
        return f"Carrito de {self.usuario.nombre_cliente} - {self.producto.nombre} ({self.cantidad_prod})"

    def clean(self):
        """Validaciones adicionales"""
        # Validar que no exceda el stock disponible
        if self.cantidad_prod > self.producto.cantidad_en_stock:
            raise ValidationError('La cantidad excede el stock disponible')
        
        # Validar que no exceda el límite de compra
        if self.cantidad_prod > self.limite_compra:
            raise ValidationError(f'No puede comprar más de {self.limite_compra} unidades de este producto')

    def save(self, *args, **kwargs):
        """Lógica al guardar el item del carrito"""
        # Si es un nuevo registro, reservar el stock temporalmente
        if not self.pk:
            self.cantidad_temp = self.cantidad_prod
            self.producto.cantidad_en_stock -= self.cantidad_temp
            self.producto.save()
        
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Lógica al eliminar el item del carrito"""
        # Liberar el stock reservado al eliminar
        self.producto.cantidad_en_stock += self.cantidad_temp
        self.producto.save()
        super().delete(*args, **kwargs)

    @classmethod
    def liberar_stock_expirado(cls, minutos_expiracion=5):
        """Método para liberar stock de carritos no actualizados"""
        from django.utils import timezone
        from datetime import timedelta
        
        limite_tiempo = timezone.now() - timedelta(minutes=minutos_expiracion)
        carritos_expirados = cls.objects.filter(fecha_actualizacion__lt=limite_tiempo)
        
        for carrito in carritos_expirados:
            carrito.producto.cantidad_en_stock += carrito.cantidad_temp
            carrito.producto.save()
            carrito.delete()

    @classmethod
    def verificar_stock_disponible(cls, usuario):
        """Verifica el stock disponible para los productos en el carrito del usuario"""
        carritos = cls.objects.filter(usuario=usuario)
        productos_sin_stock = []
        
        for carrito in carritos:
            # Si no hay suficiente stock, ajustar cantidades
            if carrito.producto.cantidad_en_stock < carrito.cantidad_prod:
                if carrito.producto.cantidad_en_stock <= 0:
                    productos_sin_stock.append(carrito.producto.nombre)
                    carrito.delete()
                else:
                    # Ajustar a la cantidad disponible
                    carrito.cantidad_prod = carrito.producto.cantidad_en_stock
                    carrito.cantidad_temp = carrito.cantidad_prod
                    carrito.save()
        
        return productos_sin_stock