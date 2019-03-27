from django import forms
from .models import Assignment


class AssignmentForm(forms.ModelForm):

    class Meta:
        model = Assignment
        fields = ('name', 'active', "git_source", "git_username", "git_password")
