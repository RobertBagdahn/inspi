from django.contrib import admin

from imagekit.admin import AdminThumbnail
from .models import Profile
from image_cropping import ImageCroppingMixin

from .models import (
    Topic,
    TagCategory,
    Activity,
    MaterialItem,
    ExperimentItem,
    Experiment,
    MaterialName,
    MaterialUnit,
    ScoutLevelChoice,
    ActivityTypeChoice,
    LocationChoice,
    TimeChoice,
    Comment,
    Emotion,

)

class MyModelAdmin(ImageCroppingMixin, admin.ModelAdmin):
    pass

@admin.register(Activity)
class ActivityAdmin(MyModelAdmin, admin.ModelAdmin):
    list_display = (
        "title",
        "summary",
        "summary_long",
        "is_public",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_public",)
    search_fields = (
        "title",
        "description",
    )
    date_hierarchy = "created_at"

admin.site.register(TagCategory)

admin.site.register(Experiment)
admin.site.register(ExperimentItem)

admin.site.register(MaterialItem)
admin.site.register(MaterialUnit)
admin.site.register(MaterialName)
admin.site.register(Emotion)


@admin.register(Topic)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description",
        "sorting",
        "is_public",
    )
    list_filter = ("is_public",)
    search_fields = (
        "name",
        "description",
    )


class ProfileAdmin(admin.ModelAdmin):
    list_display = ("__str__", "admin_thumbnail")
    admin_thumbnail = AdminThumbnail(image_field="avatar_thumbnail")


admin.site.register(Profile, ProfileAdmin)

admin.site.register(ScoutLevelChoice)
admin.site.register(ActivityTypeChoice)
admin.site.register(LocationChoice)
admin.site.register(TimeChoice)
admin.site.register(Comment)
