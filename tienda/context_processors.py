def cart_context(request):
    """Context processor para mostrar el conteo del carrito en toda la app"""
    cart = request.session.get('carrito', {})
    count = sum(item['cantidad'] for item in cart.values())
    return {'cart_count': count}
