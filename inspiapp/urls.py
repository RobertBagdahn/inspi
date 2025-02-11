"""
URL configuration for inspi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import TemplateView
from django.urls import re_path

from django.contrib.sitemaps.views import sitemap
from activity.sitemaps import ActivitySitemap

from .views import index, search, autocompleteModel

sitemaps = {
    "activitys": ActivitySitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("activity/", include("activity.urls")),
    path("general/", include("general.urls")),
    path("event/", include("event.urls")),
    path("food/", include("food.urls")),
    path("blog/", include("blog.urls")),
    path("group/", include("group.urls")),
    path("", index, name="index"),
    path("accounts/", include("allauth.urls")),
    path("__reload__/", include("django_browser_reload.urls")),
    path("search", search, name="global-search"),
    path("autocomplete", autocompleteModel, name="autocomplete"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
    re_path(r'^tracking/', include('tracking.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
