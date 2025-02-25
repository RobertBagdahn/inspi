from django.urls import path
from event.basic import views

urlpatterns = [
    path('basic/', views.event_main, name='event-main'),
    path('details/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    path('create/', views.event_create, name='event_create'),
]
