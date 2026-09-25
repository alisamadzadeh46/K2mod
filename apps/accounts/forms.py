from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Address, CustomUser


class RegisterForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["phone_number", "full_name", "email"]
        widgets = {
            "phone_number": forms.TextInput(attrs={"placeholder": "۰۹۱۲۳۴۵۶۷۸۹", "autocomplete": "tel"}),
            "full_name": forms.TextInput(attrs={"placeholder": "نام و نام خانوادگی خود را وارد کنید"}),
            "email": forms.EmailInput(attrs={"placeholder": "ایمیل خود را وارد کنید", "autocomplete": "email"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["placeholder"] = "رمز عبور را وارد کنید"
        self.fields["password2"].widget.attrs["placeholder"] = "تکرار رمز عبور را وارد کنید"


class PhoneLoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "شماره موبایل یا رمز عبور وارد شده صحیح نیست.",
        "inactive": "این حساب کاربری غیرفعال است.",
    }

    username = forms.CharField(
        label="شماره موبایل",
        widget=forms.TextInput(
            attrs={"autofocus": True, "autocomplete": "tel", "placeholder": "۰۹۱۲۳۴۵۶۷۸۹"}
        ),
    )
    password = forms.CharField(
        label="رمز عبور",
        widget=forms.PasswordInput(
            attrs={"autocomplete": "current-password", "placeholder": "رمز عبور خود را وارد کنید"}
        ),
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["full_name", "email", "avatar"]


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = [
            "title",
            "receiver_full_name",
            "receiver_phone_number",
            "province",
            "city",
            "postal_code",
            "full_address",
            "is_default",
        ]
        labels = {
            "title": "عنوان آدرس",
            "receiver_full_name": "نام تحویل‌گیرنده",
            "receiver_phone_number": "شماره تماس تحویل‌گیرنده",
            "province": "استان",
            "city": "شهر",
            "postal_code": "کد پستی",
            "full_address": "نشانی کامل",
            "is_default": "به عنوان آدرس پیش‌فرض ثبت شود",
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً: خانه، محل کار"}),
            "receiver_full_name": forms.TextInput(attrs={"placeholder": "نام و نام خانوادگی"}),
            "receiver_phone_number": forms.TextInput(attrs={"placeholder": "۰۹۱۲۳۴۵۶۷۸۹"}),
            "province": forms.TextInput(attrs={"placeholder": "استان"}),
            "city": forms.TextInput(attrs={"placeholder": "شهر"}),
            "postal_code": forms.TextInput(attrs={"placeholder": "کد پستی ۱۰ رقمی"}),
            "full_address": forms.Textarea(attrs={"rows": 3, "placeholder": "خیابان، کوچه، پلاک، واحد"}),
        }
