from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST, require_http_methods
from django.db import transaction
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate
from datetime import timedelta
from decimal import Decimal
from .models import Muebles, Categorias, Usuarios, Clientes, Ventas, DetallesVentas
from .forms import RegistroForm, LoginForm

def home(request):
    """Página principal"""
    categorias = Categorias.objects.all()[:6]
    muebles_destacados = Muebles.objects.all()[:8]
    context = {
        'categorias': categorias,
        'muebles_destacados': muebles_destacados,
    }
    return render(request, 'home.html', context)


def catalogo(request):
    """Catálogo de muebles con filtro por categoría"""
    categorias = Categorias.objects.all()
    categoria_id = request.GET.get('categoria')

    if categoria_id:
        # Validar que categoria_id sea un entero válido
        try:
            categoria_id = int(categoria_id)
        except (ValueError, TypeError):
            messages.warning(request, 'Categoría inválida.')
            return redirect('catalogo')
        muebles = Muebles.objects.filter(id_categoria_id=categoria_id, stock__gt=0)
        categoria_actual = Categorias.objects.filter(id_categoria=categoria_id).first()
    else:
        muebles = Muebles.objects.filter(stock__gt=0)
        categoria_actual = None

    context = {
        'muebles': muebles,
        'categorias': categorias,
        'categoria_actual': categoria_actual,
    }
    return render(request, 'catalogo.html', context)


def registro_view(request):
    """Vista de registro de usuario"""
    if request.session.get('usuario_id'):
        return redirect('home')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = Usuarios(
                nombre=form.cleaned_data['nombre'],
                apellido=form.cleaned_data['apellido'],
                usuario=form.cleaned_data['usuario'],
                contrasenia=make_password(form.cleaned_data['contrasenia']),
                rol='cliente',
                eliminado=False,
            )
            usuario.save()
            messages.success(request, '¡Registro exitoso! Ahora puedes iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()

    return render(request, 'registro.html', {'form': form})


def login_view(request):
    """Vista de inicio de sesión"""
    if request.session.get('usuario_id'):
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['usuario']
            password = form.cleaned_data['contrasenia']
            try:
                usuario = Usuarios.objects.get(usuario=username, eliminado=False)
                if check_password(password, usuario.contrasenia):
                    request.session['usuario_id'] = usuario.id_usuario
                    request.session['usuario_nombre'] = f"{usuario.nombre} {usuario.apellido}"
                    request.session['usuario_rol'] = usuario.rol
                    messages.success(request, f'¡Bienvenido, {usuario.nombre}!')
                    return redirect('home')
                else:
                    messages.error(request, 'Contraseña incorrecta.')
            except Usuarios.DoesNotExist:
                messages.error(request, 'El usuario no existe.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    """Vista de cierre de sesión"""
    request.session.flush()
    messages.success(request, 'Has cerrado sesión correctamente.')
    return redirect('home')


def detalle_mueble(request, mueble_id):
    """Vista de detalle de un mueble"""
    try:
        mueble = Muebles.objects.get(id_muebles=mueble_id)
    except Muebles.DoesNotExist:
        messages.error(request, 'Mueble no encontrado.')
        return redirect('catalogo')

    muebles_relacionados = Muebles.objects.filter(
        id_categoria=mueble.id_categoria
    ).exclude(id_muebles=mueble_id)[:4]

    context = {
        'mueble': mueble,
        'muebles_relacionados': muebles_relacionados,
    }
    return render(request, 'detalle_mueble.html', context)


# ========== CARRITO DE COMPRAS ==========

def _get_cart(request):
    """Obtener el carrito de la sesión"""
    return request.session.get('carrito', {})


def _save_cart(request, cart):
    """Guardar el carrito en la sesión"""
    request.session['carrito'] = cart
    request.session.modified = True


def _cart_count(request):
    """Contar total de items en el carrito"""
    cart = _get_cart(request)
    return sum(item['cantidad'] for item in cart.values())


@require_POST
def agregar_al_carrito(request, mueble_id):
    """Agregar un mueble al carrito (solo POST)"""
    try:
        mueble = Muebles.objects.get(id_muebles=mueble_id)
    except Muebles.DoesNotExist:
        messages.error(request, 'Mueble no encontrado.')
        return redirect('catalogo')

    cart = _get_cart(request)
    key = str(mueble_id)

    cantidad_en_carrito = cart.get(key, {}).get('cantidad', 0)

    if cantidad_en_carrito + 1 > mueble.stock:
        messages.warning(request, f'No hay suficiente stock de "{mueble.nombre}". Stock disponible: {mueble.stock}')
    else:
        if key in cart:
            cart[key]['cantidad'] += 1
        else:
            cart[key] = {
                'mueble_id': mueble.id_muebles,
                'nombre': mueble.nombre,
                'precio': str(mueble.precio),
                'imagen': mueble.imagen.url if mueble.imagen else '',
                'cantidad': 1,
                'stock': mueble.stock,
            }
        _save_cart(request, cart)
        messages.success(request, f'"{mueble.nombre}" agregado al carrito.')

    # Volver a la página anterior — validar que sea URL interna (prevenir Open Redirect)
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/catalogo/'))
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = '/catalogo/'
    return redirect(next_url)


def actualizar_carrito(request, mueble_id):
    """Actualizar cantidad de un item en el carrito"""
    if request.method == 'POST':
        cart = _get_cart(request)
        key = str(mueble_id)

        if key in cart:
            try:
                nueva_cantidad = int(request.POST.get('cantidad', 1))
            except (ValueError, TypeError):
                nueva_cantidad = 1

            try:
                mueble = Muebles.objects.get(id_muebles=mueble_id)
                if nueva_cantidad > mueble.stock:
                    messages.warning(request, f'Solo hay {mueble.stock} unidades disponibles de "{mueble.nombre}".')
                    cart[key]['cantidad'] = mueble.stock
                elif nueva_cantidad <= 0:
                    del cart[key]
                    messages.info(request, 'Producto eliminado del carrito.')
                else:
                    cart[key]['cantidad'] = nueva_cantidad
            except Muebles.DoesNotExist:
                del cart[key]

            _save_cart(request, cart)

    return redirect('ver_carrito')


@require_POST
def eliminar_del_carrito(request, mueble_id):
    """Eliminar un item del carrito (solo POST)"""
    cart = _get_cart(request)
    key = str(mueble_id)

    if key in cart:
        nombre = cart[key]['nombre']
        del cart[key]
        _save_cart(request, cart)
        messages.info(request, f'"{nombre}" eliminado del carrito.')

    return redirect('ver_carrito')


def ver_carrito(request):
    """Ver el contenido del carrito"""
    cart = _get_cart(request)
    items = []
    total = Decimal('0.00')

    for key, item in cart.items():
        precio = Decimal(item['precio'])
        subtotal = precio * item['cantidad']
        total += subtotal
        items.append({
            'mueble_id': item['mueble_id'],
            'nombre': item['nombre'],
            'precio': precio,
            'imagen': item['imagen'],
            'cantidad': item['cantidad'],
            'stock': item.get('stock', 0),
            'subtotal': subtotal,
        })

    context = {
        'items': items,
        'total': total,
        'cantidad_items': len(items),
    }
    return render(request, 'carrito.html', context)


def checkout(request):
    """Procesar la compra — requiere login"""
    # Verificar que el usuario esté logueado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.warning(request, 'Debes iniciar sesión para realizar una compra.')
        return redirect('login')

    cart = _get_cart(request)
    if not cart:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('catalogo')

    if request.method == 'POST':
        try:
            usuario = Usuarios.objects.get(id_usuario=usuario_id)

            # Crear o obtener el cliente asociado al usuario
            cliente, created = Clientes.objects.get_or_create(
                nombre=usuario.nombre,
                apellido=usuario.apellido,
                defaults={
                    'correo': '',
                    'telefono': '',
                    'dirreccion': '',
                }
            )

            # Usar transacción atómica y select_for_update para evitar condiciones de carrera
            with transaction.atomic():
                # Verificar stock y re-verificar precios desde la BD
                total = Decimal('0.00')
                items_to_process = []
                for key, item in cart.items():
                    # select_for_update bloquea la fila hasta que termine la transacción
                    mueble = Muebles.objects.select_for_update().get(
                        id_muebles=item['mueble_id']
                    )
                    if item['cantidad'] > mueble.stock:
                        messages.error(
                            request,
                            f'No hay suficiente stock de "{mueble.nombre}". '
                            f'Stock disponible: {mueble.stock}.'
                        )
                        return redirect('ver_carrito')
                    # Re-verificar precio real de la BD (no confiar en el precio de la sesión)
                    subtotal = mueble.precio * item['cantidad']
                    total += subtotal
                    items_to_process.append((mueble, item['cantidad'], mueble.precio))

                # Crear la venta
                venta = Ventas.objects.create(
                    id_cliente=cliente,
                    id_usuario=usuario,
                    total=total,
                )

                # Crear detalles y actualizar stock
                for mueble, cantidad, precio in items_to_process:
                    DetallesVentas.objects.create(
                        id_ventas=venta,
                        id_muebles=mueble,
                        cantidad=cantidad,
                        precio_unitario=precio,
                    )
                    # Descontar stock
                    mueble.stock -= cantidad
                    mueble.save()

            # Limpiar carrito
            request.session['carrito'] = {}
            request.session.modified = True

            messages.success(
                request,
                f'¡Compra realizada exitosamente! Orden #{venta.id_venta} — Total: L.{total}'
            )
            return redirect('orden_confirmada', venta_id=venta.id_venta)

        except Usuarios.DoesNotExist:
            messages.error(request, 'Error con tu cuenta. Inicia sesión de nuevo.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f'Error al procesar la compra: {str(e)}')
            return redirect('ver_carrito')

    # GET — mostrar resumen antes de confirmar
    items = []
    total = Decimal('0.00')
    for key, item in cart.items():
        precio = Decimal(item['precio'])
        subtotal = precio * item['cantidad']
        total += subtotal
        items.append({
            'mueble_id': item['mueble_id'],
            'nombre': item['nombre'],
            'precio': precio,
            'imagen': item['imagen'],
            'cantidad': item['cantidad'],
            'subtotal': subtotal,
        })

    context = {
        'items': items,
        'total': total,
    }
    return render(request, 'checkout.html', context)


def orden_confirmada(request, venta_id):
    """Página de confirmación de orden — protegida por usuario"""
    # Verificar que el usuario esté logueado
    usuario_id = request.session.get('usuario_id')
    if not usuario_id:
        messages.warning(request, 'Debes iniciar sesión para ver tus órdenes.')
        return redirect('login')

    try:
        venta = Ventas.objects.get(id_venta=venta_id)
        # Verificar que la orden pertenezca al usuario logueado
        if venta.id_usuario_id != usuario_id:
            messages.error(request, 'No tienes permiso para ver esta orden.')
            return redirect('home')
        detalles = DetallesVentas.objects.filter(id_ventas=venta)
    except Ventas.DoesNotExist:
        messages.error(request, 'Orden no encontrada.')
        return redirect('home')

    context = {
        'venta': venta,
        'detalles': detalles,
    }
    return render(request, 'orden_confirmada.html', context)


# ========== DASHBOARD ADMIN ==========

def admin_dashboard(request):
    """Vista principal del Dashboard de Ventas para el administrador"""
    # Verificar permisos admin
    usuario_rol = request.session.get('usuario_rol')
    if usuario_rol != 'admin':
        messages.error(request, 'Acceso denegado. Se requieren permisos de administrador para ver el Dashboard.')
        return redirect('home')
        
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Ventas del mes actual
    ventas_mes = Ventas.objects.filter(fecha__gte=inicio_mes)
    
    # 1. Total Ventas Mes (Cantidad de ordenes)
    total_ventas_mes = ventas_mes.count()
    
    # 2. Ingresos Mes
    ingresos_mes = ventas_mes.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    # 3. Ticket Promedio (mes)
    ticket_promedio = (ingresos_mes / total_ventas_mes) if total_ventas_mes > 0 else Decimal('0.00')
    
    # 4. Productos Vendidos (mes)
    productos_vendidos = DetallesVentas.objects.filter(id_ventas__in=ventas_mes).aggregate(total=Sum('cantidad'))['total'] or 0
    
    # Variación vs 30 días previos
    hace_30_dias = hoy - timedelta(days=30)
    hace_60_dias = hoy - timedelta(days=60)
    
    ventas_ultimos_30 = Ventas.objects.filter(fecha__gte=hace_30_dias)
    ingresos_30 = ventas_ultimos_30.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    ventas_previos_30 = Ventas.objects.filter(fecha__gte=hace_60_dias, fecha__lt=hace_30_dias)
    ingresos_previos = ventas_previos_30.aggregate(total=Sum('total'))['total'] or Decimal('0.00')
    
    if ingresos_previos > 0:
        variacion_ingresos = ((ingresos_30 - ingresos_previos) / ingresos_previos) * 100
    else:
        variacion_ingresos = 100 if ingresos_30 > 0 else 0
        
    # Ventas recientes (Tabla, top 10)
    ventas_recientes = Ventas.objects.select_related('id_cliente', 'id_usuario').order_by('-fecha')[:10]
    
    context = {
        'total_ventas_mes': total_ventas_mes,
        'ingresos_mes': ingresos_mes,
        'ticket_promedio': ticket_promedio,
        'productos_vendidos': productos_vendidos,
        'variacion_ingresos': variacion_ingresos,
        'ventas_recientes': ventas_recientes,
    }
    return render(request, 'admin/dashboard.html', context)


def admin_dashboard_data(request):
    """API para obtener datos de los gráficos del Dashboard"""
    usuario_rol = request.session.get('usuario_rol')
    if usuario_rol != 'admin':
        return JsonResponse({'error': 'No autorizado'}, status=403)
        
    hoy = timezone.now()
    hace_30_dias = hoy - timedelta(days=30)
    
    # 1. Ventas por Día (Últimos 30 días)
    ventas_por_dia = list(Ventas.objects.filter(fecha__gte=hace_30_dias)
        .annotate(dia=TruncDate('fecha'))
        .values('dia')
        .annotate(total=Sum('total'))
        .order_by('dia'))
        
    # 2. Ventas por Categoría (Dona)
    categorias_ventas = list(DetallesVentas.objects
        .values(nombre_cat=F('id_muebles__id_categoria__nombre_categoria'))
        .annotate(total_cantidad=Sum('cantidad'))
        .order_by('-total_cantidad'))
        
    # 3. Top 5 Productos (Barras Horizontales)
    top_productos = list(DetallesVentas.objects
        .values(nombre_mueble=F('id_muebles__nombre'))
        .annotate(total_vendido=Sum('cantidad'))
        .order_by('-total_vendido')[:5])
        
    # 4. Ingresos por Mes (Últimos 6 meses)
    ingresos_por_mes = {}
    for i in range(5, -1, -1):
        # Buscar el mes y el año de hace i meses (approx 30 dias por mes)
        mes_target = hoy - timedelta(days=30*i)
        mes_nombre = f"{mes_target.strftime('%b %Y')}"
        
        # Filtro aproximado
        ventas_mes_i = Ventas.objects.filter(
            fecha__year=mes_target.year, 
            fecha__month=mes_target.month
        )
        total_mes = ventas_mes_i.aggregate(t=Sum('total'))['t'] or 0
        ingresos_por_mes[mes_nombre] = float(total_mes)

    data = {
        'ventas_dia': {
            'labels': [str(v['dia']) for v in ventas_por_dia],
            'data': [float(v['total']) for v in ventas_por_dia],
        },
        'ventas_categoria': {
            'labels': [c['nombre_cat'] for c in categorias_ventas],
            'data': [c['total_cantidad'] for c in categorias_ventas],
        },
        'top_productos': {
            'labels': [str(p['nombre_mueble'])[:20] + '...' if len(p['nombre_mueble']) > 20 else p['nombre_mueble'] for p in top_productos],
            'data': [p['total_vendido'] for p in top_productos],
        },
        'ingresos_mes': {
            'labels': list(ingresos_por_mes.keys()),
            'data': list(ingresos_por_mes.values()),
        }
    }
    
    return JsonResponse(data)
