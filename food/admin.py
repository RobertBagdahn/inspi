from django.contrib import admin

from .models import (
    MeasuringUnit,
    Price,
    Ingredient,
    Recipe,
    Portion,
    RecipeItem,
    RecipeHint,
    MealEvent,
    Meal,
    MealDay,
    MealItem,
    MealEventTemplate,
    MetaInfo,
    Portion,
    NutritionalTag,
    TemplateOption,
    RetailSection,
)

admin.site.register(MeasuringUnit)
admin.site.register(Price)
admin.site.register(Portion)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ("name",)


admin.site.register(RecipeItem)


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem
    fk_name = 'recipe'  # Specify which ForeignKey to use


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


@admin.register(RecipeHint)
class RecipeHintAdmin(admin.ModelAdmin):
    search_fields = [
        "hint",
        "improvement",
    ]
    list_display = (
        "hint",
        "parameter",
        "min_max",
        "value",
        "hint_level",
        "recipe_type",
        "recipe_objective",
    )
    list_filter = (
        "parameter",
        "hint_level",
        "min_max",
        "recipe_type",
        "recipe_objective",
    )


admin.site.register(MealEvent)
admin.site.register(MealDay)
admin.site.register(NutritionalTag)
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

@admin.register(MetaInfo)
class MetaInfoAdmin(admin.ModelAdmin):
    search_fields = ["id"]
    list_display = ("id",)
admin.site.register(RetailSection)
