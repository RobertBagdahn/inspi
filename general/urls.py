from django.urls import include, path

urlpatterns = [
    path('footer/', include('general.footer.urls')),
    path('auth/', include('general.login.urls')),
]
