from django.contrib import admin

from anmelde_tool.event.basic.models import (
    Event,
    BookingOption,
    EventModule,
    StandardEventTemplate,
    EventPermission,
    EventRegistrationType,
)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "start_date", "end_date", "is_public")
    search_fields = ("name", "short_description")
    list_filter = ("is_public", "location")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(EventModule)
class EventModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "header", "event", "ordering", "required", "standard")
    list_filter = ("required", "standard", "allow_multiply", "event")
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


@admin.register(EventRegistrationType)
class EventRegistrationTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name", "description")
