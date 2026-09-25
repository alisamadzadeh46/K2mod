from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View

from apps.cart.utils import merge_anonymous_cart
from apps.catalog.models import Favorite, ProductComment

from .forms import AddressForm, PhoneLoginForm, ProfileForm, RegisterForm
from .models import Address, CustomUser


class RegisterView(CreateView):
    model = CustomUser
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("catalog:home")

    def form_valid(self, form):
        # session key changes after login, keep it for merging the cart
        old_session_key = self.request.session.session_key
        response = super().form_valid(form)
        # backend has to be set explicitly because of axes
        login(self.request, self.object, backend="django.contrib.auth.backends.ModelBackend")
        merge_anonymous_cart(self.object, old_session_key)
        messages.success(self.request, "حساب کاربری شما با موفقیت ساخته شد. خوش آمدید!")
        return response


class PhoneLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = PhoneLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        old_session_key = self.request.session.session_key
        messages.success(self.request, f"سلام {form.get_user().get_short_name()}، خوش آمدید!")
        response = super().form_valid(form)
        merge_anonymous_cart(self.request.user, old_session_key)
        return response


class PhoneLogoutView(LogoutView):
    next_page = reverse_lazy("catalog:home")


class ProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")
    extra_context = {"active_account_tab": "profile"}

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "اطلاعات حساب با موفقیت به‌روزرسانی شد.")
        return super().form_valid(form)


class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = "accounts/addresses.html"
    context_object_name = "addresses"
    extra_context = {"active_account_tab": "addresses"}

    def get_queryset(self):
        return self.request.user.addresses.all()


class FavoriteListView(LoginRequiredMixin, ListView):
    template_name = "accounts/favorites.html"
    context_object_name = "products"
    extra_context = {"active_account_tab": "favorites"}

    def get_queryset(self):
        return [f.product for f in Favorite.objects.filter(user=self.request.user).select_related("product")]


class MyCommentsView(LoginRequiredMixin, ListView):
    template_name = "accounts/my_comments.html"
    context_object_name = "comments"
    paginate_by = 10
    extra_context = {"active_account_tab": "comments"}

    def get_queryset(self):
        return (
            ProductComment.objects.filter(user=self.request.user, parent__isnull=True)
            .select_related("product")
            .prefetch_related("replies")
            .order_by("-created_at")
        )


class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    form_class = AddressForm
    template_name = "accounts/address_form.html"
    success_url = reverse_lazy("accounts:addresses")

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "آدرس با موفقیت افزوده شد.")
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = "accounts/address_form.html"
    success_url = reverse_lazy("accounts:addresses")

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "آدرس با موفقیت ویرایش شد.")
        return super().form_valid(form)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    template_name = "accounts/address_confirm_delete.html"
    success_url = reverse_lazy("accounts:addresses")

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def form_valid(self, form):
        # Order.address is PROTECT
        if self.get_object().orders.exists():
            messages.error(self.request, "این آدرس در یک سفارش استفاده شده و قابل حذف نیست.")
            return redirect("accounts:addresses")
        response = super().form_valid(form)
        messages.success(self.request, "آدرس حذف شد.")
        return response


class AddressSetDefaultView(LoginRequiredMixin, View):
    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user)
        address.is_default = True
        address.save()
        messages.success(request, f"«{address.title}» به عنوان آدرس پیش‌فرض انتخاب شد.")
        return redirect("accounts:addresses")
