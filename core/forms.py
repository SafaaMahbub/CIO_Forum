from django import forms
from .models import CIO
from .models import UploadedFile

from .models import CIO, Review


class CIOForm(forms.ModelForm):
    class Meta:
        model = CIO
        fields = ["name", "description"]

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ["title", "file"]

class ReviewForm(forms.Form):
    cio = forms.ModelChoiceField(queryset=CIO.objects.all(), label="Select a CIO")
    comment = forms.CharField(widget=forms.Textarea(), label="Add a comment")
