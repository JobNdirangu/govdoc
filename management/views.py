import os
import logging

# Set TensorFlow to suppress logs completely
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0' 
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

# Optionally suppress TensorFlow's internal logs further by adjusting the root logger
logging.getLogger('tensorflow').setLevel(logging.ERROR)
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from .models import CompanySetting,ActionLog,Department,Document, DocumentShare,Notification,RelatedDocument,User,Workflow,DocumentAccess,Ministry,Profile
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
from django.db.models import Q,Sum,F, FloatField,Count,ExpressionWrapper,DecimalField,CharField,OuterRef, Subquery,IntegerField
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
from urllib.parse import quote
import mimetypes
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

register = template.Library()

def custom_403_view(request, exception=None):
    return render(request, 'home/403.html', status=403)

@login_required
def dashboard(request):
    documents = Document.objects.all().order_by('-upload_date').filter(visibility='Public')
    recent = Document.objects.all().order_by('-upload_date').filter(visibility='Public')[:5]    
    shares = DocumentShare.objects.filter(shared_by=request.user).count()
    views = ActionLog.objects.filter(action="Viewed Details", action_by_id=request.user).count()
    uploads = ActionLog.objects.filter(action="created", action_by_id=request.user).count()
    downloads = ActionLog.objects.filter(action="Download", action_by_id=request.user).count()

    paginator = Paginator(documents, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for index, documents in enumerate(page_obj.object_list):
        documents.serial_number = index + 1 + (page_obj.number - 1) * paginator.per_page
    context={
        'page_obj': page_obj, 
        'recent':recent,
        'shares':shares,
        'views':views,
        'uploads':uploads,
        'downloads':downloads,
    }

    return render(request, 'home/dashboard.html',context)

# Login user custom
class CustomLoginView(LoginView):
    template_name = 'home/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['departments'] = Department.objects.all()
        context['ministries'] = Ministry.objects.all()
        return context
    
# Register user
def register_user(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        personal_number = request.POST.get('personal_number')
        department_id = request.POST.get('department')
        ministry_id = request.POST.get('ministry')

        if not (firstname and lastname and email and password and personal_number and department_id and ministry_id):
            messages.error(request, 'All fields are required.')
            return redirect('register_user')

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,  # Use email as the username
                    email=email,
                    first_name=firstname,
                    last_name=lastname,
                    password=password,
                    is_active=False  # User is inactive by default until admin approves
                )

                # Create Profile
                Profile.objects.create(
                    user=user,
                    personal_number=personal_number,
                    department_id=department_id,
                    ministry_id=ministry_id,
                )

                messages.success(request, 'Account created successfully. Wait for admin approval.')
                return redirect('login')  

        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('register_user')

    departments = Department.objects.all()
    ministries = Ministry.objects.all()
    return render(request, 'home/login.html', {
        'departments': departments,
        'ministries': ministries
    })


# View all documents
@login_required
def document_list(request):
    query = request.GET.get('q', '')  
    user_documents = Document.objects.filter(uploaded_by=request.user) 

    documents = user_documents.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(file__icontains=query)
    ).order_by('-upload_date') if query else user_documents.order_by('-upload_date')

    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Return search results as JSON for live search
        data = {
            'documents': list(page_obj.object_list.values('id', 'name', 'description', 'upload_date')),
        }
        return JsonResponse(data)

    for index, document in enumerate(page_obj.object_list):
        document.serial_number = index + 1 + (page_obj.number - 1) * paginator.per_page

    return render(request, 'documents/document_list.html', {'page_obj': page_obj})

# Edit document info
def document_edit(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES, instance=document)
        if form.is_valid():
            form.save()
            return redirect('document_list')  
    else:
        form = DocumentForm(instance=document)
    return render(request, 'management/document_edit.html', {'form': form, 'document': document})

    
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
    file_url = request.build_absolute_uri(document.file.url)
    file_url = quote(file_url, safe=':/')
    # file_url = unquote(document.file.url)    
    ActionLog.objects.create(
        document=document,
        action_by=request.user,
        action='Viewed in System',
        comments="Document has been opened"
    )
    return render(request, 'documents/document_view.html', {'document': document, 'file_url': file_url})

# Download document
@login_required
def document_download(request, pk):
    document = get_object_or_404(Document, pk=pk)
    file_url = request.build_absolute_uri(document.file.url)
    file_url = quote(file_url, safe=':/')
    # if mime_type is None:
    mime_type = 'application/octet-stream'

    response = render(request, 'documents/document_list.html', {
        'document': document,
    })    
    response['Content-Disposition'] = 'inline; filename="{}"'.format(document.file.name)
    response['Content-Type'] = mime_type    
     
    ActionLog.objects.create(
        document=document,
        action_by=request.user,
        action='Download',
        comments="Document has been downloaded"
    )
    return response 


# @login_required
# def document_view(request, pk):
#     document = get_object_or_404(Document, pk=pk)
#     file_path = document.file.path

#     if not os.path.exists(file_path):
#         raise Http404("File not found")

#     mime_type, _ = mimetypes.guess_type(file_path)
#     if mime_type is None:
#         mime_type = 'application/octet-stream'
#     else:
#         response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
#         response['Content-Disposition'] = 'inline; filename="{}"'.format(document.file.name)
#         return response

@login_required      
def view_pdf(request, document_id):
    try:
        document = get_object_or_404(Document, pk=document_id)
        file_path = document.file.path

        if not os.path.exists(file_path):
            raise Http404("The requested document does not exist.")
        if os.path.getsize(file_path) == 0:
            raise Http404("The requested document is empty or corrupted.")

        # Using FileResponse to stream the file, it handles opening/closing the file correctly
        with open(file_path, 'rb') as pdf_file:
            response = FileResponse(pdf_file, content_type='application/pdf')

            response['Content-Disposition'] = f'inline; filename="{document.file.name}"'

            # Prevent caching
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

            return response

    except FileNotFoundError:
        raise Http404("The requested document was not found.")
    except Exception as e:
        print(f"Error: {e}")  # Debugging log
        raise Http404("An error occurred while processing your request.")

# Document information
@login_required
def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    related_documents = document.related_documents.all().order_by("-added_date")
    count_related_documents = document.related_documents.all().count()
    workflows = document.workflows.all()
    shares=len(document.shares.all())
    views = document.action_logs.filter(action="Viewed Details").count()

    users=User.objects.all()
    ActionLog.objects.create(
        document=document,
        action_by=request.user,
        action='Viewed Details',
        comments="Document details viewed"
    )
    context = {
        'document': document,
        'related_documents': related_documents,
        'count_related_documents':count_related_documents,
        'workflows': workflows,
        'shares':shares,
        'views':views,
        'users': users,
        'departments': Department.objects.all(),
        'ministries': Ministry.objects.all(),
    }
    return render(request, 'documents/document_detail.html', context)

# Document Upload
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
    return redirect('document_list')

# Releated Document upload
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
            messages.success(request, f"Related Document uploaded with {request.user}.")

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

# Share document
def share_document(request, pk):
    document = get_object_or_404(Document, pk=pk)
    if request.method == "POST":
        share_with = request.POST.get('share_with')
        remarks = request.POST.get('remarks', '')

        if share_with == 'user':
            user_id = request.POST.get('user')
            recipient = get_object_or_404(User, pk=user_id)
            DocumentShare.objects.create(
                document=document,
                shared_with_user=recipient,
                remarks=remarks,
                shared_by=request.user
            )
            ActionLog.objects.create(
                document=document,
                action_by=request.user,   
                action=f"Shared to: {recipient.username}",
                comments=remarks
            )
            messages.success(request, f"Document shared with {recipient.username}.")
        elif share_with == 'department':
            department_id = request.POST.get('department')
            recipient = get_object_or_404(Department, pk=department_id)
            DocumentShare.objects.create(
                document=document,
                shared_with_department=recipient,
                remarks=remarks,
                shared_by=request.user
            )
            ActionLog.objects.create(
                document=document,
                action_by=request.user,  
                action=f"Shared to Department: {recipient.name}",
                comments=remarks
            )
            messages.success(request, f"Document shared with {recipient.name}.")
        elif share_with == 'ministry':
            ministry_id = request.POST.get('ministry')
            recipient = get_object_or_404(Ministry, pk=ministry_id)
            DocumentShare.objects.create(
                document=document,
                shared_with_ministry=recipient,
                remarks=remarks,
                shared_by=request.user
            )
            ActionLog.objects.create(
                document=document,
                action_by=request.user,  
                action=f"Shared to ministry: {recipient.name}",
                comments=remarks 
            )
            messages.success(request, f"Document shared with {recipient.name}.")
        return redirect('document_detail', pk=document.pk)

    return redirect('document_detail', pk=document.pk)

# view shared documents
@login_required
def user_shared_documents(request):
    shared_documents = DocumentShare.objects.filter(shared_with_user=request.user)
    paginator = Paginator(shared_documents, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for index, shared_documents in enumerate(page_obj.object_list):
        shared_documents.serial_number = index + 1 + (page_obj.number - 1) * paginator.per_page
    
    context = {
        'page_obj': page_obj
        }
    return render(request, 'shared/user_documents.html', context)

@login_required
def department_shared_documents(request):
    department = request.user.profile.department
    shared_documents = DocumentShare.objects.filter(shared_with_department=department)
    paginator = Paginator(shared_documents, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for index, shared_documents in enumerate(page_obj.object_list):
        shared_documents.serial_number = index + 1 + (page_obj.number - 1) * paginator.per_page

    return render(request, 'shared/department_documents.html', {'page_obj': page_obj})

@login_required
def ministry_shared_documents(request):
    ministry = request.user.profile.ministry
    shared_documents = DocumentShare.objects.filter(shared_with_ministry=ministry)
    paginator = Paginator(shared_documents, 10)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    for index, shared_documents in enumerate(page_obj.object_list):
        shared_documents.serial_number = index + 1 + (page_obj.number - 1) * paginator.per_page
    
    

    return render(request, 'shared/ministry_documents.html', {'page_obj': page_obj})


# Theme settings handles in user_management app
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

    return render(request, 'user_management/company_settings.html', {'form': form, 'theme_choice': theme_choice})

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


def summary_result(request):
    summary = request.session.get('summary', 'No summary available.')
    return render(request, 'documents/document_summary.html', {'summary': summary})



import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
tf.get_logger().setLevel('ERROR')
# Initialize the summarization pipeline with a specific model
# summarizer = pipeline("summarization", model="EleutherAI/gpt-neo-1.3B")
summarizer = pipeline("summarization", model="t5-small")
# summarizer = pipeline("summarization", model="facebook/bart-large-cnn", revision="main")

def summarize_pdf(request, document_id):
    print('docu id', document_id)
    try:
        document = get_object_or_404(Document, pk=document_id)
        pdf_path = document.file.path 
        messages.success(request, "Summarization started. Please wait...")


        # Extract text from the PDF
        text = extract_text_from_pdf(pdf_path)

        if not text:
            messages.error(request, "No text found in the PDF document.")
            return render(request, 'documents/document_summary.html')

        # If the document is too large, we return an error message
        if len(text) > 10000:  # Adjust this size threshold as needed
            messages.error(request, "Document is too large to summarize.")
            return render(request, 'documents/document_summary.html')

        # Generate summary
        summary = summarize_text(text)

        # Log the summarization action
        ActionLog.objects.create(
            document=document,
            action_by=request.user,
            action='Summarized',
            comments="Summary generated"
        )

        return render(request, 'documents/document_summary.html', {'summary': summary})

    except Exception as e:
        # Handle unexpected errors
        messages.error(request, f"An error occurred: {str(e)}")
        return render(request, 'documents/document_summary.html')

def extract_text_from_pdf(pdf_path):
    try:
        # Extract text from each page of the PDF
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        # Return an error if PDF extraction fails
        print(f"Error extracting text from PDF: {e}")
        return None

def summarize_text(text):
    try:
        max_input_length = 1024  # Adjust this based on model's token size
        chunk_size = max_input_length // 2  # Split into chunks of ~512 tokens
        text_chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        summary = ""
        for chunk in text_chunks:
            # Summarize each chunk
            chunk_summary = summarizer(chunk, max_length=100, min_length=30, do_sample=False)
            summary += chunk_summary[0]['summary_text'] + " "
        return summary

    except Exception as e:
        print(f"Error during text summarization: {e}")
        return "Error summarizing the text."



# def summarize_text(text):
#     if len(text.split()) < 10:  
#         return "Text too short to summarize"

#     input_length = len(text.split())
#     max_length = min(input_length // 5, 100)
#     summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
#     print(summary)
#     return summary[0]['summary_text']


