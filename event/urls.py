from django.urls import include, path

urlpatterns = [
    path('', include('event.basic.urls')),
    path('registration', include('event.registration.urls')),
    path('participant', include('event.participant.urls')),

]
