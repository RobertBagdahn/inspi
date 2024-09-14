from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.mainView, name="blog-main"),
    path("post/<slug>/", views.post, name="post"),
    path("post-list/", views.post_list, name="post-list"),
    path("post-create/", views.post_create, name="post-create"),
    path("post-update/<slug>/", views.post_update, name="post-update"),
    path("post-dashboard/", views.post_dashboard, name="post-dashboard"),
    path("post-publish/<slug>/", views.post_publish, name="post-publish"),
    path("comment/create/", views.comment_create, name="comment-create"),
]
