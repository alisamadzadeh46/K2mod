from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from apps.common.validators import validate_image_file


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=True, verbose_name="نشانی صفحه (اسلاگ)")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children",
        verbose_name="دسته‌بندی والد",
    )
    icon_class = models.CharField(
        max_length=50, blank=True, verbose_name="کلاس آیکون",
        help_text="کلاس آیکون Remix، مثلاً ri-paint-brush-line",
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش", help_text="عدد کوچک‌تر، بالاتر نمایش داده می‌شود.")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_list", kwargs={"category_slug": self.slug})


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام برند")
    slug = models.SlugField(max_length=120, unique=True, blank=True, allow_unicode=True, verbose_name="نشانی صفحه (اسلاگ)")

    class Meta:
        ordering = ["name"]
        verbose_name = "برند"
        verbose_name_plural = "برندها"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="نام رنگ")
    hex_code = models.CharField(max_length=7, default="#cccccc", verbose_name="کد رنگ (Hex)", help_text="مثلاً ‎#ca1250")

    class Meta:
        ordering = ["name"]
        verbose_name = "رنگ"
        verbose_name_plural = "رنگ‌ها"

    def __str__(self):
        return self.name


class Size(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="نام سایز")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش", help_text="ترتیب نمایش (کوچک‌تر = اول).")

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "سایز"
        verbose_name_plural = "سایزها"

    def __str__(self):
        return self.name


class Product(models.Model):
    class Badge(models.TextChoices):
        NONE = "none", "بدون برچسب"
        BESTSELLER = "bestseller", "پرفروش"
        NEW = "new", "جدید"
        SPECIAL_DISCOUNT = "special_discount", "تخفیف ویژه"

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products", verbose_name="دسته‌بندی")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name="برند")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name="products", verbose_name="رنگ")
    sizes = models.ManyToManyField(Size, blank=True, related_name="products", verbose_name="سایزها")
    # `color` is the old single field, the picker uses `colors`
    colors = models.ManyToManyField(Color, blank=True, related_name="color_products", verbose_name="رنگ‌ها")
    name = models.CharField(max_length=255, verbose_name="نام محصول")
    slug = models.SlugField(max_length=280, unique=True, blank=True, allow_unicode=True, verbose_name="نشانی صفحه (اسلاگ)")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    price = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)], verbose_name="قیمت (تومان)")
    old_price = models.DecimalField(
        max_digits=12, decimal_places=0, null=True, blank=True, validators=[MinValueValidator(0)],
        verbose_name="قیمت قبل از تخفیف (تومان)",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی انبار")
    badge = models.CharField(max_length=20, choices=Badge.choices, default=Badge.NONE, verbose_name="برچسب")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_featured = models.BooleanField(default=False, verbose_name="محصول منتخب", help_text="نمایش در بخش‌های منتخب صفحه اصلی.")

    # SEO (falls back to name/description if empty)
    meta_title = models.CharField(
        max_length=70, blank=True, verbose_name="عنوان سئو (meta title)",
        help_text="عنوانی که در نتایج گوگل و تب مرورگر نمایش داده می‌شود. خالی = نام محصول.",
    )
    meta_description = models.CharField(
        max_length=160, blank=True, verbose_name="توضیحات سئو (meta description)",
        help_text="توضیح کوتاه برای نتایج گوگل (حداکثر ۱۶۰ کاراکتر).",
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["category", "is_active"])]
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True) or "product"
            slug = base_slug
            suffix = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                suffix += 1
                slug = f"{base_slug}-{suffix}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalog:product_detail", kwargs={"slug": self.slug})

    @property
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return round((self.old_price - self.price) / self.old_price * 100)
        return 0

    @property
    def in_stock(self):
        return self.stock > 0

    @property
    def primary_image(self):
        return self.images.first()

    @property
    def seo_title(self):
        return self.meta_title or f"{self.name} | فروشگاه k2mod"

    @property
    def seo_description(self):
        if self.meta_description:
            return self.meta_description
        text = " ".join(self.description.split())
        return (text[:157] + "…") if len(text) > 158 else text


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images", verbose_name="محصول")
    image = models.ImageField(upload_to="products/", validators=[validate_image_file], verbose_name="تصویر")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="متن جایگزین")
    order = models.PositiveIntegerField(default=0, blank=True, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"

    def __str__(self):
        return self.alt_text or f"Image for {self.product.name}"


class Banner(models.Model):
    class Placement(models.TextChoices):
        HERO = "hero", "اسلایدر اصلی"
        PROMO = "promo", "بنر تبلیغاتی"

    title = models.CharField(max_length=200, blank=True, verbose_name="عنوان")
    image = models.ImageField(upload_to="banners/", validators=[validate_image_file], verbose_name="تصویر")
    link_url = models.CharField(max_length=255, blank=True, verbose_name="لینک مقصد", help_text="آدرسی که بنر به آن پیوند می‌خورد، مثلاً /c/cosmetics/")
    placement = models.CharField(max_length=10, choices=Placement.choices, default=Placement.HERO, verbose_name="محل نمایش")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "بنر"
        verbose_name_plural = "بنرها"

    def __str__(self):
        return self.title or f"Banner #{self.pk}"


class ProductComment(models.Model):
    """parent is only set for staff replies (one level)."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments", verbose_name="محصول")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="product_comments", verbose_name="کاربر")
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies",
        verbose_name="پاسخ به",
    )
    body = models.TextField(max_length=2000, verbose_name="متن دیدگاه")
    is_approved = models.BooleanField(default=False, verbose_name="تأیید شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        ordering = ["created_at"]
        verbose_name = "دیدگاه"
        verbose_name_plural = "دیدگاه‌ها"

    def __str__(self):
        return f"Comment by {self.user} on {self.product.name}"

    @property
    def is_staff_reply(self):
        return self.parent_id is not None


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites", verbose_name="کاربر")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorited_by", verbose_name="محصول")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ افزودن")

    class Meta:
        unique_together = ["user", "product"]
        ordering = ["-created_at"]
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "علاقه‌مندی‌ها"

    def __str__(self):
        return f"{self.user} ♥ {self.product.name}"
