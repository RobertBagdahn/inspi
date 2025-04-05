from django.urls import include, path

from . import views

urlpatterns = [
    path(
        "user-detail-overview/<username>/",
        views.user_detail_overview,
        name="user-detail-overview",
    ),
    path(
        "user-detail-manage/<username>/",
        views.user_detail_manage,
        name="user-detail-manage",
    ),
    path(
        "user-detail-memberships/<username>/",
        views.user_detail_memberships,
        name="user-detail-memberships",
    ),
    path(
        "user-detail-my-requests/<username>/",
        views.user_detail_my_requests_user,
        name="user-details-my-requests-user",
    ),
    path(
        "profile-edit/<username>/",
        views.profile_edit,
        name="login-profile-edit",
    ),
    path(
        "profile-delete/<username>/",
        views.profile_delete,
        name="login-profile-delete",
    ),
    path("settings/<username>/", views.settings, name="login-settings"),
    path(
        "user-dashboard/",
        views.user_dashboard,
        name="user-dashboard",
    ),
    path(
        "user-detail-person-wizard/<username>/",
        views.PersonWizardView.as_view(), 
        name="person-wizard"
    ),
    path(
        "user-detail-person-wizard/",
        views.start_person_wizard, 
        name="start-person-wizard"
    ),
    path(
        "user-detail-person-wizard-start/<username>/",
        views.start_person_wizard, 
        name="start-person-wizard-with-username"
    ),
    # user-list
    path("user-list/", views.user_list, name="user-list"),
]
