from django import forms
from django.contrib.auth.models import User, Group

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff', 'is_active', 'groups']

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']
