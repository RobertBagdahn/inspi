from datetime import date

from django.db.models.functions import ExtractMonth, ExtractYear
from django_filters import FilterSet, BooleanFilter, ModelMultipleChoiceFilter, NumberFilter, BaseInFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import pagination, viewsets, mixins, filters, status
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import render
from django.views.generic import ListView

from django.http import HttpResponse

from activity.activity import models as activity_models

from django.http import Http404
from django.core.paginator import Paginator

from django.template import loader


def list(request):
    latest_list = activity_models.Activity.objects.order_by("-created_at")[:10]
    template = loader.get_template("activity/list.html")
    context = {
        "latest_question_list": latest_list,
    }
    return HttpResponse(template.render(context, request))


def detail(request, activity_id):
    try:
        activity = activity_models.Activity.objects.get(pk=activity_id)
    except activity_models.Activity.DoesNotExist:
        raise Http404("Question does not exist")
    return render(request, "activity/detail.html", {"activity": activity})


def overview(request):
    query = request.GET.get('q', '')
    page_num = request.GET.get('page', 1)
    activities_raw = activity_models.Activity.objects.filter(title__icontains=query).order_by("-created_at")
    paginator = Paginator(activities_raw, per_page=5)
    page_object = paginator.get_page(page_num)
    page_object.adjusted_elided_pages = paginator.get_elided_page_range(page_num)

    context = {
        "activities": page_object,
        "page_object": page_object,
    }
    return render(request, "activity/overview.html", context)


def faq(request):
    template = loader.get_template("footer/faq.html")
    context = {}
    return HttpResponse(template.render(context, request))