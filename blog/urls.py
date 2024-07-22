from django.urls import include, path

from . import views

urlpatterns = [
    path("posts", views.mainView, name="blog-main"),
    path('post/<slug>/', views.post, name = 'post'),
    path('post_list/', views.post_list, name = 'post_list'),
    path('post_create/', views.post_create, name = 'post_create'),
    path('post_dashboard/', views.post_dashboard, name = 'post_dashboard'),
]
