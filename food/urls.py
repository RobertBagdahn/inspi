from django.urls import include, path

from . import views

from food.forms import (
    IngredientIntroForm,
    IngredientBasicInfoForm,
    IngredientPhysicalPropertiesForm,
    IngredientNutritionalTagsForm,
    IngredientScoresForm,
    IngredientRecipeInfoForm,
    IngredientNutritionForm,
    IngredientManagementForm,
)

form_list = [
    ("intro", IngredientIntroForm),
    ("basic_info", IngredientBasicInfoForm),
    ("physical_properties", IngredientPhysicalPropertiesForm),
    ("nutritional_tags", IngredientNutritionalTagsForm),
    ("scores", IngredientScoresForm),
    ("recipe_info", IngredientRecipeInfoForm),
    ("nutrition", IngredientNutritionForm),
    ("management", IngredientManagementForm),
]

urlpatterns = [
    path("main", views.mainView, name="food-main"),
    path("dashboard", views.food_dashboard, name="food-dashboard"),
    path("plan-create/", views.plan_create, name="plan-create"),
    path("plan-dashboard/", views.plan_dashboard, name="plan-dashboard"),
    # plan detail
    path(
        "plan/<slug>/overview", views.plan_detail_overview, name="plan-detail-overview"
    ),
    path(
        "plan/<slug>/participant",
        views.plan_detail_participant,
        name="plan-detail-participant",
    ),
    path(
        "plan/<slug>/plan-editor",
        views.plan_detail_plan_editor,
        name="plan-detail-plan-editor",
    ),
    path(
        "plan/<slug>/shopping-list",
        views.plan_detail_shopping_list,
        name="plan-detail-shopping-list",
    ),
    path(
        "plan/<slug>/time-table",
        views.plan_detail_time_table,
        name="plan-detail-time-table",
    ),
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
    path(
        "plan/<slug>/meal/<id>/overview",
        views.meal_detail_overview,
        name="meal-detail-overview",
    ),
    path(
        "plan/<slug>/meal/<id>/analyse",
        views.meal_detail_overview,
        name="meal-detail-analyse",
    ),
    path(
        "plan/<slug>/meal/<id>/shopping",
        views.meal_detail_overview,
        name="meal-detail-shopping",
    ),
    path(
        "plan/<slug>/meal/<id>/comment",
        views.meal_detail_overview,
        name="recipe-detail-comment",
    ),
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
    path(
        "recipe/<slug>/overview",
        views.recipe_detail_overview,
        name="recipe-detail-overview",
    ),
    path(
        "recipe/<slug>/analyse",
        views.recipe_detail_analyse,
        name="recipe-detail-analyse",
    ),
    path(
        "recipe/<slug>/checks",
        views.recipe_detail_checks,
        name="recipe-detail-checks",
    ),
    path(
        "recipe/<slug>/shopping",
        views.recipe_detail_shopping,
        name="recipe-detail-shopping",
    ),
    path(
        "recipe/<slug>/comment",
        views.recipe_detail_comment,
        name="recipe-detail-comment",
    ),
    path(
        "recipe/<slug>/manage",
        views.recipe_detail_manage,
        name="recipe-detail-manage",
    ),
    path("recipes/", views.recipes, name="recipe-main"),
    path("recipe-create/", views.recipe_create, name="recipe-create"),
    path("recipe/<slug>/update", views.recipe_update, name="recipe-update"),
    path("recipe-clone/<slug>", views.recipe_clone, name="recipe-clone"),
    path("recipe-scale/<slug>", views.recipe_scale, name="recipe-scale"),
    path("recipe-delete/<slug>", views.recipe_delete, name="recipe-delete"),
    path(
        "recipe-item-create/<slug>", views.recipe_item_create, name="recipe-item-create"
    ),
    path(
        "recipe-item-update/<slug>", views.recipe_item_update, name="recipe-item-update"
    ),
    # recipe_update_meta_infos
    path(
        "recipe-update-meta-infos/<slug>/",
        views.recipe_update_meta_infos,
        name="recipe-update-meta-infos",
    ),
    path("search/results/", views.search_results_view, name="search_results_view"),
    path(
        "ingredient-create-choice/",
        views.ingredient_create_choice,
        name="ingredient-create-choice",
    ),
    path("ingredient-create/", views.ingredient_create, name="ingredient-create"),
    path(
        "ingredient-create-copy/",
        views.ingredient_create_copy,
        name="ingredient-create-copy",
    ),
    path(
        "ingredient-create-ai/", views.ingredient_create_ai, name="ingredient-create-ai"
    ),
    path(
        "ingredients/autocomplete/",
        views.ingredients_autocomplete,
        name="ingredients-autocomplete",
    ),
    path(
        "ingredient-update-basic/<slug>/",
        views.ingredient_update_basic,
        name="ingredient-update-basic",
    ),
    path(
        "ingredient-update-attribute/<slug>/",
        views.ingredient_update_attribute,
        name="ingredient-update-attribute",
    ),
    path(
        "ingredient-update-score/<slug>/",
        views.ingredient_update_score,
        name="ingredient-update-score",
    ),
    path(
        "ingredient-update-nutritional-tags/<slug>/",
        views.ingredient_update_nutritional_tags,
        name="ingredient-update-nutritional-tags",
    ),
    path(
        "ingredient-update-nutrition/<slug>/",
        views.ingredient_update_nutrition,
        name="ingredient-update-nutrition",
    ),
    path(
        "ingredient-update-recipe/<slug>/",
        views.ingredient_update_recipe,
        name="ingredient-update-recipe",
    ),
    # ingredient_update_manage
    path(
        "ingredient-update-manage/<slug>/",
        views.ingredient_update_manage,
        name="ingredient-update-manage",
    ),
    path("ingredient-list/", views.ingredient_list, name="ingredient-list"),
    path(
        "ingredient/<slug>/portion-create/",
        views.ingredient_portion_create,
        name="ingredient-portion-create",
    ),
    path(
        "ingredient/<slug>/portion-update/<pk>",
        views.ingredient_portion_update,
        name="ingredient-portion-update",
    ),
    path(
        "ingredient/<slug>/price-create/",
        views.ingredient_price_create,
        name="ingredient-price-create",
    ),
    path(
        "ingredient/<slug>/price-update/<pk>",
        views.ingredient_price_update,
        name="ingredient-price-update",
    ),
    path(
        "ingredient/<slug>/overview",
        views.ingredient_detail_overview,
        name="ingredient-detail-overview",
    ),
    path(
        "ingredient/<slug>/analyse",
        views.ingredient_detail_analyse,
        name="ingredient-detail-analyse",
    ),
    path(
        "ingredient/<slug>/portion",
        views.ingredient_detail_portion,
        name="ingredient-detail-portion",
    ),
    path(
        "ingredient/<slug>/recipe",
        views.ingredient_detail_recipe,
        name="ingredient-detail-recipe",
    ),
    # ingredient-detail-manage
    path("ingredient/<slug>/manage", views.ingredient_detail_manage, name="ingredient-detail-manage"),
    path(
        "ingredient-update-meta-infos/<slug>/",
        views.ingredient_update_meta_infos,
        name="ingredient-update-meta-infos",
    ),
    path(
        "portions-by-ingredient",
        views.get_portions_by_ingredient,
        name="portions-by-ingredient",
    ),
    # ingredient-suggestions
    path(
        "ingredient-suggestions/<slug>/basic/",
        views.ingredient_suggestions_basic,
        name="ingredient-suggestions-basic",
    ),
    # attribute
    path(
        "ingredient-suggestions/<slug>/attribute/",
        views.ingredient_suggestions_attribute,
        name="ingredient-suggestions-attribute",
    ),
    # nutritional tags
    path(
        "ingredient-suggestions/<slug>/nutritional-tags/",
        views.ingredient_suggestions_nutritional_tags,
        name="ingredient-suggestions-nutritional-tags",
    ),
    # score
    path(
        "ingredient-suggestions/<slug>/score/",
        views.ingredient_suggestions_score,
        name="ingredient-suggestions-score",
    ),
    path(
        "ingredient-suggestions/<slug>/recipe/",
        views.ingredient_suggestions_recipe,
        name="ingredient-suggestions-recipe",
    ),
    path(
        "ingredient-suggestions/<slug>/nutrition/",
        views.ingredient_suggestions_nutrition,
        name="ingredient-suggestions-nutrition",
    ),
    path(
        "ingredient-update-ref/<slug>/",
        views.ingredient_update_ref,
        name="ingredient-update-ref",
    ),
    # Ingredient alias routes
    path(
        "ingredient-alias/create/",
        views.ingredient_alias_create,
        name="ingredient-alias-create",
    ),
    path(
        "ingredient-alias/create/<int:ingredient_id>/",
        views.ingredient_alias_create,
        name="ingredient-alias-create-with-id",
    ),
    path(
        "ingredient-alias/delete/<int:alias_id>/",
        views.ingredient_alias_delete,
        name="ingredient-alias-delete",
    ),
    path(
        "ingredient-alias/edit/<int:alias_id>/",
        views.ingredient_alias_edit,
        name="ingredient-alias-edit",
    ),
    path("admin/main", views.admin_main, name="food-admin-main"),

    path(
        "ingredient-wizard/", 
        views.IngredientWizardView.as_view(form_list), 
        name="ingredient-wizard"
    ),
    path(
        "ingredient-wizard-final/<slug>/", 
        views.ingredient_wizard_final, 
        name="ingredient-wizard-final"
    ),
    path(
        'api/wizard-suggestions/<str:step_name>/<str:slug>/', 
        views.wizard_suggestions_api, 
        name='wizard-suggestions-api'
    ),
    path(
        "ingredient/<slug>/portion/<pk>/delete/",
        views.ingredient_portion_delete,
        name="ingredient-portion-delete"
    ),
    path('ingredient/<slug:slug>/price/<int:pk>/delete/', views.ingredient_price_delete, name='ingredient-price-delete'),
]
