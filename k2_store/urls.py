from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "مدیریت پیشرفته فروشگاه k2mod"
admin.site.site_title = "پنل مدیریت k2mod"
admin.site.index_title = "خوش آمدید"

urlpatterns = [
    # admin url comes from .env
    path(f"{settings.DJANGO_ADMIN_URL_PREFIX}/", admin.site.urls),
    path(f"{settings.DASHBOARD_URL_PREFIX}/", include("apps.dashboard.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("cart/", include("apps.cart.urls")),
    path("orders/", include("apps.orders.urls")),
    path("", include("apps.catalog.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
