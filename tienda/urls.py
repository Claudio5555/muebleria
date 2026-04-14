from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mueble/<int:mueble_id>/', views.detalle_mueble, name='detalle_mueble'),
    # Carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:mueble_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/actualizar/<int:mueble_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:mueble_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views.checkout, name='checkout'),
    path('orden/<int:venta_id>/', views.orden_confirmada, name='orden_confirmada'),
    # Dashboard Admin
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/data/', views.admin_dashboard_data, name='admin_dashboard_data'),
]
