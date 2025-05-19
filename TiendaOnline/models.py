from django.db import models

class Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(
        max_length=255,
        verbose_name='Nombre del Producto',
        help_text='El nombre del producto'
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio del Producto',
        help_text='El precio del producto'
    )
    cantidad_en_stock = models.IntegerField(
        verbose_name='Cantidad en Stock',
        help_text='Cantidad disponible en inventario'
    )
    descripcion = models.TextField(
        verbose_name='Descripción del Producto',
        help_text='Descripción detallada del producto',
        blank=True,
        null=True
    )
    imagen_base64 = models.TextField(
        verbose_name='Imagen en Base64',
        help_text='Imagen del producto codificada en Base64',
        blank=True,
        null=True
    )
    categoria = models.CharField(
        max_length=3,
        choices=[('M', 'Mujeres'), ('H', 'Hombres')],
        verbose_name='Categoria',
        help_text='Tamaño del producto',
        blank=True,
        null=True
    )
    tamaño = models.CharField(
        max_length=3,
        choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL')],
        verbose_name='Tamaño',
        help_text='Tamaño del producto',
        blank=True,
        null=True
    )
    colores = models.TextField(        
        verbose_name='Color Hexadecimal',
        help_text='Color en formato hexadecimal (ej. #FF0000)',
        default='#FFFFFF',        
        null=False,
    )

    def formatted_price(self):
        return f"${self.precio:.2f}"

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    ESTADO_CHOICES = [
        ('Pagado', 'Pagado'),
        ('En Camino', 'En Camino'),
        ('Recibido', 'Recibido')
    ]

    id_pedido = models.AutoField(primary_key=True)
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        verbose_name='Producto',
        help_text='Producto asociado al pedido'
    )
    nombre_cliente = models.CharField(
        max_length=255,
        verbose_name='Nombre del Cliente',
        help_text='El nombre del cliente que realizó el pedido'
    )
    apellido_cliente = models.CharField(
        max_length=255,
        verbose_name='Apellido del Cliente',
        help_text='El apellido del cliente que realizó el pedido',
        null=True,
        blank=True
    )
    cantidad = models.IntegerField(
        verbose_name='Cantidad de productos',
        help_text='Cantidad de productos que se compraron',
        default=0
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Subtotal',
        help_text='Subtotal del pedido'
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Total',
        help_text='Total del pedido'
    )
    isv = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.15,
        verbose_name='ISV',
        help_text='Impuesto sobre ventas'
    )
    compañia = models.CharField(
        max_length=255,
        verbose_name='Compañia',
        help_text='Compañia a entregar',
        blank=True,
        null=True
    )
    direccion = models.CharField(
        max_length=255,
        verbose_name='Dirección',
        help_text='Dirección de entrega',
        blank=True,
        null=True
    )
    pais = models.CharField(
        max_length=255,
        verbose_name='Pais',
        help_text='Pais de entrega',
        blank=True,
        null=True
    )
    estado_pais = models.CharField(
        max_length=255,
        verbose_name='Estado',
        help_text='Estado del pais de entregas',
        blank=True,
        null=True
    )
    ciudad = models.CharField(
        max_length=255,
        verbose_name='Ciudad',
        help_text='Ciudad de entrega',
        blank=True,
        null=True
    )
    zip = models.CharField(
        max_length=255,
        verbose_name='codigo postal',
        help_text='Codigo Postal de entrega',
        blank=True,
        null=True
    )
    correo = models.EmailField(
        verbose_name='Correo Electrónico',
        help_text='Correo electrónico del cliente',
        blank=True,
        null=True
    )
    telefono = models.CharField(
        max_length=20,
        verbose_name='Teléfono',
        help_text='Teléfono del cliente',
        blank=True,
        null=True
    )
    estado = models.CharField(
        max_length=50,
        choices=ESTADO_CHOICES,
        verbose_name='Estado del Pedido',
        help_text='Estado actual del pedido',
        default='Pagado',
    )
    descripcion_adicional = models.TextField(
        verbose_name='Descripción Adicional',
        help_text='Información adicional sobre el pedido',
        blank=True,
        null=True
    )
    fecha_compra = models.DateField(
        verbose_name='Fecha de Compra',
        help_text='Fecha en que se realizó el pedido'
    )
    fecha_entrega = models.DateField(
        verbose_name='Fecha de Entrega',
        help_text='Fecha estimada de entrega',
        blank=True,
        null=True
    )

    def formatted_subtotal(self):
        return f"${self.subtotal:.2f}"

    def formatted_total(self):
        return f"${self.total:.2f}"

    def get_nombre_producto(self):
        return self.producto.nombre if self.producto else "Producto no especificado"

    def __str__(self):
        return f"Pedido #{self.id_pedido} - {self.nombre_cliente} - {self.get_nombre_producto()}"
    