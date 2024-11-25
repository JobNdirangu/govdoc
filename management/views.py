import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import CompanySetting,ActionLog,Department,Document, DocumentMovement,Notification,RelatedDocument,User,Workflow
from .forms import CompanySettingForm,Workflow,Document,WorkflowForm,DocumentForm,RelatedDocumentForm
from django.contrib.auth.decorators import login_required,permission_required
from django.core.exceptions import PermissionDenied
from django.contrib.auth.views import LoginView
from django.http import Http404, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils.dateparse import parse_date
from django.db.models import Sum,F, FloatField,Count,ExpressionWrapper,DecimalField,CharField,OuterRef, Subquery,IntegerField
from .models import Notification 
from django.utils import timezone
import json
from django.db.models.functions import TruncDate,TruncDay,TruncMonth,Concat
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from datetime import timedelta,datetime
from django.urls import reverse
from reportlab.lib.units import inch
from reportlab.lib.colors import blue, brown
import pytz
from django import template
from transformers import pipeline
from django.http import FileResponse
import fitz  # PyMuPDF
from transformers import pipeline
from urllib.parse import unquote


os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN custom ops
import tensorflow as tf

register = template.Library()

def custom_403_view(request, exception=None):
    return render(request, 'home/403.html', status=403)

@login_required
def dashboard(request):
    documents = Document.objects.all().order_by('-upload_date')
    recent = Document.objects.all().order_by('-upload_date')[:5]
    paginator = Paginator(documents, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for index, documents in enumerate(page_obj.object_list):
        documents.serial_number = index + 1 + (page_obj.number - 1) * paginator.per_page

    return render(request, 'home/dashboard.html',{'page_obj': page_obj, 'recent':recent})

# View all documents
@login_required
def document_list(request):
    documents = Document.objects.all().order_by('-upload_date')
    paginator = Paginator(documents, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for index, documents in enumerate(page_obj.object_list):
        documents.serial_number = index + 1 + (page_obj.number - 1) * paginator.per_page

    return render(request, 'documents/document_list.html', {'page_obj': page_obj})

# Download Document
@login_required
def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk)
    file_path = document.file.path
    if not os.path.exists(file_path):
        raise Http404("File not found")    
    try:
        with open(file_path, 'rb') as file:
            response = FileResponse(file, as_attachment=True, filename=document.file.name)
            response['Content-Type'] = 'application/pdf'  # Optional, change based on file type
            return response
    except Exception as e:
        raise Http404(f"Error opening file: {str(e)}")
    
import mimetypes
# Open Document
@login_required
def document_open(request, pk):
    document = get_object_or_404(Document, pk=pk)
    mime_type, _ = mimetypes.guess_type(document.file.path)    
    # Ensure the MIME type is correct
    if mime_type is None:
        mime_type = 'application/octet-stream'
    
    response = render(request, 'documents/document_open.html', {
        'document': document,
    })    
    response['Content-Disposition'] = 'inline; filename="{}"'.format(document.file.name)
    response['Content-Type'] = mime_type    
    return response


@login_required
def document_view(request, pk):
    document = get_object_or_404(Document, pk=pk)
    file_url = unquote(document.file.url)    
    ActionLog.objects.create(
        document=document,
        action_by=request.user,
        action='Viewed in System',
        comments="Document has been opened"
    )
    return render(request, 'documents/document_view.html', {'document': document, 'file_url': file_url})


# @login_required
# def document_view(request, pk):
#     document = get_object_or_404(Document, pk=pk)
#     mime_type, _ = mimetypes.guess_type(document.file.path)
#     response = HttpResponse(document.file, content_type=mime_type)
#     response['Content-Disposition'] = f'inline; filename="{document.file.name}"'
#     return response

# Document information
@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    related_documents = document.related_documents.all().order_by("-added_date")
    workflows = document.workflows.all()
    ActionLog.objects.create(
        document=document,
        action_by=request.user,
        action='Viewed Details',
        comments="Document details viewed"
    )
    return render(request, 'documents/document_detail.html', {
        'document': document,
        'related_documents': related_documents,
        'workflows': workflows,
    })


@login_required
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.uploaded_by = request.user
            document.save()

            Notification.objects.create(
                    user=request.user,
                    message=f'{request.user} has uploaded a new document successfully'
                )
            messages.success(request, f'{request.user} has uploaded a new document successfully', )

            return redirect('document_list')
    else:
        form = DocumentForm()
    return render(request, 'documents/upload_document.html', {'form': form})


@login_required
def add_related_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        form = RelatedDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            related_doc = form.save(commit=False)
            related_doc.parent_document = document
            related_doc.added_by = request.user
            related_doc.save()
            ActionLog.objects.create(
                document=document,
                action_by=request.user,
                action='Additional documents',
                comments="Related documents upload has been created."
            )
            return redirect('document_detail', pk=document.pk)
    else:
        form = RelatedDocumentForm()
    return render(request, 'documents/add_related_document.html', {'form': form, 'document': document})


@login_required
def update_workflow(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        form = WorkflowForm(request.POST)
        if form.is_valid():
            workflow = form.save(commit=False)
            workflow.document = document
            workflow.assigned_to = request.user
            workflow.save()
            return redirect('document_detail', pk=document.pk)
    else:
        form = WorkflowForm()
    return render(request, 'documents/update_workflow.html', {'form': form, 'document': document})

# Theme settings
@login_required
def company_settings_view(request):
    setting, created = CompanySetting.objects.get_or_create(id=1)
    print(timezone.now())
    # print(pytz.all_timezones)
    if not request.user.has_perm('management.change_companysetting'):
        messages.error(request, 'You Do Not Have Permission to Change Company Settings')
        form = CompanySettingForm(instance=setting)
        theme_choice = setting.theme_choice
        return render(request, 'home/company_settings.html', {'form': form, 'theme_choice': theme_choice})
    
    if request.method == "POST":
        form = CompanySettingForm(request.POST, instance=setting)
        if form.is_valid():
            form.save()
            messages.success(request, 'Changes successfully saved')
            return redirect('company_settings')  # Make sure this is defined in your URL patterns
    else:
        form = CompanySettingForm(instance=setting)
    theme_choice = setting.theme_choice

    return render(request, 'home/company_settings.html', {'form': form, 'theme_choice': theme_choice})

#  Notifications
@login_required
def notifications(request):
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    context = {'notifications': user_notifications}
    return render(request, 'home/notifications.html', context)

@login_required
def notification_count(request):
    """Return the count of unread notifications as JSON."""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})

@login_required
def mark_notification_read(request, notification_id):
    """Mark a specific notification as read."""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')  

@login_required
def clear_notifications(request):
    """Clear all notifications for the user."""
    Notification.objects.filter(user=request.user).delete()
    return redirect('notifications')  



# Initialize the summarization pipeline
summarizer = pipeline("summarization")

def summarize_pdf(request, document_id):
    document = get_object_or_404(Document, pk=document_id)
    pdf_path = document.file.path  
    text = extract_text_from_pdf(pdf_path)
    summary = summarize_text(text)
    print(summary)
    ActionLog.objects.create(
        document=document,
        action_by=request.user,
        action='Summarized',
        comments="Summary generated"
    )

    return render(request, 'documents/document_summary.html', {'summary': summary})

def extract_text_from_pdf(pdf_path):
    # Extract text from each page of the PDF
    doc = fitz.open(pdf_path)
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text()
    return text

def summarize_text(text):
    max_input_length = 1024
    chunk_size = max_input_length // 2  
    text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    
    summary = ""
    for chunk in text_chunks:
        chunk_summary = summarizer(chunk, max_length=100, min_length=50, do_sample=False)
        summary += chunk_summary[0]['summary_text'] + " "
    return summary





# def summarize_text(text):
#     if len(text.split()) < 10:  
#         return "Text too short to summarize"

#     input_length = len(text.split())
#     max_length = min(input_length // 5, 100)
#     summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
#     print(summary)
#     return summary[0]['summary_text']


