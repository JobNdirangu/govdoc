from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('403/', views.custom_403_view, name='403'),

    path('documents', views.document_list, name='document_list'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    path('document/upload/', views.upload_document, name='upload_document'),
    path('document/<int:pk>/add-related/', views.add_related_document, name='add_related_document'),
    path('document/<int:pk>/update-workflow/', views.update_workflow, name='update_workflow'),
    
    # Open document
    path('document/download/<int:pk>/', views.document_download, name='document_download'),
    path('document/view/', views.document_view, name='document_view'),
    path('document/open/<int:pk>/', views.document_open, name='document_open'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),
    path('notifications/count/', views.notification_count, name='notification_count'),

    # Summarize
    # path('documents/<int:pk>/summarize/', views.summarize_document, name='document_summarize'),
    # path('summarize/<int:document_id>/', views.summarize_pdf, name='summarize_pdf'),

    # Company Settings
    path('settings/', views.company_settings_view, name='company_settings'),

    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    # Login/Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),
]

