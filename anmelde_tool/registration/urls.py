from django.urls import include, path
from anmelde_tool.registration import views
from anmelde_tool.event.summary import views as event_summary_views

from anmelde_tool.event.basic.forms import (
    EventIntroForm,
    EventBasicInfoForm,
    EventLocationForm,
    EventScheduleForm,
    EventPermissionFormSet,
    EventSummaryForm,
)

form_list = [
    ("123", EventIntroForm),
]

urlpatterns = [
    path('register-detail-overview/<uuid:reg_id>/', views.register_detail_overview, name='reg-detail-overview'),
    path('register-detail-attribute/<uuid:reg_id>/', views.register_detail_attribute, name='reg-detail-attribute'),
    path('register-detail-permission/<uuid:reg_id>/', views.register_detail_permission, name='reg-detail-permission'),
    path('register-detail-participant/<uuid:reg_id>/', views.register_detail_participant, name='reg-detail-participant'),
    path('register-detail-privacy/<uuid:reg_id>/', views.register_detail_privacy, name='reg-detail-privacy'),
    path('registration-list/', views.registration_list, name='reg-list'),
    path('registration-create/<slug:event_slug>/', views.registration_create, name='registration-create'),
    path('registration-wizard/<slug:event_slug>/', views.RegistrationWizardView.as_view(form_list), name='registration-wizard'),
]
