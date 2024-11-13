from django.urls import include, path

from . import views

urlpatterns = [
    path(
        "user-profile/<username>/", views.user_profile, name="login-profile"
    ),
    path(
        "profile-edit/<username>/",
        views.profile_edit,
        name="login-profile-edit",
    ),
    path(
        "profile-delete/<username>/",
        views.profile_delete,
        name="login-profile-delete",
    ),
    path("settings/<username>/", views.settings, name="login-settings"),
]
