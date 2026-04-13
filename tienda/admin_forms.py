"""
Formularios de validación para el panel de administración de Django.
Cada ModelForm aplica validaciones que se ejecutan al crear/editar
registros desde el admin.
"""

import re
from django import forms
from django.core.exceptions import ValidationError
from .models import (
    Categorias, Muebles, Usuarios, Clientes,
    Ventas, DetallesVentas, Proveedor, Compras,
    Materiales, DetalleCompra
)


# ─────────────────────────────────────────────
# Helpers de validación reutilizables
# ─────────────────────────────────────────────

def validar_solo_letras(valor, campo_nombre):
    """Valida que un campo solo contenga letras, espacios y acentos."""
    if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$', valor.strip()):
        raise ValidationError(
            f'El {campo_nombre} solo puede contener letras y espacios.'
        )


def validar_telefono(valor):
    """Valida formato de teléfono."""
    if valor and not re.match(r'^[0-9+\-\s()]+$', valor.strip()):
        raise ValidationError(
            'El teléfono solo puede contener números, +, -, espacios y paréntesis.'
        )
    if valor and len(re.sub(r'[^0-9]', '', valor)) < 7:
        raise ValidationError(
            'El teléfono debe tener al menos 7 dígitos.'
        )


def validar_no_solo_espacios(valor, campo_nombre):
    """Valida que el campo no esté compuesto solo de espacios."""
    if valor and not valor.strip():
        raise ValidationError(
            f'El {campo_nombre} no puede estar compuesto solo de espacios.'
        )


# ─────────────────────────────────────────────
# Formulario: Categorías
# ─────────────────────────────────────────────

class CategoriasAdminForm(forms.ModelForm):
    class Meta:
        model = Categorias
        fields = '__all__'

    def clean_nombre_categoria(self):
        nombre = self.cleaned_data.get('nombre_categoria', '').strip()
        if not nombre:
            raise ValidationError('El nombre de la categoría es obligatorio.')
        if len(nombre) < 2:
            raise ValidationError(
                'El nombre de la categoría debe tener al menos 2 caracteres.'
            )
        validar_solo_letras(nombre, 'nombre de la categoría')
        # Verificar duplicados (case-insensitive) excluyendo el registro actual
        qs = Categorias.objects.filter(nombre_categoria__iexact=nombre)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ya existe una categoría con este nombre.')
        return nombre


# ─────────────────────────────────────────────
# Formulario: Muebles
# ─────────────────────────────────────────────

class MueblesAdminForm(forms.ModelForm):
    class Meta:
        model = Muebles
        fields = '__all__'

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise ValidationError('El nombre del mueble es obligatorio.')
        if len(nombre) < 2:
            raise ValidationError(
                'El nombre del mueble debe tener al menos 2 caracteres.'
            )
        validar_no_solo_espacios(nombre, 'nombre')
        return nombre

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is None:
            raise ValidationError('El precio es obligatorio.')
        if precio <= 0:
            raise ValidationError('El precio debe ser mayor a 0.')
        if precio > 999999.99:
            raise ValidationError(
                'El precio no puede exceder 999,999.99.'
            )
        return precio

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None:
            raise ValidationError('El stock es obligatorio.')
        if stock < 0:
            raise ValidationError('El stock no puede ser negativo.')
        if stock > 99999:
            raise ValidationError(
                'El stock no puede exceder 99,999 unidades.'
            )
        return stock

    def clean_id_categoria(self):
        categoria = self.cleaned_data.get('id_categoria')
        if not categoria:
            raise ValidationError('Debe seleccionar una categoría.')
        return categoria


# ─────────────────────────────────────────────
# Formulario: Usuarios
# ─────────────────────────────────────────────

class UsuariosAdminForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        fields = '__all__'

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise ValidationError('El nombre es obligatorio.')
        if len(nombre) < 2:
            raise ValidationError(
                'El nombre debe tener al menos 2 caracteres.'
            )
        validar_solo_letras(nombre, 'nombre')
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido', '').strip()
        if not apellido:
            raise ValidationError('El apellido es obligatorio.')
        if len(apellido) < 2:
            raise ValidationError(
                'El apellido debe tener al menos 2 caracteres.'
            )
        validar_solo_letras(apellido, 'apellido')
        return apellido

    def clean_usuario(self):
        usuario = self.cleaned_data.get('usuario', '').strip()
        if not usuario:
            raise ValidationError('El nombre de usuario es obligatorio.')
        if len(usuario) < 4:
            raise ValidationError(
                'El nombre de usuario debe tener al menos 4 caracteres.'
            )
        if not re.match(r'^[a-zA-Z0-9_-]+$', usuario):
            raise ValidationError(
                'El nombre de usuario solo puede contener letras, números, '
                'guiones (-) y guiones bajos (_).'
            )
        # Verificar duplicados excluyendo el registro actual
        qs = Usuarios.objects.filter(usuario__iexact=usuario)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Este nombre de usuario ya está en uso.')
        return usuario

    def clean_contrasenia(self):
        contrasenia = self.cleaned_data.get('contrasenia', '')
        if not contrasenia:
            raise ValidationError('La contraseña es obligatoria.')
        if len(contrasenia) < 8:
            raise ValidationError(
                'La contraseña debe tener al menos 8 caracteres.'
            )
        if not re.search(r'[A-Z]', contrasenia):
            raise ValidationError(
                'La contraseña debe contener al menos una letra mayúscula.'
            )
        if not re.search(r'[a-z]', contrasenia):
            raise ValidationError(
                'La contraseña debe contener al menos una letra minúscula.'
            )
        if not re.search(r'[0-9]', contrasenia):
            raise ValidationError(
                'La contraseña debe contener al menos un número.'
            )
        return contrasenia

    def clean_rol(self):
        rol = self.cleaned_data.get('rol')
        if not rol:
            raise ValidationError('Debe seleccionar un rol.')
        roles_validos = [choice[0] for choice in Usuarios.ROL_CHOICES]
        if rol not in roles_validos:
            raise ValidationError(
                f'Rol inválido. Opciones válidas: {", ".join(roles_validos)}.'
            )
        return rol


# ─────────────────────────────────────────────
# Formulario: Clientes
# ─────────────────────────────────────────────

class ClientesAdminForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = '__all__'

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise ValidationError('El nombre es obligatorio.')
        if len(nombre) < 2:
            raise ValidationError(
                'El nombre debe tener al menos 2 caracteres.'
            )
        validar_solo_letras(nombre, 'nombre')
        return nombre

    def clean_apellido(self):
        apellido = self.cleaned_data.get('apellido', '').strip()
        if not apellido:
            raise ValidationError('El apellido es obligatorio.')
        if len(apellido) < 2:
            raise ValidationError(
                'El apellido debe tener al menos 2 caracteres.'
            )
        validar_solo_letras(apellido, 'apellido')
        return apellido

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        if telefono:
            validar_telefono(telefono)
        return telefono

    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '')
        if correo:
            correo = correo.strip().lower()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
                raise ValidationError('Ingrese un correo electrónico válido.')
        return correo

    def clean_dirreccion(self):
        dirreccion = self.cleaned_data.get('dirreccion', '')
        if dirreccion:
            validar_no_solo_espacios(dirreccion, 'dirección')
            if len(dirreccion.strip()) < 5:
                raise ValidationError(
                    'La dirección debe tener al menos 5 caracteres.'
                )
        return dirreccion


# ─────────────────────────────────────────────
# Formulario: Ventas
# ─────────────────────────────────────────────

class VentasAdminForm(forms.ModelForm):
    class Meta:
        model = Ventas
        fields = '__all__'

    def clean_total(self):
        total = self.cleaned_data.get('total')
        if total is not None and total < 0:
            raise ValidationError('El total de la venta no puede ser negativo.')
        return total

    def clean_id_cliente(self):
        cliente = self.cleaned_data.get('id_cliente')
        if not cliente:
            raise ValidationError('Debe seleccionar un cliente.')
        return cliente

    def clean_id_usuario(self):
        usuario = self.cleaned_data.get('id_usuario')
        if not usuario:
            raise ValidationError('Debe seleccionar un usuario/vendedor.')
        # Verificar que el usuario no esté eliminado
        if usuario and usuario.eliminado:
            raise ValidationError(
                'No se puede asignar una venta a un usuario eliminado.'
            )
        return usuario


# ─────────────────────────────────────────────
# Formulario: Detalles de Ventas
# ─────────────────────────────────────────────

class DetallesVentasAdminForm(forms.ModelForm):
    class Meta:
        model = DetallesVentas
        fields = '__all__'

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None:
            raise ValidationError('La cantidad es obligatoria.')
        if cantidad < 1:
            raise ValidationError('La cantidad debe ser al menos 1.')
        if cantidad > 9999:
            raise ValidationError('La cantidad no puede exceder 9,999.')
        return cantidad

    def clean_precio_unitario(self):
        precio = self.cleaned_data.get('precio_unitario')
        if precio is None:
            raise ValidationError('El precio unitario es obligatorio.')
        if precio <= 0:
            raise ValidationError('El precio unitario debe ser mayor a 0.')
        return precio

    def clean(self):
        cleaned_data = super().clean()
        mueble = cleaned_data.get('id_muebles')
        cantidad = cleaned_data.get('cantidad')
        # Verificar que hay suficiente stock
        if mueble and cantidad:
            if cantidad > mueble.stock:
                raise ValidationError(
                    f'Stock insuficiente para "{mueble.nombre}". '
                    f'Stock disponible: {mueble.stock}, '
                    f'cantidad solicitada: {cantidad}.'
                )
        return cleaned_data


# ─────────────────────────────────────────────
# Formulario: Proveedor
# ─────────────────────────────────────────────

class ProveedorAdminForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = '__all__'

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise ValidationError('El nombre del proveedor es obligatorio.')
        if len(nombre) < 2:
            raise ValidationError(
                'El nombre del proveedor debe tener al menos 2 caracteres.'
            )
        validar_no_solo_espacios(nombre, 'nombre')
        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '')
        if telefono:
            validar_telefono(telefono)
        return telefono

    def clean_correo(self):
        correo = self.cleaned_data.get('correo', '')
        if correo:
            correo = correo.strip().lower()
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
                raise ValidationError('Ingrese un correo electrónico válido.')
        return correo

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion', '')
        if direccion:
            validar_no_solo_espacios(direccion, 'dirección')
            if len(direccion.strip()) < 5:
                raise ValidationError(
                    'La dirección debe tener al menos 5 caracteres.'
                )
        return direccion


# ─────────────────────────────────────────────
# Formulario: Compras
# ─────────────────────────────────────────────

class ComprasAdminForm(forms.ModelForm):
    class Meta:
        model = Compras
        fields = '__all__'

    def clean_id_proveedor(self):
        proveedor = self.cleaned_data.get('id_proveedor')
        if not proveedor:
            raise ValidationError('Debe seleccionar un proveedor.')
        return proveedor

    def clean_id_usuario(self):
        usuario = self.cleaned_data.get('id_usuario')
        if not usuario:
            raise ValidationError('Debe seleccionar un usuario.')
        if usuario and usuario.eliminado:
            raise ValidationError(
                'No se puede asignar una compra a un usuario eliminado.'
            )
        return usuario


# ─────────────────────────────────────────────
# Formulario: Materiales
# ─────────────────────────────────────────────

class MaterialesAdminForm(forms.ModelForm):
    class Meta:
        model = Materiales
        fields = '__all__'

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if not nombre:
            raise ValidationError('El nombre del material es obligatorio.')
        if len(nombre) < 2:
            raise ValidationError(
                'El nombre del material debe tener al menos 2 caracteres.'
            )
        validar_no_solo_espacios(nombre, 'nombre')
        return nombre

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is None:
            raise ValidationError('El stock es obligatorio.')
        if stock < 0:
            raise ValidationError(
                'El stock de materiales no puede ser negativo.'
            )
        if stock > 999999:
            raise ValidationError(
                'El stock no puede exceder 999,999 unidades.'
            )
        return stock

    def clean_tipo(self):
        tipo = self.cleaned_data.get('tipo', '')
        if tipo:
            validar_no_solo_espacios(tipo, 'tipo')
        return tipo

    def clean_unidad_medida(self):
        unidad = self.cleaned_data.get('unidad_medida', '')
        if unidad:
            validar_no_solo_espacios(unidad, 'unidad de medida')
        return unidad


# ─────────────────────────────────────────────
# Formulario: Detalle de Compra
# ─────────────────────────────────────────────

class DetalleCompraAdminForm(forms.ModelForm):
    class Meta:
        model = DetalleCompra
        fields = '__all__'

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None:
            raise ValidationError('La cantidad es obligatoria.')
        if cantidad < 1:
            raise ValidationError('La cantidad debe ser al menos 1.')
        if cantidad > 99999:
            raise ValidationError('La cantidad no puede exceder 99,999.')
        return cantidad

    def clean_precio_unitario(self):
        precio = self.cleaned_data.get('precio_unitario')
        if precio is None:
            raise ValidationError('El precio unitario es obligatorio.')
        if precio <= 0:
            raise ValidationError('El precio unitario debe ser mayor a 0.')
        if precio > 999999.99:
            raise ValidationError(
                'El precio unitario no puede exceder 999,999.99.'
            )
        return precio

    def clean_id_material(self):
        material = self.cleaned_data.get('id_material')
        if not material:
            raise ValidationError('Debe seleccionar un material.')
        return material

    def clean_id_compra(self):
        compra = self.cleaned_data.get('id_compra')
        if not compra:
            raise ValidationError('Debe seleccionar una compra.')
        return compra
