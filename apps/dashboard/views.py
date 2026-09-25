from django.contrib import messages
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, TemplateView, UpdateView, View

from apps.accounts.models import CustomUser
from apps.catalog.models import Category, Product, ProductComment, ProductImage
from apps.orders.models import Coupon, Order, OrderItem, ShippingSettings

from .forms import (
    BrandForm,
    CategoryForm,
    ColorForm,
    CommentReplyForm,
    CouponForm,
    OrderStatusForm,
    ProductForm,
    ProductImageForm,
    ShippingSettingsForm,
)
from .mixins import ActiveTabMixin, StaffRequiredMixin


class DashboardHomeView(StaffRequiredMixin, ActiveTabMixin, TemplateView):
    template_name = "dashboard/home.html"
    active_tab = "dashboard"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paid_orders = Order.objects.filter(
            status__in=[Order.Status.PAID, Order.Status.SHIPPED, Order.Status.DELIVERED]
        )

        context["total_revenue"] = paid_orders.aggregate(total=Sum("total_price"))["total"] or 0
        context["products_sold"] = (
            OrderItem.objects.filter(order__in=paid_orders).aggregate(total=Sum("quantity"))["total"] or 0
        )
        context["new_users_count"] = CustomUser.objects.filter(
            date_joined__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()
        context["new_orders_count"] = Order.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()

        context["recent_products"] = Product.objects.select_related("category")[:5]
        context["recent_orders"] = Order.objects.select_related("user")[:5]

        context["monthly_sales"] = (
            paid_orders.annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(total=Sum("total_price"))
            .order_by("month")[:7]
        )
        return context


class ProductListView(StaffRequiredMixin, ActiveTabMixin, ListView):
    model = Product
    template_name = "dashboard/product_list.html"
    context_object_name = "products"
    paginate_by = 20
    active_tab = "products"

    def get_queryset(self):
        return Product.objects.select_related("category").order_by("-created_at")


class ProductCreateView(StaffRequiredMixin, ActiveTabMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/product_form.html"
    success_url = reverse_lazy("dashboard:product_list")
    active_tab = "add-product"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "محصول با موفقیت ایجاد شد.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_form"] = ProductImageForm()
        return context


class ProductUpdateView(StaffRequiredMixin, ActiveTabMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "dashboard/product_form.html"
    success_url = reverse_lazy("dashboard:product_list")
    active_tab = "products"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "محصول با موفقیت ویرایش شد.")
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["image_form"] = ProductImageForm()
        return context


class ProductDeleteView(StaffRequiredMixin, ActiveTabMixin, DeleteView):
    model = Product
    template_name = "dashboard/product_confirm_delete.html"
    success_url = reverse_lazy("dashboard:product_list")
    active_tab = "products"


class ProductImageUploadView(StaffRequiredMixin, View):
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save(commit=False)
            image.product = product
            image.save()
            messages.success(request, "تصویر با موفقیت آپلود شد.")
        else:
            messages.error(request, "آپلود تصویر با خطا مواجه شد.")
        return redirect("dashboard:product_edit", pk=product.pk)


class ProductImageDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk, image_pk):
        image = get_object_or_404(ProductImage, pk=image_pk, product_id=pk)
        image.image.delete(save=False)
        image.delete()
        messages.success(request, "تصویر حذف شد.")
        return redirect("dashboard:product_edit", pk=pk)


class OrderListView(StaffRequiredMixin, ActiveTabMixin, ListView):
    model = Order
    template_name = "dashboard/order_list.html"
    context_object_name = "orders"
    paginate_by = 20
    active_tab = "orders"

    def get_queryset(self):
        return Order.objects.select_related("user").order_by("-created_at")


class OrderDetailView(StaffRequiredMixin, ActiveTabMixin, UpdateView):
    model = Order
    form_class = OrderStatusForm
    template_name = "dashboard/order_detail.html"
    active_tab = "orders"

    def get_success_url(self):
        messages.success(self.request, "وضعیت سفارش به‌روزرسانی شد.")
        return reverse_lazy("dashboard:order_detail", kwargs={"pk": self.object.pk})


class UserListView(StaffRequiredMixin, ActiveTabMixin, ListView):
    model = CustomUser
    template_name = "dashboard/user_list.html"
    context_object_name = "users"
    paginate_by = 30
    active_tab = "users"

    def get_queryset(self):
        return CustomUser.objects.order_by("-date_joined")


class UserDetailView(StaffRequiredMixin, ActiveTabMixin, DetailView):
    model = CustomUser
    template_name = "dashboard/user_detail.html"
    context_object_name = "account"
    active_tab = "users"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        context["orders"] = user.orders.all()[:10]
        context["addresses"] = user.addresses.all()
        context["comment_count"] = user.product_comments.count()
        context["favorite_count"] = user.favorites.count()
        return context


class UserToggleActiveView(StaffRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        messages.success(request, f"کاربر {user} اکنون {'فعال' if user.is_active else 'غیرفعال'} است.")
        return redirect(request.META.get("HTTP_REFERER", reverse_lazy("dashboard:user_list")))


class UserToggleStaffView(StaffRequiredMixin, View):
    def post(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)
        if user == request.user:
            messages.error(request, "نمی‌توانید سطح دسترسی خودتان را تغییر دهید.")
        else:
            user.is_staff = not user.is_staff
            user.save(update_fields=["is_staff"])
            messages.success(
                request, f"کاربر {user} {'به مدیر ارتقا یافت' if user.is_staff else 'از مدیریت خارج شد'}."
            )
        return redirect(request.META.get("HTTP_REFERER", reverse_lazy("dashboard:user_list")))


class CategoryListView(StaffRequiredMixin, ActiveTabMixin, ListView):
    model = Category
    template_name = "dashboard/category_list.html"
    context_object_name = "categories"
    active_tab = "categories"

    def get_queryset(self):
        return Category.objects.select_related("parent").order_by("order", "name")


class CategoryCreateView(StaffRequiredMixin, ActiveTabMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "dashboard/category_form.html"
    success_url = reverse_lazy("dashboard:category_list")
    active_tab = "categories"

    def form_valid(self, form):
        messages.success(self.request, "دسته‌بندی ایجاد شد.")
        return super().form_valid(form)


class CategoryUpdateView(StaffRequiredMixin, ActiveTabMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "dashboard/category_form.html"
    success_url = reverse_lazy("dashboard:category_list")
    active_tab = "categories"

    def form_valid(self, form):
        messages.success(self.request, "دسته‌بندی ویرایش شد.")
        return super().form_valid(form)


class CategoryDeleteView(StaffRequiredMixin, ActiveTabMixin, DeleteView):
    model = Category
    template_name = "dashboard/category_confirm_delete.html"
    success_url = reverse_lazy("dashboard:category_list")
    active_tab = "categories"

    def form_valid(self, form):
        # Product.category is PROTECT
        if self.get_object().products.exists():
            messages.error(self.request, "این دسته‌بندی محصول دارد و قابل حذف نیست.")
            return redirect("dashboard:category_list")
        messages.success(self.request, "دسته‌بندی حذف شد.")
        return super().form_valid(form)


class CouponListView(StaffRequiredMixin, ActiveTabMixin, ListView):
    model = Coupon
    template_name = "dashboard/coupon_list.html"
    context_object_name = "coupons"
    active_tab = "coupons"


class CouponCreateView(StaffRequiredMixin, ActiveTabMixin, CreateView):
    model = Coupon
    form_class = CouponForm
    template_name = "dashboard/coupon_form.html"
    success_url = reverse_lazy("dashboard:coupon_list")
    active_tab = "coupons"

    def form_valid(self, form):
        messages.success(self.request, "کد تخفیف ایجاد شد.")
        return super().form_valid(form)


class CouponUpdateView(StaffRequiredMixin, ActiveTabMixin, UpdateView):
    model = Coupon
    form_class = CouponForm
    template_name = "dashboard/coupon_form.html"
    success_url = reverse_lazy("dashboard:coupon_list")
    active_tab = "coupons"

    def form_valid(self, form):
        messages.success(self.request, "کد تخفیف ویرایش شد.")
        return super().form_valid(form)


class CouponDeleteView(StaffRequiredMixin, ActiveTabMixin, DeleteView):
    model = Coupon
    template_name = "dashboard/coupon_confirm_delete.html"
    success_url = reverse_lazy("dashboard:coupon_list")
    active_tab = "coupons"

    def form_valid(self, form):
        messages.success(self.request, "کد تخفیف حذف شد.")
        return super().form_valid(form)


class ShippingSettingsView(StaffRequiredMixin, ActiveTabMixin, FormView):
    template_name = "dashboard/shipping_settings.html"
    form_class = ShippingSettingsForm
    success_url = reverse_lazy("dashboard:shipping_settings")
    active_tab = "shipping"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = ShippingSettings.get_solo()
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "تنظیمات هزینه ارسال ذخیره شد.")
        return super().form_valid(form)


class CategoryCreateAjaxView(StaffRequiredMixin, View):
    def post(self, request):
        form = CategoryForm({"name": request.POST.get("name", ""), "is_active": True})
        if form.is_valid():
            category = form.save()
            return JsonResponse({"id": category.id, "name": category.name})
        return JsonResponse({"error": "نام دسته‌بندی نامعتبر است."}, status=400)


class BrandCreateAjaxView(StaffRequiredMixin, View):
    def post(self, request):
        form = BrandForm(request.POST)
        if form.is_valid():
            brand = form.save()
            return JsonResponse({"id": brand.id, "name": brand.name})
        return JsonResponse({"error": "نام برند نامعتبر است."}, status=400)


class ColorCreateAjaxView(StaffRequiredMixin, View):
    def post(self, request):
        form = ColorForm(request.POST)
        if form.is_valid():
            color = form.save()
            return JsonResponse({"id": color.id, "name": color.name})
        return JsonResponse({"error": "نام رنگ نامعتبر است."}, status=400)


class CommentListView(StaffRequiredMixin, ActiveTabMixin, ListView):
    model = ProductComment
    template_name = "dashboard/comment_list.html"
    context_object_name = "comments"
    paginate_by = 20
    active_tab = "comments"

    def get_queryset(self):
        qs = (
            ProductComment.objects.filter(parent__isnull=True)
            .select_related("user", "product")
            .prefetch_related("replies__user")
            .order_by("-created_at")
        )
        self.current_filter = self.request.GET.get("filter", "all")
        if self.current_filter == "pending":
            qs = qs.filter(is_approved=False)
        elif self.current_filter == "approved":
            qs = qs.filter(is_approved=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reply_form"] = CommentReplyForm()
        context["current_filter"] = self.current_filter
        base = ProductComment.objects.filter(parent__isnull=True)
        context["pending_count"] = base.filter(is_approved=False).count()
        context["approved_count"] = base.filter(is_approved=True).count()
        return context


class CommentApproveView(StaffRequiredMixin, View):
    def post(self, request, pk):
        comment = get_object_or_404(ProductComment, pk=pk, parent__isnull=True)
        comment.is_approved = True
        comment.save(update_fields=["is_approved"])
        messages.success(request, "دیدگاه تأیید و منتشر شد.")
        return redirect(request.META.get("HTTP_REFERER", reverse_lazy("dashboard:comment_list")))


class CommentReplyView(StaffRequiredMixin, View):
    def post(self, request, pk):
        parent = get_object_or_404(ProductComment, pk=pk, parent__isnull=True)
        form = CommentReplyForm(request.POST)
        if form.is_valid():
            ProductComment.objects.create(
                product=parent.product,
                user=request.user,
                parent=parent,
                body=form.cleaned_data["body"],
                is_approved=True,
            )
            # replying also approves the comment
            if not parent.is_approved:
                parent.is_approved = True
                parent.save(update_fields=["is_approved"])
            messages.success(request, "پاسخ شما ثبت شد.")
        return redirect("dashboard:comment_list")


class CommentDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        get_object_or_404(ProductComment, pk=pk).delete()
        messages.success(request, "دیدگاه حذف شد.")
        return redirect(request.META.get("HTTP_REFERER", reverse_lazy("dashboard:comment_list")))


class ReportsView(StaffRequiredMixin, ActiveTabMixin, TemplateView):
    template_name = "dashboard/reports.html"
    active_tab = "reports"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_orders = Order.objects.all()
        paid_orders = Order.objects.filter(
            status__in=[Order.Status.PAID, Order.Status.SHIPPED, Order.Status.DELIVERED]
        )
        paid_items = OrderItem.objects.filter(order__in=paid_orders)

        context["total_revenue"] = paid_orders.aggregate(t=Sum("total_price"))["t"] or 0
        context["total_orders"] = all_orders.count()
        context["paid_orders_count"] = paid_orders.count()
        context["units_sold"] = paid_items.aggregate(t=Sum("quantity"))["t"] or 0
        context["avg_order"] = (
            int(context["total_revenue"] / context["paid_orders_count"]) if context["paid_orders_count"] else 0
        )

        status_rows = list(
            all_orders.values("status").annotate(count=Count("id")).order_by("-count")
        )
        status_labels = dict(Order.Status.choices)
        for row in status_rows:
            row["label"] = status_labels.get(row["status"], row["status"])
        context["status_rows"] = status_rows
        context["status_total"] = sum(r["count"] for r in status_rows) or 1

        cat_rows = list(
            paid_items.values("product__category__name")
            .annotate(total=Sum("quantity"))
            .order_by("-total")
        )
        cat_max = max((r["total"] for r in cat_rows), default=0) or 1
        for row in cat_rows:
            row["pct"] = round(row["total"] / cat_max * 100)
        context["category_sales"] = cat_rows

        context["top_products"] = (
            paid_items.values("product__name")
            .annotate(units_sold=Sum("quantity"), revenue=Sum("unit_price"))
            .order_by("-units_sold")[:6]
        )
        return context
