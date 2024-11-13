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
    path("plan/<slug>/meal-detail/<id>/", views.meal_detail, name="plan-meal-detail"),

    path("template-create/", views.template_create, name="template-create"),
    path("template-update/<id>/", views.template_update, name="template-update"),

    path("meal-event-create/", views.meal_event_create, name="meal-event-create"),
    path("meal-event-clone", views.meal_event_clone, name="meal-event-clone"),

    path("recipe-list/", views.recipe_list, name="recipe-list"),
    
    path("recipe/<slug>/overview", views.recipe_detail_overview, name="recipe-detail-overview"),
    path("recipe/<slug>/analyse", views.recipe_detail_analyse, name="recipe-detail-analyse"),
    path("recipe/<slug>/shopping", views.recipe_detail_shopping, name="recipe-detail-shopping"),
    path("recipe/<slug>/comment", views.recipe_detail_comment, name="recipe-detail-comment"),
    
    path("recipes/", views.recipes, name="recipe-main"),
    path("recipe-create/", views.recipe_create, name="recipe-create"),
    path("recipe-update/<slug>/", views.recipe_update, name="recipe-update"),
    path("recipe-clone/<slug>", views.recipe_clone, name="recipe-clone"),

    path("recipe-item-create/<slug>", views.recipe_item_create, name="recipe-item-create"),
    path("recipe-item-update/<slug>", views.recipe_item_update, name="recipe-item-update"),
    path("recipe-item-delete/", views.recipe_item_delete, name="recipe-item-delete"),

    path("ingredient-create/", views.ingredient_create, name="ingredient-create"),
    path("ingredient-update/<slug>/", views.ingredient_update, name="ingredient-update"),
    path("ingredient/<slug>/", views.ingredient_detail, name="ingredient-detail"),
    path("ingredient-list/", views.ingredient_list, name="ingredient-list"),
    # add ingredient new portion
    path("ingredient/<slug>/portion-create/", views.ingredient_portion_create, name="ingredient-portion-create"),
    path("ingredient/<slug>/portion-update/<pk>", views.ingredient_portion_update, name="ingredient-portion-update"),
    path("ingredient/<slug>/price-create/", views.ingredient_price_create, name="ingredient-price-create"),
    path("ingredient/<slug>/price-update/<pk>", views.ingredient_price_update, name="ingredient-price-update"),

    # get_portions_by_ingredient
    path("portions-by-ingredient", views.get_portions_by_ingredient, name="portions-by-ingredient"),
]
