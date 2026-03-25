from django import forms
from .models import CIO

class CIOForm(forms.ModelForm):
    class Meta:
        model = CIO
        fields = ["name", "description"]