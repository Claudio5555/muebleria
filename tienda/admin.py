from django.contrib import admin
from .models import (
    Categorias, Muebles, Usuarios, Clientes,
    Ventas, DetallesVentas, Proveedor, Compras,
    Materiales, DetalleCompra
)   
from .admin_forms import (
    CategoriasAdminForm, MueblesAdminForm, UsuariosAdminForm,
    ClientesAdminForm, VentasAdminForm, DetallesVentasAdminForm,
    ProveedorAdminForm, ComprasAdminForm, MaterialesAdminForm,
    DetalleCompraAdminForm,
)


@admin.register(Categorias)
class CategoriasAdmin(admin.ModelAdmin):
    form = CategoriasAdminForm
    list_display = ('id_categoria', 'nombre_categoria')


@admin.register(Muebles)
class MueblesAdmin(admin.ModelAdmin):
    form = MueblesAdminForm
    list_display = ('id_muebles', 'nombre', 'precio', 'stock', 'id_categoria')
    list_filter = ('id_categoria',)
    search_fields = ('nombre', 'descripcion')


@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    form = UsuariosAdminForm
    list_display = ('id_usuario', 'nombre', 'apellido', 'usuario', 'rol', 'eliminado')
    list_filter = ('rol', 'eliminado')
    search_fields = ('nombre', 'apellido', 'usuario')


@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    form = ClientesAdminForm
    list_display = ('id_cliente', 'nombre', 'apellido', 'telefono', 'correo')
    search_fields = ('nombre', 'apellido', 'correo')


@admin.register(Ventas)
class VentasAdmin(admin.ModelAdmin):
    form = VentasAdminForm
    list_display = ('id_venta', 'fecha', 'id_cliente', 'id_usuario', 'total')


@admin.register(DetallesVentas)
class DetallesVentasAdmin(admin.ModelAdmin):
    form = DetallesVentasAdminForm
    list_display = ('id_deventas', 'id_ventas', 'id_muebles', 'cantidad', 'precio_unitario')


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    form = ProveedorAdminForm
    list_display = ('id_proveedores', 'nombre', 'telefono', 'correo')
    search_fields = ('nombre',)


@admin.register(Compras)
class ComprasAdmin(admin.ModelAdmin):
    form = ComprasAdminForm
    list_display = ('id_compra', 'fecha', 'id_proveedor', 'id_usuario')


@admin.register(Materiales)
class MaterialesAdmin(admin.ModelAdmin):
    form = MaterialesAdminForm
    list_display = ('id_materiales', 'nombre', 'tipo', 'stock', 'unidad_medida')
    search_fields = ('nombre',)


@admin.register(DetalleCompra)
class DetalleCompraAdmin(admin.ModelAdmin):
    form = DetalleCompraAdminForm
    list_display = ('id_decompras', 'id_compra', 'id_material', 'cantidad', 'precio_unitario')
