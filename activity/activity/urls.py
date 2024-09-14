# myapi/urls.py
from django.urls import include, re_path, path
from pictures.conf import get_settings

from activity.activity import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # redirect to the overview/ page
    path("", views.main_view, name="activity-main"),
    path("all-items", views.all_items, name="activity-all-items"),
    path("details/<int:activity_id>", views.detail, name="activity-detail"),
    path("list", views.list, name="activity-list"),
    path("faq", views.faq, name="footer-faq"),
]

if get_settings().USE_PLACEHOLDERS:
    urlpatterns += [
        path("_pictures/", include("pictures.urls")),
    ]
