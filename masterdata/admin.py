from django.contrib import admin
from .models import ScoutHierarchy, EventLocation, NutritionalTag, ZipCode

from django.utils.html import format_html

@admin.register(ScoutHierarchy)
class ScoutHierarchyAdmin(admin.ModelAdmin):
    list_display = ("name", "abbreviation", "full_name", "zip_code")
    search_fields = ("name", "abbreviation", "full_name")

@admin.register(EventLocation)
class EventLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "zip_code", "address", "contact_name")
    search_fields = ("name", "address", "contact_name", "contact_email")


@admin.register(NutritionalTag)
class NutritionalTagAdmin(admin.ModelAdmin):
    list_display = ("name", "name_opposite", "rank", "is_dangerous")
    search_fields = ("name", "name_opposite", "description")
    list_filter = ("is_dangerous",)

@admin.register(ZipCode)
class ZipCodeAdmin(admin.ModelAdmin):
    list_display = ("zip_code", "city")
    search_fields = ("zip_code", "city")
