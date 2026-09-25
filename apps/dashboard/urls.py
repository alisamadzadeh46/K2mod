from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("products/add/", views.ProductCreateView.as_view(), name="product_add"),
    path("products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("products/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    path("products/<int:pk>/upload-image/", views.ProductImageUploadView.as_view(), name="product_upload_image"),
    path("products/<int:pk>/images/<int:image_pk>/delete/", views.ProductImageDeleteView.as_view(), name="product_delete_image"),
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user_detail"),
    path("users/<int:pk>/toggle-active/", views.UserToggleActiveView.as_view(), name="user_toggle_active"),
    path("users/<int:pk>/toggle-staff/", views.UserToggleStaffView.as_view(), name="user_toggle_staff"),
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path("categories/add/", views.CategoryCreateView.as_view(), name="category_add"),
    path("categories/<int:pk>/edit/", views.CategoryUpdateView.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/", views.CategoryDeleteView.as_view(), name="category_delete"),
    path("categories/create/", views.CategoryCreateAjaxView.as_view(), name="category_create"),
    path("brands/create/", views.BrandCreateAjaxView.as_view(), name="brand_create"),
    path("colors/create/", views.ColorCreateAjaxView.as_view(), name="color_create"),
    path("coupons/", views.CouponListView.as_view(), name="coupon_list"),
    path("coupons/add/", views.CouponCreateView.as_view(), name="coupon_add"),
    path("coupons/<int:pk>/edit/", views.CouponUpdateView.as_view(), name="coupon_edit"),
    path("coupons/<int:pk>/delete/", views.CouponDeleteView.as_view(), name="coupon_delete"),
    path("shipping/", views.ShippingSettingsView.as_view(), name="shipping_settings"),
    path("comments/", views.CommentListView.as_view(), name="comment_list"),
    path("comments/<int:pk>/approve/", views.CommentApproveView.as_view(), name="comment_approve"),
    path("comments/<int:pk>/reply/", views.CommentReplyView.as_view(), name="comment_reply"),
    path("comments/<int:pk>/delete/", views.CommentDeleteView.as_view(), name="comment_delete"),
    path("reports/", views.ReportsView.as_view(), name="reports"),
]
