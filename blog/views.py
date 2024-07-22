from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Post, Category

# import CustomUser from login
from general.login.models import CustomUser as User

from .forms import PostForm


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
    context = {
        "post": post,
    }
    return render(request, "post.html", context)


def post_list(request):
    posts = Post.objects.all()
    context = {
        "posts": posts,
    }
    return render(request, "post_list.html", context)


def post_create(request):
    if request.method == "POST":
        # create a form instance and populate it with data from the request:
        form = PostForm(request.POST)


        if form.is_valid():
            # process the data in form.cleaned_data as required
            # fill author with the current user

            data = form.cleaned_data

            # remove categories from data
            categories = data.pop("categories")

            print('categories')
            print(categories)

            # create a new post
            post = Post(**data)
            post.author = User.objects.first()
            post.save()
            for category in categories:
                post.categories.add(category)

            return HttpResponseRedirect("/blog/post_dashboard/")

    # if a GET (or any other method) we'll create a blank form
    else:
        form = PostForm()

    return render(request, "post_create.html", {"form": form})


def post_dashboard(request):
    posts = Post.objects.all()
    statuschoice = Post._meta.get_field("status").choices
    context = {
        "posts": posts,
        "statuses": dict(statuschoice),
    }
    return render(request, "post_dashboard.html", context)
