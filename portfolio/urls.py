from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("contact/", views.contact, name="contact"),
    path("contact/verify/", views.contact_verify, name="contact_verify"),
    path("contact/resend/", views.contact_resend, name="contact_resend"),
    path("api/chat/", views.chat_api, name="chat_api"),
    path("api/chat/history/", views.chat_history, name="chat_history"),
]
