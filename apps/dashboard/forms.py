import re

import jdatetime
from django import forms
from django.utils import timezone as dj_timezone

from apps.catalog.models import Brand, Category, Color, Product, ProductComment, ProductImage
from apps.orders.models import Coupon, Order, ShippingSettings

# persian/arabic digits -> latin
_DIGIT_TRANS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
_FA_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
_JALALI_RE = re.compile(r"^(\d{4})[-/](\d{1,2})[-/](\d{1,2})(?:[ T](\d{1,2}):(\d{2}))?$")


class JalaliDateTimeField(forms.CharField):
    """Jalali input for a DateTimeField, e.g. ۱۴۰۴/۰۴/۱۵ ۱۴:۳۰"""

    widget = forms.TextInput(
        attrs={"class": "jalali-datetime-input", "placeholder": "۱۴۰۴/۰۴/۱۵ ۱۴:۳۰", "autocomplete": "off"}
    )

    def to_python(self, value):
        if not value:
            return None
        raw = value.strip().translate(_DIGIT_TRANS)
        match = _JALALI_RE.match(raw)
        if not match:
            raise forms.ValidationError("قالب تاریخ نامعتبر است. مثال: ۱۴۰۴/۰۴/۱۵ ۱۴:۳۰")
        year, month, day, hour, minute = match.groups()
        try:
            j = jdatetime.datetime(int(year), int(month), int(day), int(hour or 0), int(minute or 0))
            gregorian = j.togregorian()
        except ValueError:
            raise forms.ValidationError("تاریخ وارد شده معتبر نیست.")
        if dj_timezone.is_naive(gregorian):
            gregorian = dj_timezone.make_aware(gregorian)
        return gregorian

    def prepare_value(self, value):
        if value is None or isinstance(value, str):
            return value
        if dj_timezone.is_aware(value):
            value = dj_timezone.localtime(value)
        j = jdatetime.datetime.fromgregorian(datetime=value)
        return f"{j.year}/{j.month:02d}/{j.day:02d} {j.hour:02d}:{j.minute:02d}".translate(_FA_DIGITS)


class SeparatedNumberInput(forms.TextInput):
    """Price input with thousands separators (see db-money in dashboard.js)."""

    def __init__(self, attrs=None):
        defaults = {"inputmode": "numeric", "autocomplete": "off", "class": "db-money"}
        if attrs:
            defaults.update(attrs)
        super().__init__(defaults)

    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if not value:
            return value
        value = value.translate(_DIGIT_TRANS)
        for sep in (",", "٬", "،", " ", "‌"):
            value = value.replace(sep, "")
        return value


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "category",
            "brand",
            "sizes",
            "colors",
            "name",
            "slug",
            "description",
            "price",
            "old_price",
            "stock",
            "badge",
            "is_active",
            "is_featured",
            "meta_title",
            "meta_description",
        ]
        widgets = {
            "slug": forms.TextInput(attrs={"placeholder": "خالی بگذارید تا خودکار ساخته شود"}),
            "description": forms.Textarea(attrs={"rows": 6, "class": "db-richtext"}),
            "meta_description": forms.Textarea(attrs={"rows": 2, "class": "seo-desc"}),
            "meta_title": forms.TextInput(attrs={"class": "seo-title"}),
            "price": SeparatedNumberInput(),
            "old_price": SeparatedNumberInput(),
            "sizes": forms.CheckboxSelectMultiple(),
            "colors": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False
        # custom dropdowns in dashboard.js
        for name in ["category", "brand", "badge"]:
            self.fields[name].widget.attrs["class"] = "db-enhance"


class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ["image", "alt_text", "order"]


class CommentReplyForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "پاسخ فروشگاه را بنویسید..."}),
        max_length=2000,
    )


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name"]


class ColorForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = ["name", "hex_code"]


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "parent", "icon_class", "is_active", "order"]
        widgets = {
            "icon_class": forms.TextInput(attrs={"placeholder": "مثلاً ri-t-shirt-line"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent"].required = False
        self.fields["parent"].widget.attrs["class"] = "db-enhance"


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["status", "shipping_carrier", "tracking_code"]
        widgets = {
            "status": forms.Select(attrs={"class": "db-enhance"}),
            "shipping_carrier": forms.Select(attrs={"class": "db-enhance"}),
            "tracking_code": forms.TextInput(attrs={
                "placeholder": "کد رهگیری پست یا تیپاکس",
                "dir": "ltr",
            }),
        }


class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [
            "code",
            "discount_type",
            "percent",
            "amount",
            "valid_from",
            "valid_until",
            "max_uses",
            "is_active",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"placeholder": "مثلاً SUMMER25", "style": "text-transform:uppercase"}),
            "discount_type": forms.Select(attrs={"class": "db-enhance"}),
            "percent": forms.NumberInput(attrs={"placeholder": "مثلاً ۲۰"}),
            "amount": SeparatedNumberInput(attrs={"placeholder": "مثلاً ۵۰۰۰۰"}),
            "max_uses": forms.NumberInput(attrs={"placeholder": "خالی = نامحدود"}),
        }
        field_classes = {"valid_from": JalaliDateTimeField, "valid_until": JalaliDateTimeField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ("percent", "amount", "valid_from", "valid_until", "max_uses"):
            self.fields[name].required = False

    def clean(self):
        cleaned = super().clean()
        cleaned["code"] = (cleaned.get("code") or "").upper()
        dtype = cleaned.get("discount_type")
        if dtype == Coupon.DiscountType.PERCENT and not cleaned.get("percent"):
            self.add_error("percent", "برای تخفیف درصدی، درصد را وارد کنید.")
        if dtype == Coupon.DiscountType.FIXED and not cleaned.get("amount"):
            self.add_error("amount", "برای تخفیف مبلغ ثابت، مبلغ را وارد کنید.")
        return cleaned


class ShippingSettingsForm(forms.ModelForm):
    class Meta:
        model = ShippingSettings
        fields = ["flat_fee", "free_threshold"]
        widgets = {
            "flat_fee": SeparatedNumberInput(attrs={"placeholder": "مثلاً ۵۰۰۰۰"}),
            "free_threshold": SeparatedNumberInput(attrs={"placeholder": "خالی = غیرفعال"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["free_threshold"].required = False
