import json

from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseRedirect
from .models import Post, Category
from django.db.models import Q
from django.views import generic
from django.utils.formats import date_format
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from django.views.generic.base import TemplateView
from django.contrib import messages

# import CustomUser from login
from general.login.models import CustomUser as User

from .forms import PostForm, SearchForm, CommentForm
from .models import Comment as PostComment


def mainView(request):
    categories = Category.objects.all()[0:3]
    latest = Post.objects.order_by("-timestamp_created")[0:3]
    context = {
        "object_list": latest,
        "latest": latest,
        "categories": categories,
    }
    return render(request, "blog-home.html", context)


def post(request, slug):
    post = Post.objects.get(slug=slug)
    comment_form = CommentForm()
    related_posts = Post.objects.all().order_by("?")[:3]
    context = {
        "post": post,
        "comment_form": comment_form,
        "related_posts": related_posts,
    }
    return render(request, "post.html", context)


def post_list(request):
    posts = Post.objects.all()
    context = {
        "posts": posts,
    }
    return render(request, "post-list.html", context)


def post_create(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = PostForm(request.POST)

        if form.is_valid():

            data = form.cleaned_data

            data["slug"] = data["title"].replace(" ", "-").lower()

            # remove categories from data
            categories = data.pop("categories")

            # create a new post
            post = Post(**data)
            post.author = User.objects.first()
            post.save()
            for category in categories:
                post.categories.add(category)

            return HttpResponseRedirect("/blog/post-dashboard/")

        return render(request, "post-create.html", {"form": form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PostForm()
        return render(request, "post-create.html", {"form": form})


def post_update(request, slug):
    post = Post.objects.get(slug=slug)
    if not post.is_allowed_to_edit(request.user):
        messages.error(request, "You are not allowed to edit this post")
        return redirect("post-dashboard")

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            data = form.cleaned_data
            data["slug"] = data["title"].replace(" ", "-").lower()

            # remove categories from data
            categories = data.pop("categories")

            post = Post(**data)
            post.author = User.objects.first()
            post.save()
            for category in categories:
                post.categories.add(category)

            return HttpResponseRedirect("/blog/post-dashboard/")

        return render(request, "post-create.html", {"form": form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PostForm(instance=post)
        return render(request, "post-create.html", {"form": form})


def post_dashboard(request):
    posts = Post.objects.all()
    form = SearchForm(request.GET, initial={"status": "all"})

    if form.is_valid():
        if form.cleaned_data["query"] and form.cleaned_data["query"] is not None:
            posts = posts.filter(title__icontains=form.cleaned_data["query"])

        if form.cleaned_data["status"] and form.cleaned_data["status"] != "all":
            posts = posts.filter(status=form.cleaned_data["status"])

    context = {
        "posts": posts,
        "form": form,
    }
    return render(request, "post-dashboard.html", context)


def post_publish(request, slug):
    me = request.user
    post = Post.objects.get(slug=slug)
    if not post.is_allowed_to_edit(me):
        messages.error(request, "You are not allowed to publish this post")
        return redirect("post-dashboard")
    post.status = "published"
    post.save()
    messages.success(request, "Post published")
    return redirect("post-dashboard")


def comment_create(request):
    data = json.loads(request.body)
    post_id = data["post_id"]
    content = data["content"]

    post = get_object_or_404(Post, id=post_id)
    comment = PostComment.objects.create(
        author=request.user, content=content, post=post
    )

    return JsonResponse(
        {
            "author": comment.author.username,
            "content": comment.content,
            "timestamp": date_format(comment.date_posted, "SHORT_DATETIME_FORMAT"),
        }
    )
