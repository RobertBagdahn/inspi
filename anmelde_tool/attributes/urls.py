from django.urls import path
from . import views

urlpatterns = [
    path('edit/<int:attribute_id>/', views.attributes_edit, name='attributes-edit'),
    path('delete/<int:attribute_id>/', views.attributes_delete, name='attributes-delete'),
    path('create/<uuid:registration_id>/<int:attribute_module_id>/', views.attributes_create, name='attributes-create'),
    path('detail/<int:attribute_id>/', views.attribute_detail, name='event-attribute-detail'),
    path('update/<int:attribute_id>/', views.attribute_update, name='attributes-update'),
    path('delete/<int:attribute_id>/', views.attribute_delete, name='attributes-delete'),
    
]
