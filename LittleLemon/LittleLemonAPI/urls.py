from django.urls import path
from .views import *

urlpatterns=[
    path('menu-items/',MenuItems),
    path('menu-item/<int:pk>/',MenuItemDetail)
]