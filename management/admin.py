from django.contrib import admin
from .models import Document, RelatedDocument, ActionLog, Workflow, Department, DocumentAccess,ApprovalTask,Ministry,CompanySetting,Profile,DocumentShare

admin.site.register(Document)
admin.site.register(RelatedDocument)
admin.site.register(ActionLog)
admin.site.register(Workflow)
admin.site.register(Department)
admin.site.register(DocumentAccess)
admin.site.register(ApprovalTask)
admin.site.register(CompanySetting)
admin.site.register(Ministry)
admin.site.register(DocumentShare)
admin.site.register(Profile)