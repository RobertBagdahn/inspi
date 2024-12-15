from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.mainView, name="food-main"),
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

    path("plan/<slug>/meal/<id>/overview", views.meal_detail_overview, name="meal-detail-overview"),
    path("plan/<slug>/meal/<id>/analyse", views.meal_detail_overview, name="meal-detail-analyse"),
    path("plan/<slug>/meal/<i>/shopping", views.meal_detail_overview, name="meal-detail-shopping"),
    path("plan/<slug>/meal/<id>/comment", views.meal_detail_overview, name="recipe-detail-comment"),

    path("meal-event-create/", views.meal_event_create, name="meal-event-create"),
    path("meal-event-clone", views.meal_event_clone, name="meal-event-clone"),

    path("meal-event-update/<id>/", views.meal_event_update, name="meal-event-update"),
    path("meal-event-delete/", views.meal_event_delete, name="meal-event-delete"),

    # meal update and delete, create
    path("meal-create/<meal_day_id>/", views.meal_create, name="meal-create"),
    path("meal-update/<id>/", views.meal_update, name="meal-update"),
    path("meal-delete/<id>/", views.meal_delete, name="meal-delete"),

    # meal-item-create
    path("meal-item-create/", views.meal_item_create, name="meal-item-create"),
    path("meal-item-update/<id>/", views.meal_item_update, name="meal-item-update"),

    # meal-day update and delete
    path("meal-day-update/<id>/", views.meal_day_update, name="meal-day-update"),
    path("meal-day-delete/<id>/", views.meal_day_delete, name="meal-day-delete"),

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

    # admin
    path("admin/main", views.admin_main, name="food-admin-main"),
]
