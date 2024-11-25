from django import forms
from .models import *

class CompanySettingForm(forms.ModelForm):
    class Meta:
        model = CompanySetting
        fields = ['company_name', 'discount_percentage','min_points_to_redeem','theme_choice']  # Include discount_percentage in the fields list
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Customize company_name field
        self.fields['company_name'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Company Name'
        })
        
        # Customize discount_percentage field
        self.fields['discount_percentage'].widget = forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Discount Percentage (0-100)',
            'min': 0,
            'max': 100,
            'step': 0.01  # Allow decimal values for the percentage
        })

        # Customize min_points field
        self.fields['min_points_to_redeem'].widget = forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Minimum Points to Redeem',
            'min': 0,
            'step': 0.01  # Allow decimal values for the percentage
        })

        self.fields['theme_choice'].widget = forms.Select(
            attrs={'class': 'form-control'}
        )
        self.fields['theme_choice'].choices = [
            ('default', 'Default'),
            ('dark', 'Dark'),
            ('light', 'WineRed'),
            ('green', 'Green'),
        ]

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['name', 'description', 'file', 'priority']


class RelatedDocumentForm(forms.ModelForm):
    class Meta:
        model = RelatedDocument
        fields = ['related_file', 'remarks']


class WorkflowForm(forms.ModelForm):
    class Meta:
        model = Workflow
        fields = ['department', 'status', 'remarks']