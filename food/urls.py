from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.mainView, name="food-main"),
    path("plan-overview/", views.plan_overview, name="plan-overview"),
    path("plan-create/", views.plan_create, name="plan-create"),
    path("plan-dashboard/", views.plan_dashboard, name="plan-dashboard"),
    path("plan/<slug>/", views.plan, name="plan"),
    path("plan/<slug>/editor", views.plan_editor, name="plan-editor"),
    path(
        "plan/<slug>/shopping-chart/",
        views.plan_shopping_cart,
        name="plan-shopping-chart",
    ),
    path(
        "plan/<slug>/participants/", views.plan_participants, name="plan-participants"
    ),
    path("template-create/", views.template_create, name="template-create"),
    path("meal-event-create/", views.meal_event_create, name="meal-event-create"),
    path("meal-event-clone", views.meal_event_clone, name="meal-event-clone"),
    path("recipe-list/", views.recipe_list, name="recipe-list"),
    path("recipe/<slug>/", views.recipe_detail, name="recipe-detail"),
    path("recipes/", views.recipes, name="recipe-main"),
    path("ingredient-create/", views.ingredient_create, name="ingredient-create"),
    path("ingredient/<slug>/", views.ingredient_detail, name="ingredient-detail"),
    path("ingredient-list/", views.ingredient_list, name="ingredient-list"),
]
