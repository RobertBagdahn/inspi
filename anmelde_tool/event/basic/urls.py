from django.urls import path
from anmelde_tool.event.basic import views


# from anmelde_tool.email_services import views as email_services_views
# from anmelde_tool.attributes import views as attributes_views
# from . import views


from anmelde_tool.event.basic.forms import (
    EventIntroForm,
    EventBasicInfoForm,
    EventLocationForm,
    EventLocationCreationForm,
    EventScheduleForm,
    EventPermissionFormSet,
    EventModuleForm,
    EventSummaryForm,
    EventPermissionForm,
    BookingOptionForm,  # Make sure this is imported
    EventRegistrationTypeForm,
)

form_list = [
    ("intro", EventIntroForm),
    ("basic_info", EventBasicInfoForm),
    ("location", EventLocationForm),
    ("location_create", EventLocationCreationForm),
    ("schedule", EventScheduleForm),
    ("invite", EventPermissionFormSet),
    ("booking_option", BookingOptionForm),
    ("module", EventModuleForm),
    ("registration_type", EventRegistrationTypeForm),
    ("summary", EventSummaryForm),
]

urlpatterns = [
    path('dashboard/', views.event_dashboard, name='event-dashboard'),
    path('list/', views.event_list, name='event-list'),
    path('create/', views.event_create, name='event-create'),
    path('update/<str:slug>/', views.event_update, name='event-update'),
    path('delete/<str:slug>/', views.event_delete, name='event-delete'),
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
    #download
    path(
        "detail/<str:slug>/download",
        views.event_detail_download,
        name="event-detail-download"
    ),
    path(
        "detail/<str:slug>/invitees",
        views.event_detail_invitees,
        name="event-detail-invitees"
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
        "detail/permission/<int:pk>/delete",
        views.event_permission_delete,
        name="event-permission-delete"
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
        "detail/<str:event_slug>/module/add",
        views.event_module_add,
        name="event-module-add"
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
    path(
        "detail/<str:event_slug>/download/participants",
        views.download_participants,
        name="event-download-participants"
    ),
    path(
        "detail/<str:event_slug>/download/registrations",
        views.download_registrations,
        name="event-download-registrations"
    ),
    path(
        "detail/<str:event_slug>/download/participants-example",
        views.download_participants_example,
        name="event-download-participants-example"
    ),
]
