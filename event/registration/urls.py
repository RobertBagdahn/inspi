from django.urls import include, path
from event.registration import views

urlpatterns = [
    path('registration/', views.registrations, name='registration'),
]
