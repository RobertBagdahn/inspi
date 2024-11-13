from django.contrib import admin

from .models import (
    MeasuringUnit,
    Price,
    Ingredient,
    Recipe,
    Portion,
    RecipeItem,
    Hint,
    MealEvent,
    Meal,
    MealDay,
    MealItem,
    MealEventTemplate,
    MetaInfo,
    Portion,
    Intolerance,
    TemplateOption,
)

admin.site.register(MeasuringUnit)
admin.site.register(Price)
admin.site.register(Portion)
admin.site.register(Ingredient)
admin.site.register(RecipeItem)


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    ordering = ["name"]
    readonly_fields = ("hints",)
    list_display = ("name", "status", "get_hints")
    list_filter = (
        "recipe_type",
        "status",
    )

    def get_hints(self, obj):
        return "\n, ".join([p.name for p in obj.hints.all()])

    inlines = [
        RecipeItemInline,
    ]



@admin.register(Hint)
class EventModuleAdmin(admin.ModelAdmin):
    search_fields = [
        "name",
        "description",
    ]
    list_display = (
        "name",
        "description",
        "parameter",
        "min_max",
        "value",
        "hint_level",
    )
    list_filter = ("parameter",)


admin.site.register(MealEvent)
admin.site.register(MealDay)
admin.site.register(Intolerance)
admin.site.register(TemplateOption)



@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "time_start",
        "time_end",
    )
    list_filter = ("meal_day",)


admin.site.register(MealItem)
admin.site.register(MealEventTemplate)

admin.site.register(MetaInfo)
