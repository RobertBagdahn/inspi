from django.contrib import admin

from imagekit.admin import AdminThumbnail
from .models import Profile

from .models import Tag, TagCategory, Activity, MaterialItem, ExperimentItem, Experiment, MaterialName, MaterialUnit

@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "summary",
        "is_public",
        "created_at",
        "updated_at",
    )
    list_filter = ('is_public',)
    search_fields = ('title', 'description', )
    date_hierarchy = "created_at"

admin.site.register(TagCategory)

admin.site.register(Experiment)
admin.site.register(ExperimentItem)

admin.site.register(MaterialItem)
admin.site.register(MaterialUnit)
admin.site.register(MaterialName)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "color",
        "sorting",
        "is_public",
    )
    list_filter = ('category', 'is_public',)
    search_fields = ('name', 'description', )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'admin_thumbnail')
    admin_thumbnail = AdminThumbnail(image_field='avatar_thumbnail')


admin.site.register(Profile, ProfileAdmin)