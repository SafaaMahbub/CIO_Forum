from django import forms
from .models import CIO
from .models import UploadedFile

from .models import CIO, Review, Profile, Comment, Category



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
    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Categories (optional)",
    )

    class Meta:
        model = CIO
        fields = ["name", "description", "cio_profile_picture", "categories"]


class CIOEditForm(forms.ModelForm):
    """Edit form for existing CIOs; profile picture is optional on edit."""

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Categories (optional)",
    )

    class Meta:
        model = CIO
        fields = ["name", "description", "cio_profile_picture", "categories"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cio_profile_picture"].required = False
        self.fields["cio_profile_picture"].help_text = (
            "Leave empty to keep the current profile picture."
        )

class UploadedFileForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ["title", "file"]

RATING_CHOICES = [(None, "No rating")] + [(i, str(i)) for i in range(1, 6)]
YEAR_CHOICES = [
    ("", "Prefer not to say"),
    (1, "1st Year"),
    (2, "2nd Year"),
    (3, "3rd Year"),
    (4, "4th Year"),
]

class ReviewForm(forms.Form):
    cio = forms.ModelChoiceField(queryset=CIO.objects.all(), label="Select a CIO")
    comment = forms.CharField(widget=forms.Textarea(), label="Add a comment")
    anonymous = forms.TypedChoiceField(
        choices=[("", "---------"), (True, "Yes"), (False, "No")],
        coerce=lambda x: x == "True",
        required=True,
        label="Submit anonymously?",
    )
    year = forms.TypedChoiceField(
        choices=YEAR_CHOICES,
        coerce=int,
        required=False,
        empty_value=None,
        label="Your year (optional)",
    )
    rating_career_development = forms.TypedChoiceField(
        choices=RATING_CHOICES, coerce=int, required=False,
        empty_value=None, label="Career Development (1-5)",
    )
    rating_event_quality = forms.TypedChoiceField(
        choices=RATING_CHOICES, coerce=int, required=False,
        empty_value=None, label="Event Quality (1-5)",
    )
    rating_time_commitment = forms.TypedChoiceField(
        choices=RATING_CHOICES, coerce=int, required=False,
        empty_value=None, label="Time Commitment (1-5)",
    )
    rating_community_inclusiveness = forms.TypedChoiceField(
        choices=RATING_CHOICES, coerce=int, required=False,
        empty_value=None, label="Community & Inclusiveness (1-5)",
    )

class profileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']


class CommentForm(forms.ModelForm):
    anonymous = forms.TypedChoiceField(
        choices=[(False, "No"), (True, "Yes")],
        coerce=lambda x: x == "True",
        required=True,
        label="Post anonymously?",
        initial=False,
    )

    class Meta:
        model = Comment
        fields = ["text", "anonymous"]
        widgets = {
            "text": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Write a comment…",
                "class": "comment-input",
            }),
        }
        labels = {"text": ""}
