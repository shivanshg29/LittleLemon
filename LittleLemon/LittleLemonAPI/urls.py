from django.urls import path
from .views import *

urlpatterns=[
    path('menu-items',MenuItems),
    path('menu-items/<int:pk>',MenuItemDetail),

    path('groups/manager/users',manage_users),
    path('groups/manager/users/<int:pk>',remove_manager_user),
    path('groups/delivery-crew/users',delivery_crew_users),
    path('groups/delivery-crew/users/<int:pk>',remove_delivery_crew_user),

    path('cart/menu-items',cart_items),

    path('orders',orders),
    path('orders/<int:pk>',order_details),
]