# myapi/urls.py
from django.urls import include, re_path, path
from pictures.conf import get_settings

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # redirect to the overview/ page
    path('main/', include('activity.activity.urls')),
    path('event_of_week', include('activity.event_of_week.urls')),
]

if get_settings().USE_PLACEHOLDERS:
    urlpatterns += [
        path("_pictures/", include("pictures.urls")),
    ]