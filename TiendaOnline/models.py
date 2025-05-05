from django.db import models

class Producto(models.Model):
    id = models.AutoField(primary_key=True)  # Campo ID explícito
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
    imagen = models.ImageField(
        upload_to='productos/',
        verbose_name='Imagen del Producto',
        help_text='Imagen del producto',
        blank=True,
        null=True
    )

    def __str__(self):
        return self.nombre


class Pedido(models.Model):
    id = models.AutoField(primary_key=True)  # Campo ID explícito
    nombre_cliente = models.CharField(
        max_length=255,
        verbose_name='Nombre del Cliente',
        help_text='El nombre del cliente que realizó el pedido'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        verbose_name='Producto',
        help_text='El producto asociado al pedido'
    )
    cantidad = models.IntegerField(
        verbose_name='Cantidad',
        help_text='Cantidad de productos en el pedido'
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
    direccion = models.CharField(
        max_length=255,
        verbose_name='Dirección',
        help_text='Dirección de entrega',
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
        verbose_name='Estado del Pedido',
        help_text='Estado actual del pedido'
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

    def __str__(self):
        return f"Pedido de {self.nombre_cliente} - {self.producto.nombre}"