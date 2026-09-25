from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from apps.common.validators import validate_image_file

# 09xxxxxxxxx
phone_validator = RegexValidator(
    regex=r"^09\d{9}$",
    message="شماره موبایل باید به شکل ۰۹XXXXXXXXX باشد.",
)


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError("A phone number is required.")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[phone_validator],
        verbose_name="شماره موبایل",
        error_messages={"unique": "کاربری با این شماره موبایل قبلاً ثبت‌نام کرده است."},
    )
    full_name = models.CharField(max_length=150, blank=True, verbose_name="نام و نام خانوادگی")
    email = models.EmailField(
        unique=True,
        verbose_name="ایمیل",
        error_messages={"unique": "کاربری با این ایمیل قبلاً ثبت‌نام کرده است."},
    )
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, null=True, verbose_name="تصویر پروفایل", validators=[validate_image_file]
    )

    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_staff = models.BooleanField(default=False, verbose_name="دسترسی به پنل مدیریت")
    date_joined = models.DateTimeField(default=timezone.now, verbose_name="تاریخ عضویت")

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.full_name or self.phone_number

    def get_full_name(self):
        return self.full_name or self.phone_number

    def get_short_name(self):
        return self.full_name.split(" ")[0] if self.full_name else self.phone_number


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="addresses", verbose_name="کاربر")
    title = models.CharField(max_length=50, verbose_name="عنوان آدرس", help_text="مثلاً منزل، محل کار")
    receiver_full_name = models.CharField(max_length=150, verbose_name="نام و نام خانوادگی گیرنده")
    receiver_phone_number = models.CharField(max_length=11, validators=[phone_validator], verbose_name="شماره موبایل گیرنده")
    province = models.CharField(max_length=100, verbose_name="استان")
    city = models.CharField(max_length=100, verbose_name="شهر")
    postal_code = models.CharField(max_length=10, verbose_name="کد پستی")
    full_address = models.TextField(verbose_name="نشانی کامل")
    is_default = models.BooleanField(default=False, verbose_name="آدرس پیش‌فرض")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")

    class Meta:
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.title} — {self.receiver_full_name}"

    def save(self, *args, **kwargs):
        # only one default address per user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
