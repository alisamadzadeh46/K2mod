from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import F
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, TemplateView

from apps.cart.utils import get_cart
from apps.payments.utils import get_active_gateway

from .models import Coupon, Order, OrderItem, ShippingSettings

COUPON_SESSION_KEY = "coupon_code"


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "orders/checkout.html"

    def default_address(self):
        addresses = self.request.user.addresses.all()
        return addresses.filter(is_default=True).first() or addresses.first()

    def applied_coupon(self):
        code = self.request.session.get(COUPON_SESSION_KEY)
        if not code:
            return None
        coupon = Coupon.objects.filter(code__iexact=code).first()
        if coupon and coupon.is_valid():
            return coupon
        self.request.session.pop(COUPON_SESSION_KEY, None)
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        coupon = self.applied_coupon()
        items_total = cart.total_price
        discount = coupon.discount_for(items_total) if coupon else 0
        # free shipping is based on subtotal, not after discount
        shipping_cost = ShippingSettings.get_solo().cost_for(items_total)
        context["cart"] = cart
        context["address"] = self.default_address()
        context["coupon"] = coupon
        context["discount"] = discount
        context["shipping_cost"] = shipping_cost
        context["payable"] = max(0, items_total - discount) + shipping_cost
        return context

    def post(self, request, *args, **kwargs):
        # coupon
        if "apply_coupon" in request.POST:
            code = (request.POST.get("coupon_code") or "").strip()
            coupon = Coupon.objects.filter(code__iexact=code).first()
            if coupon and coupon.is_valid():
                request.session[COUPON_SESSION_KEY] = coupon.code
                messages.success(request, f"کد تخفیف «{coupon.code}» اعمال شد ({coupon.percent}٪).")
            else:
                messages.error(request, "کد تخفیف نامعتبر یا منقضی شده است.")
            return redirect("orders:checkout")
        if "remove_coupon" in request.POST:
            request.session.pop(COUPON_SESSION_KEY, None)
            messages.info(request, "کد تخفیف حذف شد.")
            return redirect("orders:checkout")

        # place order
        cart = get_cart(request)
        address = self.default_address()

        if not cart.items.exists():
            messages.error(request, "سبد خرید شما خالی است.")
            return redirect("cart:detail")
        if not address:
            messages.error(request, "ابتدا یک آدرس ثبت کنید.")
            return redirect("accounts:address_add")

        coupon = self.applied_coupon()

        with transaction.atomic():
            order = Order.objects.create(user=request.user, address=address, total_price=0)
            for item in cart.items.select_related("product", "product__brand", "product__color", "size", "color").all():
                p = item.product
                OrderItem.objects.create(
                    order=order,
                    product=p,
                    product_name=p.name,
                    brand_name=p.brand.name if p.brand else "",
                    color_name=item.color.name if item.color else (p.color.name if p.color else ""),
                    size_name=item.size.name if item.size else "",
                    unit_price=p.price,
                    quantity=item.quantity,
                )
            if coupon:
                order.discount = coupon.discount_for(order.items_total)
                order.coupon_code = coupon.code
                Coupon.objects.filter(pk=coupon.pk).update(used_count=F("used_count") + 1)
            order.shipping_cost = ShippingSettings.get_solo().cost_for(order.items_total)
            order.recalculate_total()
            cart.items.all().delete()
            request.session.pop(COUPON_SESSION_KEY, None)

        redirect_url = get_active_gateway().start_payment(order)
        return redirect(redirect_url)


class OrderConfirmationView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/confirmation.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"
    context_object_name = "order"
    extra_context = {"active_account_tab": "orders"}

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_history.html"
    context_object_name = "orders"
    paginate_by = 10
    extra_context = {"active_account_tab": "orders"}

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")
