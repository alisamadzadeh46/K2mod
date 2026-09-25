from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.accounts.models import Address
from apps.catalog.models import Product


class Coupon(models.Model):
    class DiscountType(models.TextChoices):
        PERCENT = "percent", "درصدی"
        FIXED = "fixed", "مبلغ ثابت (تومان)"

    code = models.CharField(max_length=30, unique=True, verbose_name="کد تخفیف")
    discount_type = models.CharField(
        max_length=10, choices=DiscountType.choices, default=DiscountType.PERCENT, verbose_name="نوع تخفیف"
    )
    percent = models.PositiveIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(90)], verbose_name="درصد تخفیف"
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=0, null=True, blank=True, verbose_name="مبلغ تخفیف (تومان)"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    valid_from = models.DateTimeField(null=True, blank=True, verbose_name="معتبر از تاریخ")
    valid_until = models.DateTimeField(null=True, blank=True, verbose_name="معتبر تا تاریخ")
    max_uses = models.PositiveIntegerField(null=True, blank=True, verbose_name="حداکثر دفعات استفاده")
    used_count = models.PositiveIntegerField(default=0, verbose_name="تعداد استفاده‌شده")

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"
        ordering = ["-id"]

    def __str__(self):
        label = f"{self.percent}%" if self.discount_type == self.DiscountType.PERCENT else f"{self.amount} ت"
        return f"{self.code} ({label})"

    def is_valid(self):
        if not self.is_active:
            return False
        now = timezone.now()
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        return True

    def discount_for(self, amount):
        amount = int(amount)
        if self.discount_type == self.DiscountType.FIXED:
            return min(amount, int(self.amount or 0))
        return amount * (self.percent or 0) // 100


class ShippingSettings(models.Model):
    """Single row, use get_solo()."""

    flat_fee = models.DecimalField(
        max_digits=12, decimal_places=0, default=0, verbose_name="هزینه ارسال (تومان)"
    )
    free_threshold = models.DecimalField(
        max_digits=12, decimal_places=0, null=True, blank=True,
        verbose_name="ارسال رایگان از این مبلغ به بالا (تومان)",
        help_text="خالی بگذارید تا ارسال رایگان همیشه غیرفعال باشد.",
    )

    class Meta:
        verbose_name = "تنظیمات ارسال"
        verbose_name_plural = "تنظیمات ارسال"

    def __str__(self):
        return "تنظیمات هزینه ارسال"

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def cost_for(self, items_subtotal):
        if self.free_threshold is not None and int(items_subtotal) >= int(self.free_threshold):
            return 0
        return int(self.flat_fee)


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING_PAYMENT = "pending_payment", "در انتظار پرداخت"
        PAID = "paid", "پرداخت شده"
        SHIPPED = "shipped", "ارسال شده"
        DELIVERED = "delivered", "تحویل داده شده"
        CANCELLED = "cancelled", "لغو شده"

    class Carrier(models.TextChoices):
        POST = "post", "پست"
        TIPAX = "tipax", "تیپاکس"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders", verbose_name="کاربر")
    address = models.ForeignKey(Address, on_delete=models.PROTECT, related_name="orders", verbose_name="آدرس ارسال")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING_PAYMENT, verbose_name="وضعیت سفارش")
    total_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ کل (تومان)")
    discount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="تخفیف (تومان)")
    coupon_code = models.CharField(max_length=30, blank=True, verbose_name="کد تخفیف")
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="هزینه ارسال (تومان)")
    shipping_carrier = models.CharField(max_length=10, choices=Carrier.choices, blank=True, verbose_name="شرکت حمل")
    tracking_code = models.CharField(max_length=50, blank=True, verbose_name="کد رهگیری")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"

    def __str__(self):
        return f"Order #{self.pk} ({self.get_status_display()})"

    @property
    def items_total(self):
        return sum((item.subtotal for item in self.items.all()), 0)

    def recalculate_total(self):
        self.total_price = max(0, self.items_total - self.discount) + self.shipping_cost
        self.save(update_fields=["total_price"])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="سفارش")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="order_items", verbose_name="محصول")
    product_name = models.CharField(max_length=255, verbose_name="نام محصول")
    brand_name = models.CharField(max_length=100, blank=True, verbose_name="برند")
    color_name = models.CharField(max_length=50, blank=True, verbose_name="رنگ")
    size_name = models.CharField(max_length=20, blank=True, verbose_name="سایز")
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت واحد (تومان)")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")

    class Meta:
        verbose_name = "قلم سفارش"
        verbose_name_plural = "اقلام سفارش"

    def __str__(self):
        return f"{self.quantity} x {self.product_name}"

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    @property
    def image_url(self):
        if self.product and self.product.primary_image:
            return self.product.primary_image.image.url
        return ""
