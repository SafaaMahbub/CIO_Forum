from django import forms
from .models import CIO
from .models import UploadedFile

from .models import CIO, Review, Profile



class StartDmForm(forms.Form):
    recipient_username = forms.CharField(
        max_length=150,
        label="Recipient username",
        help_text="The other person's login username (they must have a @virginia.edu email).",
    )


class DmMessageForm(forms.Form):
    body = forms.CharField(
        label="",
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Write a message…", "class": "dm-input"}),
    )


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

class profileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']
