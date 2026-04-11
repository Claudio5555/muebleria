from django.db import models
from django.core.validators import MinValueValidator, RegexValidator, EmailValidator


# Validador reutilizable para teléfonos
phone_validator = RegexValidator(
    regex=r'^[0-9+\-\s()]+$',
    message='El teléfono solo puede contener números, +, -, espacios y paréntesis.'
)


class Categorias(models.Model):
    id_categoria = models.AutoField(primary_key=True, db_column='ID_Categoria')
    nombre_categoria = models.CharField(
        max_length=100, unique=True, db_column='Nombre_categoria'
    )

    class Meta:
        db_table = 'Categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre_categoria


class Muebles(models.Model):
    id_muebles = models.AutoField(primary_key=True, db_column='ID_muebles')
    nombre = models.CharField(max_length=200, db_column='Nombre')
    descripcion = models.TextField(blank=True, null=True, db_column='Descripcion')
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, db_column='Precio',
        validators=[MinValueValidator(0.01, message='El precio debe ser mayor a 0.')]
    )
    stock = models.IntegerField(
        default=0, db_column='Stock',
        validators=[MinValueValidator(0, message='El stock no puede ser negativo.')]
    )
    id_categoria = models.ForeignKey(
        Categorias, on_delete=models.CASCADE,
        db_column='ID_Categoria', related_name='muebles'
    )
    imagen = models.ImageField(upload_to='muebles/', blank=True, null=True)

    class Meta:
        db_table = 'Muebles'
        verbose_name = 'Mueble'
        verbose_name_plural = 'Muebles'

    def __str__(self):
        return self.nombre


class Usuarios(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('vendedor', 'Vendedor'),
        ('cliente', 'Cliente'),
    ]
    id_usuario = models.AutoField(primary_key=True, db_column='ID_Usuario')
    nombre = models.CharField(max_length=100, db_column='Nombre')
    apellido = models.CharField(max_length=100, db_column='Apellido')
    usuario = models.CharField(max_length=100, unique=True, db_column='Usuario')
    contrasenia = models.CharField(max_length=255, db_column='Contrasenia')
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='cliente', db_column='Rol')
    eliminado = models.BooleanField(default=False, db_column='Eliminado')

    class Meta:
        db_table = 'Usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Clientes(models.Model):
    id_cliente = models.AutoField(primary_key=True, db_column='ID_Cliente')
    nombre = models.CharField(max_length=100, db_column='Nombre')
    apellido = models.CharField(max_length=100, db_column='Apellido')
    telefono = models.CharField(
        max_length=20, blank=True, null=True, db_column='Telefono',
        validators=[phone_validator]
    )
    dirreccion = models.CharField(max_length=255, blank=True, null=True, db_column='Dirreccion')
    correo = models.EmailField(
        max_length=100, blank=True, null=True, db_column='Correo'
    )

    class Meta:
        db_table = 'Clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Ventas(models.Model):
    id_venta = models.AutoField(primary_key=True, db_column='ID_Venta')
    fecha = models.DateTimeField(auto_now_add=True, db_column='Fecha')
    id_cliente = models.ForeignKey(
        Clientes, on_delete=models.CASCADE,
        db_column='ID_Cliente', related_name='ventas'
    )
    id_usuario = models.ForeignKey(
        Usuarios, on_delete=models.CASCADE,
        db_column='ID_Usuario', related_name='ventas'
    )
    total = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, db_column='Total',
        validators=[MinValueValidator(0, message='El total no puede ser negativo.')]
    )

    class Meta:
        db_table = 'Ventas'
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f"Venta #{self.id_venta}"


class DetallesVentas(models.Model):
    id_deventas = models.AutoField(primary_key=True, db_column='ID_DeVentas')
    id_ventas = models.ForeignKey(
        Ventas, on_delete=models.CASCADE,
        db_column='ID_Ventas', related_name='detalles'
    )
    id_muebles = models.ForeignKey(
        Muebles, on_delete=models.CASCADE,
        db_column='ID_Muebles', related_name='detalles_ventas'
    )
    cantidad = models.IntegerField(
        db_column='Cantidad',
        validators=[MinValueValidator(1, message='La cantidad debe ser al menos 1.')]
    )
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, db_column='Precio_unitario',
        validators=[MinValueValidator(0.01, message='El precio unitario debe ser mayor a 0.')]
    )

    class Meta:
        db_table = 'Detalles_ventas'
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Ventas'

    def __str__(self):
        return f"Detalle #{self.id_deventas} - Venta #{self.id_ventas_id}"


class Proveedor(models.Model):
    id_proveedores = models.AutoField(primary_key=True, db_column='ID_Proveedores')
    nombre = models.CharField(max_length=100, db_column='Nombre')
    telefono = models.CharField(
        max_length=20, blank=True, null=True, db_column='Telefono',
        validators=[phone_validator]
    )
    direccion = models.CharField(max_length=255, blank=True, null=True, db_column='Direccion')
    correo = models.EmailField(
        max_length=100, blank=True, null=True, db_column='Correo'
    )

    class Meta:
        db_table = 'Proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre


class Compras(models.Model):
    id_compra = models.AutoField(primary_key=True, db_column='ID_Compra')
    fecha = models.DateTimeField(auto_now_add=True, db_column='Fecha')
    id_proveedor = models.ForeignKey(
        Proveedor, on_delete=models.CASCADE,
        db_column='ID_Proveedor', related_name='compras'
    )
    id_usuario = models.ForeignKey(
        Usuarios, on_delete=models.CASCADE,
        db_column='ID_Usuario', related_name='compras'
    )

    class Meta:
        db_table = 'Compras'
        verbose_name = 'Compra'
        verbose_name_plural = 'Compras'

    def __str__(self):
        return f"Compra #{self.id_compra}"


class Materiales(models.Model):
    id_materiales = models.AutoField(primary_key=True, db_column='ID_Materiales')
    nombre = models.CharField(max_length=100, db_column='Nombre')
    tipo = models.CharField(max_length=100, blank=True, null=True, db_column='Tipo')
    stock = models.IntegerField(
        default=0, db_column='Stock',
        validators=[MinValueValidator(0, message='El stock no puede ser negativo.')]
    )
    unidad_medida = models.CharField(max_length=50, blank=True, null=True, db_column='Unidad_medida')

    class Meta:
        db_table = 'Materiales'
        verbose_name = 'Material'
        verbose_name_plural = 'Materiales'

    def __str__(self):
        return self.nombre


class DetalleCompra(models.Model):
    id_decompras = models.AutoField(primary_key=True, db_column='ID_DeCompras')
    id_compra = models.ForeignKey(
        Compras, on_delete=models.CASCADE,
        db_column='ID_Compra', related_name='detalles'
    )
    id_material = models.ForeignKey(
        Materiales, on_delete=models.CASCADE,
        db_column='ID_Material', related_name='detalles_compra'
    )
    cantidad = models.IntegerField(
        db_column='Cantidad',
        validators=[MinValueValidator(1, message='La cantidad debe ser al menos 1.')]
    )
    precio_unitario = models.DecimalField(
        max_digits=10, decimal_places=2, db_column='Precio_unitario',
        validators=[MinValueValidator(0.01, message='El precio unitario debe ser mayor a 0.')]
    )

    class Meta:
        db_table = 'Detalle_Compra'
        verbose_name = 'Detalle de Compra'
        verbose_name_plural = 'Detalles de Compra'

    def __str__(self):
        return f"Detalle #{self.id_decompras} - Compra #{self.id_compra_id}"
