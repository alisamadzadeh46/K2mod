from django.contrib import admin

from .models import Coupon, Order, OrderItem, ShippingSettings


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "status", "total_price", "discount", "shipping_cost", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["user__phone_number", "user__full_name", "id"]
    inlines = [OrderItemInline]
    list_per_page = 25


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "discount_type", "percent", "amount", "is_active", "valid_from", "valid_until", "used_count", "max_uses"]
    list_filter = ["is_active", "discount_type"]
    search_fields = ["code"]
    list_per_page = 25


@admin.register(ShippingSettings)
class ShippingSettingsAdmin(admin.ModelAdmin):
    list_display = ["flat_fee", "free_threshold"]

    def has_add_permission(self, request):
        # single row
        return not ShippingSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
