from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from apps.catalog.models import Color, Product, Size


class Cart(models.Model):
    # either user or session_key is set (guest carts use the session)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name="cart",
        verbose_name="کاربر",
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, unique=True, verbose_name="کلید نشست")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(user__isnull=False) | models.Q(session_key__isnull=False),
                name="cart_has_owner",
            )
        ]

    def __str__(self):
        return f"Cart for {self.user or self.session_key}"

    @property
    def total_price(self):
        return sum((item.subtotal for item in self.items.all()), 0)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="سبد خرید")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="سایز")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="رنگ")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="تعداد")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ افزودن")

    class Meta:
        unique_together = ["cart", "product", "size", "color"]
        verbose_name = "قلم سبد خرید"
        verbose_name_plural = "اقلام سبد خرید"

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def subtotal(self):
        return self.product.price * self.quantity
