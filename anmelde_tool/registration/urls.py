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
    path('register-detail-manage/<uuid:reg_id>/', views.register_detail_manage, name='reg-detail-manage'),
    path('registration-list/', views.registration_list, name='reg-list'),
    path('registration-create/<slug:event_slug>/', views.registration_create, name='registration-create'),
    path('registration-wizard/<slug:event_slug>/', views.RegistrationWizardView.as_view(form_list), name='registration-wizard'),
    path('registration-final/<uuid:reg_id>/', views.registration_final, name='registration-final'),
    
    # Participant management URLs
    path('participant/<uuid:reg_id>/create/', views.participant_create, name='participant-create'),
    path('participant/<uuid:reg_id>/<int:participant_id>/', views.participant_detail, name='participant-detail'),
    path('participant/<uuid:reg_id>/<int:participant_id>/update/', views.participant_update, name='participant-update'),
    path('participant/<uuid:reg_id>/<int:participant_id>/delete/', views.participant_delete, name='participant-delete'),
    
    # Responsible person management
    path('registration/<uuid:reg_id>/remove-responsible-person/<int:person_id>/', views.remove_responsible_person, name='remove-responsible-person'),
    path('registration/<uuid:reg_id>/add-responsible-person/', views.add_responsible_person, name='add-responsible-person'),
    
    # Email resend URL
    path('registration/<uuid:reg_id>/send-confirmation-email/', views.send_confirmation_email, name='send-confirmation-email'),

    # Registration revocation URL
    path('registration/<uuid:reg_id>/revoke/', views.registration_revoke, name='registration-revoke'),

    # New URLs for downloading registrations and participants
    path('event/<uuid:reg_id>/download-registrations/', views.download_registrations, name='download-registrations'),
    path('event/<uuid:reg_id>/download-participants/', views.download_participants, name='download-participants'),
    path('event/<uuid:reg_id>/download-invoice/', views.download_invoice, name='download-invoice'),
]
