from django.contrib import admin
from django.contrib.admin import display
from copy import deepcopy

from anmelde_tool.registration.models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'scout_organisation', 'created_at', 'updated_at',)
    list_filter = ('event',)
    search_fields = ('scout_organisation__name',)
    date_hierarchy = 'created_at'
