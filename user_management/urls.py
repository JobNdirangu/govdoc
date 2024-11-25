from django.urls import path
from . import views

urlpatterns = [
    # User management
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),

    # Role management
    path('groups/', views.group_list, name='group_list'),
    path('groups/add/', views.group_add, name='group_add'),
    path('groups/edit/<int:pk>/', views.group_edit, name='group_edit'),
    path('groups/delete/<int:pk>/', views.group_delete, name='group_delete'),
]
