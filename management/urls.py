from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
from .views import CustomLoginView

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('403/', views.custom_403_view, name='403'),

    path('documents', views.document_list, name='document_list'),
    path('edit/<int:pk>/', views.document_edit, name='document_edit'),
    path('document/<int:pk>/', views.document_detail, name='document_detail'),
    path('document/upload/', views.upload_document, name='upload_document'),
    path('document/<int:pk>/add-related/', views.add_related_document, name='add_related_document'),
    path('document/<int:pk>/update-workflow/', views.update_workflow, name='update_workflow'),
    
    # Open document
    path('document/download/<int:pk>/', views.document_download, name='document_download'),
    path('document/view/<int:pk>/', views.document_view, name='document_view'),
    # path('documents/<int:document_id>/view/', views.view_document, name='view_document'),

    path('documents/view/<int:document_id>/', views.view_pdf, name='view_pdf'),
    path('document/open/<int:pk>/', views.document_open, name='document_open'),
    path('documents/share/<int:pk>/', views.share_document, name='share_document'),

    # Shared documents
    path('user/shared-documents/', views.user_shared_documents, name='user_shared_documents'),
    path('department/shared-documents/', views.department_shared_documents, name='department_shared_documents'),
    path('ministry/shared-documents/', views.ministry_shared_documents, name='ministry_shared_documents'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/clear/', views.clear_notifications, name='clear_notifications'),
    path('notifications/count/', views.notification_count, name='notification_count'),

    # Summarize
    # path('documents/<int:pk>/summarize/', views.summarize_document, name='document_summarize'),
    path('summarize/<int:document_id>/', views.summarize_pdf, name='summarize_pdf'),
    path('summary_result/', views.summary_result, name='summary_result'),

    # Company Settings
    path('settings/', views.company_settings_view, name='company_settings'),
    # user register
    path('register/', views.register_user, name='register_user'),
    # Password Reset
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    # Login/Logout
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # path('login/', auth_views.LoginView.as_view(template_name='home/login.html'), name='login'),
    path('login/', CustomLoginView.as_view(), name='login'),
]

