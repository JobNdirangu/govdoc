from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete,post_save
from django.dispatch import receiver


class Ministry(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    ministry = models.ForeignKey(Ministry, on_delete=models.CASCADE, null=True, blank=True, related_name="departments")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
class Document(models.Model):
    """Main document model."""
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
    ]
    ACTION_CHOICES = [
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Deleted', 'Deleted'),
        ('None', 'None'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='documents/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    upload_date = models.DateTimeField(auto_now_add=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')
    action = models.CharField(max_length=15, choices=ACTION_CHOICES, default='None')

    def __str__(self):
        return self.name


class RelatedDocument(models.Model):
    """Documents related to the main document."""
    parent_document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='related_documents')
    related_file = models.FileField(upload_to='related_documents/')
    added_by = models.ForeignKey(User, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Related to {self.parent_document.name}"


class ActionLog(models.Model):
    """Tracks actions performed on documents."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='action_logs')
    action_by = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=15, choices=Document.ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True)

    @receiver(post_save, sender=Document)
    def log_document_action(sender, instance, created, **kwargs):
        action = 'created' if created else 'updated'
        ActionLog.objects.create(
            document=instance,
            action_by=instance.uploaded_by,
            action=action,
            comments=f"Document {action}."
        )

    @receiver(pre_delete, sender=Document)
    def log_document_deletion(sender, instance, **kwargs):
        ActionLog.objects.create(
            document=instance,
            action_by=instance.uploaded_by,
            action='deleted',
            comments="Document deleted"
        )

    def __str__(self):
        return f"Action {self.action} on {self.document.name}"


class Workflow(models.Model):
    """Tracks approval workflows and status updates."""
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Under Review', 'Under Review'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='workflows')
    department = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_workflows')
    remarks = models.TextField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Workflow for {self.document.name} - {self.status}"


class DocumentMovement(models.Model):
    """Tracks the movement of documents between departments."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='movements')
    from_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='outgoing_documents')
    to_department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='incoming_documents')
    moved_by = models.ForeignKey(User, on_delete=models.CASCADE)
    move_date = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Movement of {self.document.name} from {self.from_department} to {self.to_department}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User to whom the notification belongs
    message = models.TextField()  # The content of the notification
    is_read = models.BooleanField(default=False)  # Status of the notification
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of when the notification was created
    link = models.URLField(null=True, blank=True)  # Optional link related to the notification

    def __str__(self):
        return f'Notification for {self.user.username}: {self.message}'

class CompanySetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_settings', null=True, blank=True)
    company_name = models.CharField(max_length=100, default="W&SMS")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    theme_choice = models.CharField(
        max_length=20,
        choices=[
            ('default', 'Default'),
            ('dark', 'Dark'),
            ('light', 'Light'),
            ('green', 'Green'),
        ],
        default='default'
    )
    min_points_to_redeem = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.company_name

