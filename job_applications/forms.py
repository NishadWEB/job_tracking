import re
from pathlib import Path

from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["name", "email", "phone", "resume"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your full name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+91 9876543210"}),
        }

class ApplicationUpdateForm(ApplicationForm):
    """Form used by HR so applicants cannot set their own application status."""

    class Meta(ApplicationForm.Meta):
        fields = ["name", "email", "phone", "resume", "status"]
