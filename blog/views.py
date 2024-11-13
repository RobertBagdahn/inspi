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

from .forms import PostForm, SearchForm, CommentForm, PostFormUpdate
from .models import Comment as PostComment
from .choices import StatusTypeWithAll


def mainView(request, slug: str = None):
    categories = Category.objects.all()
    latest = Post.objects.filter(status=StatusTypeWithAll.PUBLISHED).order_by("-timestamp_created")[0:4]
    most_famous = Post.objects.filter(status=StatusTypeWithAll.PUBLISHED).order_by("-words")[0:4]
    randoms = Post.objects.filter(status=StatusTypeWithAll.PUBLISHED).order_by("?")[0:4]
    context = {
        "object_list": latest,
        "latest": latest,
        "most_famous": most_famous,
        "randoms": randoms,
        "categories": categories,
    }
    return render(request, "blog-home.html", context)


def post(request, slug):
    post = Post.objects.get(slug=slug)
    post.update_views()
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

        print(form.is_valid())

        if form.is_valid():

            data = form.cleaned_data
            data["slug"] = data["title"].replace(" ", "-").lower()

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
        form = PostFormUpdate(request.POST, instance=post)

        if form.is_valid():
            data = form.cleaned_data

            # remove categories from data
            categories = data.pop("categories")

            form.save()
            for category in categories:
                # add categories to post if they are not already there
                if category not in post.categories.all():
                    post.categories.add(category)

            return HttpResponseRedirect("/blog/post-dashboard/")

        else:
            messages.error(
                request,
                f"Form is not valid. Please check the form {[field for field in form.errors]}",
            )

        return render(request, "post-update.html", {"form": form})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PostFormUpdate(instance=post)
        return render(request, "post-update.html", {"form": form})


def post_delete(request, slug):
    post = Post.objects.get(slug=slug)
    if not post.is_allowed_to_edit(request.user):
        messages.error(request, "You are not allowed to delete this post")
        return redirect("post-dashboard")
    post.delete()
    messages.success(request, "Post deleted")
    return redirect("post-dashboard")


def post_dashboard(request):
    posts = Post.objects.all()
    form = SearchForm(request.GET or None, initial={"status": "all"})
    categories = Category.objects.all()

    if form.is_valid():
        if form.cleaned_data["query"] and form.cleaned_data["query"] is not None:
            posts = posts.filter(title__icontains=form.cleaned_data["query"])

        if form.cleaned_data["status"] and form.cleaned_data["status"] != "all":
            posts = posts.filter(status=form.cleaned_data["status"])

    context = {
        "posts": posts,
        "form": form,
        "categories": categories,
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


def post_archive(request, slug):
    me = request.user
    post = Post.objects.get(slug=slug)
    if not post.is_allowed_to_edit(me):
        messages.error(request, "You are not allowed to archive this post")
        return redirect("post-dashboard")
    post.status = "archived"
    post.save()
    messages.success(request, "Post archived")
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
