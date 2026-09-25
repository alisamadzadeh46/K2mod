from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from apps.catalog.models import Color, Product, Size

from .models import CartItem
from .utils import get_cart


def _cart_payload(cart):
    return {
        "total_items": cart.total_items,
        "total_price": str(cart.total_price),
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "name": item.product.name,
                "url": item.product.get_absolute_url(),
                "size": item.size.name if item.size else "",
                "color": item.color.name if item.color else "",
                "color_hex": item.color.hex_code if item.color else "",
                "price": str(item.product.price),
                "quantity": item.quantity,
                "subtotal": str(item.subtotal),
                "image_url": item.product.primary_image.image.url if item.product.primary_image else "",
            }
            for item in cart.items.select_related("product", "size", "color").all()
        ],
    }


class CartDetailView(TemplateView):
    template_name = "cart/cart_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = get_cart(self.request)
        return context


@require_POST
def add_item(request):
    product = get_object_or_404(Product, pk=request.POST.get("product_id"), is_active=True)
    quantity = max(1, int(request.POST.get("quantity", 1)))
    cart = get_cart(request)

    # size and color are optional
    size = None
    size_id = request.POST.get("size_id")
    if size_id:
        size = Size.objects.filter(pk=size_id, products=product).first()

    color = None
    color_id = request.POST.get("color_id")
    if color_id:
        color = Color.objects.filter(pk=color_id, color_products=product).first()

    item, created = CartItem.objects.get_or_create(
        cart=cart, product=product, size=size, color=color, defaults={"quantity": quantity}
    )
    if not created:
        item.quantity += quantity
        item.save()

    return JsonResponse(_cart_payload(cart))


@require_POST
def update_item(request, item_id):
    cart = get_cart(request)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    quantity = int(request.POST.get("quantity", 1))

    if quantity <= 0:
        item.delete()
    else:
        item.quantity = quantity
        item.save()

    return JsonResponse(_cart_payload(cart))


@require_POST
def remove_item(request, item_id):
    cart = get_cart(request)
    get_object_or_404(CartItem, pk=item_id, cart=cart).delete()
    return JsonResponse(_cart_payload(cart))
