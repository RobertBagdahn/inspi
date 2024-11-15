# test/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('download-form/<activity_id>', views.download_form, name='pdf-form'),
	path('generate-image/<activity_id>/<color>/<page>', views.generate_png_from_svg, name='generate-pdf'),
]
