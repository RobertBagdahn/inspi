from django.urls import include, path

from . import views

urlpatterns = [
    path(
        "user-profile/<scout_display_name>/", views.user_profile, name="login-profile"
    ),
    path(
        "profile-edit/<scout_display_name>/",
        views.profile_edit,
        name="login-profile-edit",
    ),
    path("settings/<scout_display_name>/", views.settings, name="login-settings"),
]
