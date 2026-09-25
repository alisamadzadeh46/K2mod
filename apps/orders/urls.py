from django.urls import path

from . import views

app_name = "orders"

urlpatterns = [
    path("checkout/", views.CheckoutView.as_view(), name="checkout"),
    path("<int:pk>/confirmation/", views.OrderConfirmationView.as_view(), name="confirmation"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="detail"),
    path("history/", views.OrderHistoryView.as_view(), name="history"),
]
