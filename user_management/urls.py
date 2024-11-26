from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_users, name='dashboard_users'),

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

     # Ministry 
    path('ministries/', views.ministry_list_create, name='ministry_list'),
    path('ministries/<int:pk>/edit/', views.ministry_edit, name='ministry_edit'),
    path('ministries/<int:pk>/delete/', views.ministry_delete, name='ministry_delete'),

    # Department 
    path('departments/', views.department_list_create, name='department_list'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
]
