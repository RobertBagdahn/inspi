from django.shortcuts import render
from django.http import HttpResponse
import json
from django.template.loader import render_to_string
from django.http import JsonResponse

from blog.models import Post


def index(request):
    return render(request, "index.html")


def search(request):
    return render(request, "search.html")


def autocompleteModel(request):
    is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if is_ajax_request:
        q = request.GET.get("q", "").capitalize()
        if q != "":
            search_qs = Post.objects.filter(title__contains=q)
            search_qs = list(search_qs.values())
        else:
            search_qs = []

        html = render_to_string(
            template_name="components/results-partial.html",
            context={"artists": search_qs},
        )

        data_dict = {"html_from_view": html}

        return JsonResponse(data=data_dict, safe=False)

    return render(request, "artists.html")
