from django.db.models import Q, QuerySet
from django_filters import CharFilter, NumberFilter
from food.choices import Gender
from django.shortcuts import render

from copy import deepcopy
from itertools import groupby
from datetime import date, timedelta
import datetime



# create view with template main.html


def mainView(request):
    return render(request, 'main.html')