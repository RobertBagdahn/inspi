from django.contrib import admin
from django.contrib.admin import display
from copy import deepcopy

from anmelde_tool.registration.models import Registration, RegistrationParticipant


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'scout_organisation', 'is_confirmed', 'created_at', 'updated_at')
    list_filter = ('event', 'is_confirmed')
    search_fields = ('scout_organisation__name',)
    date_hierarchy = 'created_at'

@admin.register(RegistrationParticipant)
class RegistrationParticipantAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'scout_name', 'registration', 'booking_option', 'gender', 'scout_level')
    list_filter = ('registration__event', 'gender', 'scout_level', 'leader', 'generated')
    search_fields = ('first_name', 'last_name', 'scout_name', 'email', 'registration__scout_organisation__name')
    date_hierarchy = 'created_at'