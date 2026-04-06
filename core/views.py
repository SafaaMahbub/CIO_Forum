from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.contrib.auth.views import redirect_to_login

from .forms import CIOForm, UploadedFileForm, ReviewForm, StartDmForm, DmMessageForm, profileForm
from .models import (
    CIOMembership,
    CIO,
    Review,
    UploadedFile,
    Conversation,
    Message,
    get_or_create_conversation,
)


def _email_is_uva(user):
    return (user.email or "").lower().endswith("@virginia.edu")


def uva_dm_only(view_func):
    """Logged-in users with @virginia.edu email only."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not _email_is_uva(request.user):
            messages.error(
                request,
                "Direct messaging is only available for @virginia.edu accounts.",
            )
            return redirect("homepage")
        return view_func(request, *args, **kwargs)

    return _wrapped

def homepage(request):
    role = None
    display_name = None
    uploads = UploadedFile.objects.all()
    cios = CIO.objects.all()

    if request.user.is_authenticated:
        display_name = request.user.email or request.user.username

        if hasattr(request.user, "profile"):
            role = request.user.profile.role

    return render(request, "home.html", {
        "role": role,
        "display_name": display_name,
        "uploads": uploads,
        "cios": cios,
    })
@login_required
def profile(request):
    form = profileForm(instance=request.user.profile)
    if request.method == "POST":
        form = profileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            if 'profile_picture' in request.FILES:
                form.save()
                messages.success(request, "Profile has been updated successfully.")
            else:
                messages.error(request, "Profile has not been updated successfully.")
            return redirect("profile")
        else:
            messages.error(request, "Please try again")

    return render(request, "profile.html", {
        "profile": request.user.profile, "form": form
    })

@login_required
def create_cio(request):
    profile = request.user.profile

    if profile.role not in ["student", "exec"]:
        messages.error(request, "You do not have permission to create a CIO.")
        return redirect("profile")

    if request.method == "POST":
        form = CIOForm(request.POST)
        if form.is_valid():
            cio = form.save()

            CIOMembership.objects.create(
                profile=profile,
                cio=cio,
                is_active=True
            )

            return redirect("profile")
    else:
        form = CIOForm()

    return render(request, "create_cio.html", {"form": form})

@login_required
def upload_file(request, cio_id):
    cio = get_object_or_404(CIO, id=cio_id)

    # Restrict uploads based on role
    if not hasattr(request.user, "profile") or request.user.profile.role == "guest":
        return HttpResponseForbidden("Guests cannot upload files.")

    if request.method == "POST":
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.cio = cio
            uploaded_file.uploaded_by = request.user
            uploaded_file.save()
            return redirect("homepage")
    else:
        form = UploadedFileForm()

    return render(request, "upload_file.html", {"form": form, "cio": cio})

def view_upload(request, id):
    upload = UploadedThing.objects.get(id=id)
    return render(request, "view_upload.html", {"upload": upload})

def create_review(request):
    profile =request.user.profile
    if profile.role not in ["student", "exec"]:
        messages.error(request, "You do not have permission to create a review for a CIO.")
        return redirect("profile")
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():

            #this checks if the current user submitted a review for the cio - if they already submitted
            #a review,the page will display an error message will appear
            if Review.objects.filter(profile=profile,cio=form.cleaned_data["cio"]).exists():
                messages.error(request, "Review already exists. Please choose a different CIO from the list.")
                return redirect("create_review")

            Review.objects.create(
                profile=request.user.profile,
                cio=form.cleaned_data["cio"],
                comment=form.cleaned_data["comment"]
            )
            messages.success(request, "Review has been created successfully.")
            return redirect("viewAllReviews")
    else:
        form = ReviewForm()
    return render(request, "create_review.html", {"form": form})


@uva_dm_only
def messages_inbox(request):
    convs = (
        Conversation.objects.filter(Q(user1=request.user) | Q(user2=request.user))
        .order_by("-updated_at")
    )
    rows = []
    for c in convs:
        other = c.other_participant(request.user)
        last = c.messages.order_by("-created_at").first()
        rows.append({"conversation": c, "other": other, "last": last})
    return render(request, "messages/inbox.html", {"rows": rows})


@uva_dm_only
def messages_thread(request, conversation_id):
    conv = get_object_or_404(
        Conversation.objects.filter(Q(user1=request.user) | Q(user2=request.user)),
        pk=conversation_id,
    )
    other = conv.other_participant(request.user)
    if request.method == "POST":
        form = DmMessageForm(request.POST)
        if form.is_valid():
            body = form.cleaned_data["body"].strip()
            if body:
                Message.objects.create(
                    conversation=conv,
                    sender=request.user,
                    body=body,
                )
            return redirect("messages_thread", conversation_id=conv.id)
    else:
        form = DmMessageForm()
    msg_list = conv.messages.select_related("sender").all()
    return render(
        request,
        "messages/thread.html",
        {
            "conversation": conv,
            "other": other,
            "message_list": msg_list,
            "form": form,
        },
    )


@uva_dm_only
def messages_new(request):
    if request.method == "POST":
        form = StartDmForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["recipient_username"].strip()
            try:
                recipient = User.objects.get(username__iexact=username)
            except User.DoesNotExist:
                messages.error(request, "No user with that username.")
                return render(request, "messages/new.html", {"form": form})
            if recipient.pk == request.user.pk:
                messages.error(request, "You cannot message yourself.")
                return render(request, "messages/new.html", {"form": form})
            if not _email_is_uva(recipient):
                messages.error(
                    request,
                    "You can only message other users with a @virginia.edu email.",
                )
                return render(request, "messages/new.html", {"form": form})
            conv = get_or_create_conversation(request.user, recipient)
            return redirect("messages_thread", conversation_id=conv.id)
    else:
        form = StartDmForm()
    return render(request, "messages/new.html", {"form": form})


@uva_dm_only
def messages_start_user(request, user_id):
    recipient = get_object_or_404(User, pk=user_id)
    if recipient.pk == request.user.pk:
        messages.error(request, "You cannot message yourself.")
        return redirect("messages_inbox")
    if not _email_is_uva(recipient):
        messages.error(
            request,
            "You can only message users with a @virginia.edu email.",
        )
        return redirect("messages_inbox")
    conv = get_or_create_conversation(request.user, recipient)
    return redirect("messages_thread", conversation_id=conv.id)


def viewAllReviews(request):
    reviews = Review.objects.select_related("profile__user","cio").all()

    return render(request, "view_all_reviews.html",{"reviews": reviews})
