from django.urls import include, path
from event.participant import views

urlpatterns = [
    path('participant/', views.participants, name='participants'),
]
