from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='group-dashboard'),
    path('my-groups/', views.my_groups, name='my-groups'),
    path('my-requests/', views.my_requests_admin, name='my-requests'),
    path('group-list', views.group_list, name='group-list'),
    path('manage-membership/<slug:group_slug>/', views.manage_membership, name='manage-membership'),
    path('create/', views.create_group, name='create-group'),
    path('edit/<slug:group_slug>/', views.edit_group, name='edit-group'),
    
    path('detail/<slug:group_slug>/overview', views.group_detail_overview, name='group-detail-overview'),
    path('detail/<slug:group_slug>/news', views.group_detail_news, name='group-detail-news'),
    path('detail/<slug:group_slug>/news/create', views.create_group_news, name='group-detail-news-create'),
    path('detail/<slug:group_slug>/news/edit/<int:news_id>', views.edit_group_news, name='group-detail-news-edit'),
    path('detail/<slug:group_slug>/members', views.group_detail_members, name='group-detail-members'),
    path('detail/<slug:group_slug>/admins', views.group_detail_admins, name='group-detail-admins'),
    path('detail/<slug:group_slug>/requests', views.group_detail_requests, name='group-detail-requests'),
    path('detail/<slug:group_slug>/child-groups', views.group_detail_child_groups, name='group-detail-child-groups'),
    path('detail/<slug:group_slug>/parent-groups', views.group_detail_parent_groups, name='group-detail-parent-groups'),

    path('detail/<slug:group_slug>/manage', views.group_detail_manage, name='group-detail-manage'),

    path('join/<slug:group_slug>/', views.join_group, name='join-group'),
    path('add-user/<slug:group_slug>/', views.add_user, name='add-user'),
    path('approve/<int:membership_id>/', views.approve_membership, name='approve-membership'),
    path('join-group-by-code/', views.join_group_by_code, name='join-group-by-code'),
    path('leave/<slug:group_slug>/', views.leave_group, name='leave-group'),
    path('join-group/<slug:group_slug>/', views.join_group, name='join-group'),
    path('manage-requests/<slug:group_slug>/', views.manage_requests, name='manage-requests'),
    path('link-groups/<slug:parent_group_slug>/<slug:child_group_slug>/', views.link_groups, name='link-groups'),
    path('create-permission/<slug:group_slug>/', views.create_permission, name='create-permission'),
    path('manage-permissions/<slug:group_slug>/', views.manage_permissions, name='manage-permissions'),
    path('membership-detail/<int:membership_id>/', views.membership_detail, name='membership-detail'),
    path('leave-group/<slug:group_slug>/', views.leave_group, name='leave-group'),
    path('remove-membership/<int:membership_id>/', views.remove_membership, name='remove-membership'),
    # edit membership
    path('edit-membership-admin/<int:membership_id>/', views.edit_membership_admin, name='edit-membership-admin'),
    path('edit-membership-member/<int:membership_id>/', views.edit_membership_member, name='edit-membership-member'),

    path('delete/<slug:group_slug>/', views.delete_group, name='delete-group'),
    
    path('approve-request/<int:request_id>/', views.approve_request, name='approve-request'),
    path('decline-request/<int:request_id>/', views.decline_request, name='decline-request'),
    path('request-detail/<int:request_id>/', views.request_detail, name='request-detail'),

    path("user/search/results/<slug:group_slug>/", views.search_results_view, name="search_results_view"),
]
