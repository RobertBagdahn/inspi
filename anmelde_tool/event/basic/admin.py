from django.contrib import admin

from anmelde_tool.event.basic.models import (
    EventLocation,
    Event,
    BookingOption,
    EventModule,
    StandardEventTemplate,
    EventPermission,
)


@admin.register(EventLocation)
class EventLocationAdmin(admin.ModelAdmin):
    list_display = ("name", "zip_code", "address", "contact_name")
    search_fields = ("name", "address", "contact_name", "contact_email")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "start_date", "end_date", "is_public")
    search_fields = ("name", "short_description")
    list_filter = ("is_public", "location")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(EventModule)
class EventModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "header", "event", "ordering", "required", "standard")
    list_filter = ("required", "standard", "internal", "event")
    search_fields = ("name", "header", "description")


@admin.register(BookingOption)
class BookingOptionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "event",
        "price",
        "bookable_from",
        "bookable_till",
        "max_participants",
    )
    list_filter = ("event",)
    search_fields = ("name", "description")


@admin.register(StandardEventTemplate)
class StandardEventTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "introduction", "summary", "participants", "letter")
    search_fields = ("name",)

    @admin.register(EventPermission)
    class EventPermissionAdmin(admin.ModelAdmin):
        list_display = (
            "event",
            "user",
            "permission_type",
            "include_subgroups",
            "created_at",
            "created_by",
        )
        list_filter = ("permission_type", "include_subgroups")
