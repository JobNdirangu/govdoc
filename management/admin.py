from django.contrib import admin
from .models import Document, RelatedDocument, ActionLog, Workflow, Department, DocumentMovement

admin.site.register(Document)
admin.site.register(RelatedDocument)
admin.site.register(ActionLog)
admin.site.register(Workflow)
admin.site.register(Department)
admin.site.register(DocumentMovement)