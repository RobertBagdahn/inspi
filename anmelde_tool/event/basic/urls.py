from django.urls import path
from anmelde_tool.event.basic import views


# from anmelde_tool.email_services import views as email_services_views
# from anmelde_tool.attributes import views as attributes_views
# from . import views


EVENT_WIZARD_TEMPLATES = {
    "intro": "event/wizard/generic_step.html",
    "basic_info": "event/wizard/generic_step.html",
    "location": "event/wizard/generic_step.html",
    "schedule": "event/wizard/generic_step.html",
    "invite": "event/wizard/generic_step.html",
    "summary": "event/wizard/generic_step.html",
}

from anmelde_tool.event.basic.forms import (
    EventIntroForm,
    EventBasicInfoForm,
    EventLocationForm,
    EventScheduleForm,
    EventPermissionFormSet,
    EventSummaryForm,
)

form_list = [
    ("intro", EventIntroForm),
    ("basic_info", EventBasicInfoForm),
    ("location", EventLocationForm),
    ("schedule", EventScheduleForm),
    ("invite", EventPermissionFormSet),
    ("summary", EventSummaryForm),
]

urlpatterns = [
    path('dashboard/', views.event_dashboard, name='event-dashboard'),
    path('list/', views.event_list, name='event-list'),
    path('create/', views.event_create, name='event-create'),
    path('detail/<slug:slug>/overview', views.event_detail_overview, name='event-detail-overview'),
    path(
        "detail/<str:slug>/permission",
        views.event_detail_permission,
        name="event-detail-permission"
    ),
    path(
        "detail/<str:slug>/module",
        views.event_detail_module,
        name="event-detail-module"
    ),
    # booking type
    path(
        "detail/<str:slug>/booking-type",
        views.event_detail_booking_type,
        name="event-detail-booking-type"
    ),
    # registration
    path(
        "detail/<str:slug>/registration",
        views.event_detail_registration,
        name="event-detail-registration"
    ),
    path(
        "event-wizard/", 
        views.EventWizardView.as_view(form_list), 
        name="event-wizard"
    ),
    path(
        "event-wizard-final/<str:slug>",
        views.event_wizard_final,
        name="event-wizard-final"
    ),
    path(
        "detail/<str:slug>/permission/create",
        views.event_permission_create,
        name="event-permission-create"
    ),
    path(
        "detail/permission/<int:pk>/update",
        views.event_permission_update,
        name="event-permission-update"
    ),
    path(
        "detail/permission/<int:pk>",
        views.event_permission_detail,
        name="event-permission-detail"
    ),
    path(
        "detail/<str:slug>/booking-type/create",
        views.event_booking_type_create,
        name="event-booking-type-create"
    ),
    path(
        "detail/booking-type/<int:pk>/update",
        views.event_booking_type_update,
        name="event-booking-type-update"
    ),
    path(
        "detail/booking-type/<int:pk>/delete",
        views.event_booking_type_delete,
        name="event-booking-type-delete"
    ),
    path(
        "detail/booking-type/<int:pk>",
        views.event_booking_type_detail,
        name="event-booking-type-detail"
    ),
    path(
        "detail/<str:event_slug>/module/create",
        views.event_module_create,
        name="event-module-create"
    ),
    path(
        "detail/module/<int:pk>",
        views.event_module_detail,
        name="event-module-detail"
    ),
    path(
        "detail/module/<int:pk>/update",
        views.event_module_update,
        name="event-module-update"
    ),
    path(
        "detail/module/<int:pk>/delete",
        views.event_module_delete,
        name="event-module-delete"
    ),
    path(
        "detail/module/<int:pk>/attribute/create",
        views.event_module_attribute_create,
        name="event-module-attribute-create"
    ),
]
