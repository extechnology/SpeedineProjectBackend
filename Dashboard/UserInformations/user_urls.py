from django.urls import path
from .user_views import *

urlpatterns = [
    path("users", UserListView.as_view(), name="user-list"),
]
