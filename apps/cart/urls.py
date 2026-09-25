from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.CartDetailView.as_view(), name="detail"),
    path("add/", views.add_item, name="add_item"),
    path("items/<int:item_id>/update/", views.update_item, name="update_item"),
    path("items/<int:item_id>/remove/", views.remove_item, name="remove_item"),
]
