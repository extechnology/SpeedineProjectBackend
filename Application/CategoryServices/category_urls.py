from django.urls import path
from .category_views import *

urlpatterns = [
    path('category-list/', CategoryView.as_view(), name='category-list'),
]