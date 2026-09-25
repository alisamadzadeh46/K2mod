from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("collection/<str:kind>/", views.CollectionView.as_view(), name="collection"),
    path("faq/", TemplateView.as_view(template_name="pages/faq.html"), name="faq"),
    path("returns/", TemplateView.as_view(template_name="pages/returns.html"), name="returns"),
    path("privacy/", TemplateView.as_view(template_name="pages/privacy.html"), name="privacy"),
    # str instead of slug because slugs can be persian
    path("c/<str:category_slug>/", views.CategoryProductListView.as_view(), name="product_list"),
    path("p/<str:slug>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("p/<str:slug>/favorite/", views.toggle_favorite, name="toggle_favorite"),
    path("p/<str:slug>/comment/", views.AddCommentView.as_view(), name="add_comment"),
    path("p/<str:slug>/comment/<int:comment_id>/reply/", views.ReplyToCommentView.as_view(), name="reply_comment"),
]
