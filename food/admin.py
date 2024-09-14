from django.contrib import admin

from .models import (
    MeasuringUnit,
    PackagePrice,
    Tag,
    TagCategory,
    Ingredient,
    Recipe,
    Portion,
    Retailer,
    Package,
    RecipeItem,
    Hint,
    MealEvent,
    Meal,
    MealDay,
    MealItem,
    PhysicalActivityLevel,
    PollItem,
    MealEventTemplate,
    TemplateOptions,
    MetaInfo,
)

admin.site.register(MeasuringUnit)
admin.site.register(Tag)
admin.site.register(TagCategory)
admin.site.register(PhysicalActivityLevel)


class PortionInline(admin.TabularInline):
    model = Portion
    ordering = ["name"]


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    ordering = ["name"]
    list_display = (
        "name",
        "description",
    )
    list_filter = ()

    inlines = [
        PortionInline,
    ]


class RecipeItemInline(admin.TabularInline):
    model = RecipeItem


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    ordering = ["name"]
    readonly_fields = ("hints",)
    list_display = ("name", "status", "get_hints")
    list_filter = (
        "meal_type",
        "status",
    )

    def get_hints(self, obj):
        return "\n, ".join([p.name for p in obj.hints.all()])

    inlines = [
        RecipeItemInline,
    ]


class PackagePriceInline(admin.TabularInline):
    model = PackagePrice
    readonly_fields = ("price_per_kg",)


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    ordering = ["portion"]

    inlines = [
        PackagePriceInline,
    ]


admin.site.register(Retailer)


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


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "time_start",
        "time_end",
    )
    list_filter = ("meal_day",)


admin.site.register(MealItem)
admin.site.register(PollItem)
admin.site.register(MealEventTemplate)
admin.site.register(TemplateOptions)

admin.site.register(MetaInfo)
