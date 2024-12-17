from django.urls import include, path
from event.basic import views

urlpatterns = [
    path('basic/', views.event_main, name='event-main'),
]
