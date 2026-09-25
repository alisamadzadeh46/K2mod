from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.PhoneLoginView.as_view(), name="login"),
    path("logout/", views.PhoneLogoutView.as_view(), name="logout"),

    # password reset
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            email_template_name="registration/password_reset_email.txt",
            html_email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("addresses/", views.AddressListView.as_view(), name="addresses"),
    path("favorites/", views.FavoriteListView.as_view(), name="favorites"),
    path("my-comments/", views.MyCommentsView.as_view(), name="my_comments"),
    path("addresses/add/", views.AddressCreateView.as_view(), name="address_add"),
    path("addresses/<int:pk>/edit/", views.AddressUpdateView.as_view(), name="address_edit"),
    path("addresses/<int:pk>/delete/", views.AddressDeleteView.as_view(), name="address_delete"),
    path("addresses/<int:pk>/set-default/", views.AddressSetDefaultView.as_view(), name="address_set_default"),
]
