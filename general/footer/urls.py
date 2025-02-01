from django.urls import include, path

from . import views

urlpatterns = [
    path("about/", views.about, name="footer-about"),
    path("contact/", views.contact, name="footer-contact"),
    path("faq/", views.faq, name="footer-faq"),
    path("impressum/", views.impressum, name="footer-impressum"),
    path("privacy/", views.privacy, name="footer-privacy"),
    path("support/", views.support, name="footer-support"),
    path("internetnacht/", views.internetnacht, name="footer-internetnacht"),
]
