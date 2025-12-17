from django.urls import path
from .user_views import *

urlpatterns = [
    path("users", UserListView.as_view(), name="user-list"),
    path("contacts", ContactListView.as_view(), name="contact-list"),   
]
