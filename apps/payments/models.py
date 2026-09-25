from django.db import models

from apps.orders.models import Order


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "در انتظار"
        SUCCESSFUL = "successful", "موفق"
        FAILED = "failed", "ناموفق"

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment", verbose_name="سفارش")
    gateway = models.CharField(max_length=30, default="manual", verbose_name="درگاه پرداخت", help_text="مثلاً manual یا zarinpal")
    authority = models.CharField(
        max_length=100, blank=True, verbose_name="کد پیگیری تراکنش", help_text="کد پیگیری صادرشده توسط درگاه، در صورت وجود.",
    )
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ (تومان)")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="وضعیت پرداخت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"

    def __str__(self):
        return f"Payment for Order #{self.order_id} ({self.get_status_display()})"
