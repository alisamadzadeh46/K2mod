from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Max, Min, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView, View

from .forms import ProductCommentForm
from .models import Banner, Brand, Category, Color, Favorite, Product, ProductComment, Size


class HomeView(TemplateView):
    template_name = "catalog/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_products = Product.objects.filter(is_active=True, category__is_active=True)

        context["banners"] = Banner.objects.filter(is_active=True, placement=Banner.Placement.HERO)
        context["promo_banners"] = Banner.objects.filter(is_active=True, placement=Banner.Placement.PROMO)
        context["bestsellers"] = active_products.filter(badge=Product.Badge.BESTSELLER)[:10]
        context["new_arrivals"] = active_products.filter(badge=Product.Badge.NEW)[:10]
        context["deals"] = active_products.filter(badge=Product.Badge.SPECIAL_DISCOUNT)[:10]
        context["featured"] = active_products.filter(is_featured=True)[:10]
        context["enamad_codes"] = settings.ENAMAD_CODES
        return context


class CollectionView(ListView):
    model = Product
    template_name = "catalog/collection.html"
    context_object_name = "products"
    paginate_by = 12

    KINDS = {
        "bestsellers": ("پرفروش‌ترین محصولات", {"badge": Product.Badge.BESTSELLER}),
        "new": ("جدیدترین محصولات", {"badge": Product.Badge.NEW}),
        "deals": ("پیشنهادهای شگفت‌انگیز", {"badge": Product.Badge.SPECIAL_DISCOUNT}),
        "featured": ("منتخب فروشگاه", {"is_featured": True}),
    }

    def get_kind(self):
        if self.kwargs["kind"] not in self.KINDS:
            from django.http import Http404

            raise Http404("Unknown collection.")
        return self.kwargs["kind"]

    def get_queryset(self):
        _, filters = self.KINDS[self.get_kind()]
        return Product.objects.filter(is_active=True, category__is_active=True, **filters)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["collection_title"] = self.KINDS[self.get_kind()][0]
        return context


class CategoryProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 12

    def get_category(self):
        return get_object_or_404(Category, slug=self.kwargs["category_slug"], is_active=True)

    def get_queryset(self):
        category = self.get_category()
        # include subcategories
        category_ids = [category.pk] + list(category.children.values_list("pk", flat=True))
        queryset = Product.objects.filter(category_id__in=category_ids, is_active=True)

        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        brand_id = self.request.GET.get("brand")
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)

        color_id = self.request.GET.get("color")
        if color_id:
            queryset = queryset.filter(colors__id=color_id)

        size_id = self.request.GET.get("size")
        if size_id:
            queryset = queryset.filter(sizes__id=size_id)

        if self.request.GET.get("in_stock") == "1":
            queryset = queryset.filter(stock__gt=0)

        sort = self.request.GET.get("sort", "newest")
        sort_map = {
            "newest": "-created_at",
            "price_asc": "price",
            "price_desc": "-price",
            "name": "name",
        }
        return queryset.order_by(sort_map.get(sort, "-created_at"))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        category_ids = [category.pk] + list(category.children.values_list("pk", flat=True))
        products_in_category = Product.objects.filter(category_id__in=category_ids)

        context["category"] = category
        context["current_sort"] = self.request.GET.get("sort", "newest")
        # only brands/colors that exist in this category
        context["available_brands"] = Brand.objects.filter(products__in=products_in_category).distinct()
        context["available_colors"] = Color.objects.filter(color_products__in=products_in_category).distinct()
        context["available_sizes"] = Size.objects.filter(products__in=products_in_category).distinct()

        # price range for the slider
        bounds = products_in_category.aggregate(lo=Min("price"), hi=Max("price"))
        context["price_min_bound"] = int(bounds["lo"] or 0)
        context["price_max_bound"] = int(bounds["hi"] or 1000000)
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_products"] = (
            Product.objects.filter(category=self.object.category, is_active=True)
            .exclude(pk=self.object.pk)[:4]
        )
        context["comments"] = (
            self.object.comments.filter(parent__isnull=True, is_approved=True)
            .select_related("user")
            .prefetch_related("replies__user")
        )
        context["comment_form"] = ProductCommentForm()
        return context


class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug, is_active=True)
        form = ProductCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = product
            comment.user = request.user
            comment.save()  # needs approval
            messages.success(request, "نظر شما ثبت شد و پس از تأیید مدیر نمایش داده می‌شود.")
        else:
            messages.error(request, "ثبت نظر با خطا مواجه شد.")
        return redirect(product.get_absolute_url())


class ReplyToCommentView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, slug, comment_id):
        product = get_object_or_404(Product, slug=slug)
        parent = get_object_or_404(ProductComment, pk=comment_id, product=product, parent__isnull=True)
        body = request.POST.get("body", "").strip()
        if body:
            ProductComment.objects.create(product=product, user=request.user, parent=parent, body=body)
            messages.success(request, "پاسخ شما ثبت شد.")
        return redirect(product.get_absolute_url())


class SearchView(ListView):
    model = Product
    template_name = "catalog/search_results.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        self.query = query
        if not query:
            return Product.objects.none()
        return Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query), is_active=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.query
        return context


@require_POST
def toggle_favorite(request, slug):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "login_required"}, status=401)

    product = get_object_or_404(Product, slug=slug, is_active=True)
    favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)
    if not created:
        favorite.delete()
    return JsonResponse({"favorited": created, "count": request.user.favorites.count()})
