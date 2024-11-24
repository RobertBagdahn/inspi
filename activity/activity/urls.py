# myapi/urls.py
from django.urls import include, re_path, path
from pictures.conf import get_settings

from activity.activity import views
from activity.activity import forms
from django.views.generic import TemplateView

from .views import (
    create_material_item,
    create_material_item_form,
    detail_material_item,
    update_material_item,
    delete_material_item
)

FORMS_FULL_LOGGEDOUT = [
    ("intro", forms.IntroForm),
    ("main-text", forms.MainTextForm),
    ("header-text", forms.HeaderTextForm),
    ("rating", forms.RatingForm),
    ("topic", forms.TopicForm),
    ("choices", forms.ChoicesForm),
    ("creator", forms.UnkownForm),
]
FORMS_FULL_LOGGEDIN = [
    ("intro", forms.IntroForm),
    ("main-text", forms.MainTextForm),
    ("header-text", forms.HeaderTextForm),
    ("rating", forms.RatingForm),
    ("topic", forms.TopicForm),
    ("choices", forms.ChoicesForm),
    ("creator", forms.CreatorForm),
]
FORMS_SHORT_LOGGEDOUT = [
    ("intro", forms.IntroForm),
    ("main-text", forms.MainTextForm),
    ("creator", forms.UnkownForm),
]
FORMS_SHORT_LOGGEDIN = [
    ("intro", forms.IntroForm),
    ("main-text", forms.MainTextForm),
    ("creator", forms.CreatorForm),
]

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # redirect to the overview/ page
    path("", views.main_view, name="activity-main"),
    path("activity-main/<int:topic_id>", views.main_category_view, name="activity-main-topic"),
    path("activity-category-main/<str:category_name>/<int:category_id>", views.main_category_view, name="activity-main-category"),
    path('activity-load-more/<str:category_name>/<int:category_id>', views.list_load_activities_view, name='activity-load-more'),
    path('search', views.search, name='activity-search'),

    path("all-items", views.all_items, name="activity-all-items"),
    path("details/<int:activity_id>", views.detail, name="activity-detail"),
    path("details/<int:activity_id>/update-rating", views.update_rating, name="activity-update-rating"),
    path("details/<int:activity_id>/update-topic", views.update_topic, name="activity-update-topic"),
    path("details/<int:activity_id>/update-choices", views.update_choices, name="activity-update-choices"),
    path("details/<int:activity_id>/update-material", views.update_material, name="activity-update-material"),
    path("details/<int:activity_id>/update-header-text", views.update_header_text, name="activity-update-header-text"),
    path("details/<int:activity_id>/update-main-text", views.update_main_text, name="activity-update-main-text"),
    path("details/<int:activity_id>/update-creator", views.update_creator, name="activity-update-creator"),
    path("details/<int:activity_id>/update-image", views.update_image, name="activity-update-image"),
    path("details/<int:activity_id>/update-crop", views.update_crop, name="activity-update-crop"),
    path("comment/create/", views.comment_create, name="activity-create-comment"),

    path("activity-archive/<int:activity_id>", views.activity_archive, name="activity-archive"),
    path("activity-publish/<int:activity_id>", views.activity_publish, name="activity-publish"),


    path("create-choice", views.create_choice, name="activity-create-choice"),
    path("create-full-in", views.ContactWizard.as_view(FORMS_FULL_LOGGEDIN), name="activity-create-full-loggedin"),
    path("create-full-out", views.ContactWizard.as_view(FORMS_FULL_LOGGEDOUT), name="activity-create-full-loggedout"),
    path("create-short-in", views.ContactWizard.as_view(FORMS_SHORT_LOGGEDIN), name="activity-create-short-loggedin"),
    path("create-short-out", views.ContactWizard.as_view(FORMS_SHORT_LOGGEDOUT), name="activity-create-short-loggedout"),
    path("create-final/<pk>/", views.create_final, name="activity-create-final"),

    path("update/<int:activity_id>", views.update, name="activity-update"),
    path("list", views.list, name="activity-list"),
    path("faq", views.faq, name="footer-faq"),

    path('create-material-item/<int:activity_id>', create_material_item, name='create-material-item'),
    path('htmx/material-item/<pk>/', detail_material_item, name="detail-material-item"),
    path('htmx/material-item/<pk>/update/', update_material_item, name="update-material-item"),
    path('htmx/material-item/<pk>/delete/', delete_material_item, name="delete-material-item"),
    path('htmx/create-material-item-form/<int:activity_id>', create_material_item_form, name='create-material-item-form'),

    path('admin/overview', views.admin_overview, name="activity-admin-overview"),
    path('admin/like', views.admin_like, name="activity-admin-like"),
    path('admin/event-of-week', views.admin_event_of_week, name="activity-admin-event-of-week"),
    path('admin/topic', views.admin_topic, name="activity-admin-topic"),
    path('admin/comment', views.admin_comment, name="activity-admin-comment"),
    path('admin/data', views.admin_data, name="activity-admin-data"),

    # event-of-week-create
    path('admin/event-of-week/create', views.event_of_week_create, name="activity-event-of-week-create"),
    path('admin/event-of-week/update/<int:id>', views.event_of_week_update, name="activity-event-of-week-update"),

    # comment
    path('admin/comment/update/<int:id>', views.comment_update, name="activity-comment-update"),

    # emotions
    path('activity/add-emotion', views.add_emotion, name="activity-admin-emotion"),
    path('admin/emotion/update/<int:id>', views.emotion_update, name="activity-emotion-update"),


]

if get_settings().USE_PLACEHOLDERS:
    urlpatterns += [
        path("_pictures/", include("pictures.urls")),
    ]
