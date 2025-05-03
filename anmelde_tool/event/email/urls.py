from django.urls import include, path
from . import views

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('email-send-confirmation/', views.event_email_send_confirmation, name='email_send_confirmation'),
    path('email-send-confirm/', views.event_email_send_confirm, name='event_email_send_confirm'),
]
