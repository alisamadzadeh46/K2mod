from .models import Category, Favorite


def nav_categories(request):
    return {"nav_categories": Category.objects.filter(is_active=True, parent__isnull=True)}


def favorites(request):
    if request.user.is_authenticated:
        ids = set(Favorite.objects.filter(user=request.user).values_list("product_id", flat=True))
    else:
        ids = set()
    return {"favorite_ids": ids}
