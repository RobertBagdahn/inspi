from django.urls import path

from . import views

urlpatterns = [
    path("basic", views.main_view, name="master-data-main"),
    path("scout-hierarchy/dashboard", views.masterdata_scout_hierarchy_dashboard, name="master-data-scout-hierarchy-dashboard"),
    path("scout-hierarchy/list", views.masterdata_scout_hierarchy_list, name="master-data-scout-hierarchy-list"),
    path("scout-hierarchy/<int:scout_hierarchy_id>/overview", views.masterdata_scout_hierarchy_overview, name="master-data-scout-hierarchy-overview"),
    path("scout-hierarchy/<int:scout_hierarchy_id>/manage", views.masterdata_scout_hierarchy_manage, name="master-data-scout-hierarchy-manage"),
    path("scout-hierarchy/<int:scout_hierarchy_id>/download", views.masterdata_scout_hierarchy_download, name="master-data-scout-hierarchy-downloads"),
    path("scout-hierarchy/<int:scout_hierarchy_id>/download-csv", views.scout_hierarchy_download_csv, name="master-data-scout-hierarchy-download-csv"),

    path("scout-hierarchy/create", views.scout_hierarchy_create, name="master-data-scout-hierarchy-create"),
    path("scout-hierarchy/<int:scout_hierarchy_id>/update", views.scout_hierarchy_update, name="master-data-scout-hierarchy-update"),
    path("scout-hierarchy/<int:scout_hierarchy_id>/delete", views.scout_hierarchy_delete, name="master-data-scout-hierarchy-delete"),
]
