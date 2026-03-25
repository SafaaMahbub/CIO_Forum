from django import forms
from .models import CIO
from .models import UploadedFile



class CIOForm(forms.ModelForm):
    class Meta:
        model = CIO
        fields = ["name", "description"]



class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ["title", "file"]