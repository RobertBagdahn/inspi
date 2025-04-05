from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import JsonResponse

from blog.models import Post
from activity.activity.models import Activity

from django.db.models import Q


def index(request):
    return render(request, "index.html")


def search(request):
    return render(request, "search.html")


def autocompleteModel(request):
    is_ajax_request = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if is_ajax_request:
        q = request.GET.get("q", "")
        q = q.strip()

        # less than 3 characters
        if len(q) <= 3:
            html = render_to_string(
                template_name="components/results-partial.html",
                context={"error": "Mehr als 3 Zeichen eingeben"},
            )

            data_dict = {"html_from_view": html}

            return JsonResponse(data=data_dict, safe=False)

        if q != "":
            search_qs = Post.objects.filter(
                Q(title__icontains=q)
                | Q(content__icontains=q)
                | Q(author__scout_display_name__icontains=q)
                | Q(categories__title__contains=q)
                | Q(overview__icontains=q)
            )
            search_qs = list(search_qs.values())
            search_acty = Activity.objects.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(authors__scout_display_name__icontains=q)
                | Q(summary__icontains=q)
            )
            search_acty = list(search_acty.values())
        else:
            search_qs = []
            search_acty = []

        html = render_to_string(
            template_name="components/results-partial.html",
            context={
                "posts": search_qs,
                "activities": search_acty,
                "error": "",
            },
        )

        data_dict = {"html_from_view": html}

        return JsonResponse(data=data_dict, safe=False)

    return render(request, "artists.html")
