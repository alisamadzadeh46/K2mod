from django.contrib import admin

from .models import Banner, Brand, Category, Color, Favorite, Product, ProductComment, ProductImage, Size


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "parent", "is_active", "order"]
    list_filter = ["is_active", "parent"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}
    list_per_page = 25


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]
    prepopulated_fields = {"slug": ["name"]}
    list_per_page = 25


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ["name", "hex_code"]
    list_per_page = 25


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ["name", "order"]
    ordering = ["order", "name"]
    list_per_page = 25


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "brand", "color", "price", "old_price", "stock", "badge", "is_active", "is_featured"]
    list_filter = ["category", "brand", "color", "sizes", "badge", "is_active", "is_featured"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ["name"]}
    filter_horizontal = ["sizes", "colors"]
    inlines = [ProductImageInline]
    list_per_page = 20


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ["title", "is_active", "order"]
    list_filter = ["is_active"]
    list_per_page = 25


@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "is_approved", "is_staff_reply", "created_at"]
    list_filter = ["is_approved", "created_at"]
    search_fields = ["product__name", "user__phone_number", "body"]
    list_per_page = 25


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "product", "created_at"]
    search_fields = ["user__phone_number", "product__name"]
    list_per_page = 25
