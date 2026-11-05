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

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if not re.fullmatch(r"\+?[0-9\s().-]{7,14}", phone):
            raise forms.ValidationError(
                "Enter a valid phone number using digits and optional +, spaces, hyphens or brackets."
            )

        digit_count = sum(character.isdigit() for character in phone)
        if not 7 <= digit_count <= 14:
            raise forms.ValidationError("The phone number must contain between 7 and 14 digits.")

        return phone

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")

        # On an edit form, resume may be the existing FieldFile. Only validate
        # a newly uploaded file here.
        if isinstance(resume, UploadedFile):
            allowed_extensions = {".pdf", ".doc", ".docx"}
            extension = Path(resume.name).suffix.lower()

            if extension not in allowed_extensions:
                raise forms.ValidationError("Upload a PDF, DOC or DOCX resume.")

            max_size = 5 * 1024 * 1024  # 5 MB
            if resume.size > max_size:
                raise forms.ValidationError("The resume must be 5 MB or smaller.")

        return resume


class ApplicationUpdateForm(ApplicationForm):
    """Form used by HR so applicants cannot set their own application status."""

    class Meta(ApplicationForm.Meta):
        fields = ["name", "email", "phone", "resume", "status"]
