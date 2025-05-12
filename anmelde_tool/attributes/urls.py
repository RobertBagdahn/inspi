from django.urls import path
from . import views

urlpatterns = [
    # for event
    path("/edit/<int:attribute_id>/", views.attributes_edit, name="attributes-edit"),
    path(
        "/delete/<int:attribute_id>/", views.attributes_delete, name="attributes-delete"
    ),
    # for registration
    path(
        "/create/<uuid:registration_id>/<int:attribute_module_id>/",
        views.attributes_create,
        name="attributes-create",
    ),
    path(
        "/detail/<int:attribute_id>/",
        views.attribute_detail,
        name="event-attribute-detail",
    ),
    path(
        "/update/<int:attribute_id>/", views.attribute_update, name="attributes-update"
    ),
    path(
        "/delete/<int:attribute_id>/", views.attribute_delete, name="attributes-delete"
    ),
    # New URLs for choice options management
    path(
        "choice/create/<int:attribute_id>/",
        views.attribute_choice_create,
        name="attribute-choice-create",
    ),
    path(
        "choice/edit/<int:choice_id>/",
        views.attribute_choice_edit,
        name="attribute-choice-edit",
    ),
    path(
        "choice/delete/<int:choice_id>/",
        views.attribute_choice_delete,
        name="attribute-choice-delete",
    ),
]
