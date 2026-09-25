from .models import Cart, CartItem


def get_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        _merge_session_cart_into(request, cart)
        return cart

    if not request.session.session_key:
        request.session.save()
    cart, _ = Cart.objects.get_or_create(session_key=request.session.session_key)
    return cart


def _merge_session_cart_into(request, user_cart):
    _merge_by_session_key(request.session.session_key, user_cart)


def _merge_by_session_key(session_key, user_cart):
    if not session_key:
        return

    try:
        session_cart = Cart.objects.get(session_key=session_key)
    except Cart.DoesNotExist:
        return

    if session_cart.pk == user_cart.pk:
        return

    for item in session_cart.items.all():
        existing = CartItem.objects.filter(
            cart=user_cart, product=item.product, size=item.size, color=item.color
        ).first()
        if existing:
            existing.quantity += item.quantity
            existing.save()
        else:
            item.pk = None
            item.cart = user_cart
            item.save()

    session_cart.delete()


def merge_anonymous_cart(user, session_key):
    # called after login with the old session key, since login rotates it
    if not session_key:
        return
    user_cart, _ = Cart.objects.get_or_create(user=user)
    _merge_by_session_key(session_key, user_cart)
