from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_users, name='dashboard_users'),

    # User management
    path('admin/inactive-users/', views.manage_inactive_users, name='manage_inactive_users'),

    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/edit/<int:pk>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),

    # Role management
    path('groups/', views.group_list, name='group_list'),
    path('groups/add/', views.group_add, name='group_add'),
    path('groups/edit/<int:pk>/', views.group_edit, name='group_edit'),
    path('groups/delete/<int:pk>/', views.group_delete, name='group_delete'),

     # Ministry 
    path('ministries/', views.ministry_list_create, name='ministry_list_create'),
    path('ministries/edit/<int:pk>/', views.ministry_edit, name='ministry_edit'),
    path('ministries/delete/<int:pk>/', views.ministry_delete, name='ministry_delete'),

    # Department 
    path('departments/', views.department_list_create, name='department_list_create'),
    path('departments/edit/<int:pk>/', views.department_edit, name='department_edit'),
    path('departments/delete/<int:pk>/', views.department_delete, name='department_delete'),
]
