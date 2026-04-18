from functools import wraps

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.contrib.auth.views import redirect_to_login
from .decorators import block_user_admin, user_admin_only

from .forms import CIOForm, UploadedFileForm, ReviewForm, StartDmForm, DmMessageForm, profileForm
from .models import (
    CIOLeadership,
    CIOMembership,
    MembershipRequest,
    CIO,
    Review,
    UploadedFile,
    Conversation,
    Message,
    get_or_create_conversation,
)


@login_required
def redirect_after_login(request):
    if request.user.profile.role == "user_admin":
        return redirect("manage_users")
    else:
        return redirect("homepage")

@login_required
@user_admin_only
# Manage users logic for user admin
def manage_users(request):
    users = User.objects.all()
    return render(request, 'manage_users.html', {'users': users})

@login_required
@user_admin_only
def update_role(request, user_id):
    if request.method == "POST":
        user = User.objects.get(id=user_id)
        new_role = request.POST.get('role')

        # Prevent modifying yourself
        if user == request.user:
            return HttpResponseForbidden("Cannot modify your own role")

        # Prevent assigning user_admin
        if new_role == 'user_admin':
            return HttpResponseForbidden('Cannot assign User Admin role')

        user.profile.role = new_role
        user.profile.save()

    return redirect('manage_users')

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


def _attach_review_verification_flags(reviews):
    reviews = list(reviews)
    verified_pairs = set(
        CIOLeadership.objects.filter(is_active=True).values_list("profile_id", "cio_id")
    )
    verified_pairs.update(
        CIOMembership.objects.filter(is_active=True).values_list("profile_id", "cio_id")
    )

    for review in reviews:
        review.is_member_verified = (review.profile_id, review.cio_id) in verified_pairs

    return reviews

def homepage(request):
    cios = CIO.objects.all()
    reviews = _attach_review_verification_flags(
        Review.objects.select_related("profile__user", "cio").all()
    )
    return render(request, "home.html", {"cios": cios, "reviews": reviews})

@login_required
@block_user_admin
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
@block_user_admin
def create_cio(request):
    profile = request.user.profile

    if profile.role != "student":
        messages.error(request, "You do not have permission to create a CIO.")
        return redirect("profile")

    if request.method == "POST":
        form = CIOForm(request.POST, request.FILES)
        if form.is_valid():
            cio = form.save()

            CIOLeadership.objects.create(
                profile=profile,
                cio=cio,
                is_active=True
            )

            return redirect("profile")
    else:
        form = CIOForm()

    return render(request, "create_cio.html", {"form": form})

@login_required
@block_user_admin
def upload_file(request, cio_id):
    cio = get_object_or_404(CIO, id=cio_id)

    if not hasattr(request.user, "profile") or not cio.leaderships.filter(profile=request.user.profile, is_active=True).exists():
        return HttpResponseForbidden("Only CIO leaders can upload files.")

    if request.method == "POST":
        form = UploadedFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.save(commit=False)
            uploaded_file.cio = cio
            uploaded_file.uploaded_by = request.user
            uploaded_file.save()
            return redirect("viewAllCios")
    else:
        form = UploadedFileForm()

    return render(request, "upload_file.html", {"form": form, "cio": cio})

@block_user_admin
def view_upload(request, id):
    upload = UploadedThing.objects.get(id=id)
    return render(request, "view_upload.html", {"upload": upload})

@block_user_admin
def create_review(request):
    profile =request.user.profile
    if profile.role != "student":
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

            cio = form.cleaned_data["cio"]
            Review.objects.create(
                profile=request.user.profile,
                cio=cio,
                comment=form.cleaned_data["comment"],
                anonymous=form.cleaned_data["anonymous"],
                rating_career_development=form.cleaned_data.get("rating_career_development"),
                rating_event_quality=form.cleaned_data.get("rating_event_quality"),
                rating_time_commitment=form.cleaned_data.get("rating_time_commitment"),
                rating_community_inclusiveness=form.cleaned_data.get("rating_community_inclusiveness"),
            )
            cio.update_average_ratings()
            messages.success(request, "Review has been created successfully.")
            return redirect("viewAllReviews")
    else:
        form = ReviewForm()
    return render(request, "create_review.html", {"form": form})

@uva_dm_only
@block_user_admin
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

    pending_requests = []
    if hasattr(request.user, "profile"):
        led_cio_ids = request.user.profile.leaderships.filter(
            is_active=True
        ).values_list("cio_id", flat=True)
        if led_cio_ids:
            pending_requests = MembershipRequest.objects.filter(
                cio_id__in=led_cio_ids, status="pending"
            ).select_related("profile__user", "cio").order_by("-created_at")

    return render(request, "messages/inbox.html", {
        "rows": rows,
        "pending_requests": pending_requests,
    })

@uva_dm_only
@block_user_admin
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
    conv.messages.filter(is_read=False).exclude(sender=request.user).update(is_read=True)
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
@block_user_admin
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
@block_user_admin
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

@block_user_admin
def cio_homepage(request, cio_id):
    cio = get_object_or_404(CIO, id=cio_id)
    reviews = Review.objects.filter(cio=cio).select_related("profile__user")
    leaders = cio.leaderships.filter(is_active=True).select_related("profile__user")
    members = cio.memberships.filter(is_active=True).select_related("profile__user")
    role = None
    is_leader = False
    is_member = False
    has_pending_request = False
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        profile = request.user.profile
        role = profile.role
        is_leader = leaders.filter(profile=profile).exists()
        is_member = members.filter(profile=profile).exists()
        has_pending_request = MembershipRequest.objects.filter(
            profile=profile, cio=cio, status="pending"
        ).exists()
    return render(request, "cio_homepage.html", {
        "cio": cio, "reviews": reviews, "leaders": leaders, "members": members,
        "role": role, "is_leader": is_leader, "is_member": is_member,
        "has_pending_request": has_pending_request,
    })

@block_user_admin
def viewAllReviews(request):
    reviews = _attach_review_verification_flags(
        Review.objects.select_related("profile__user", "cio").all()
    )
    return render(request, "view_all_reviews.html", {"reviews": reviews})

@block_user_admin
def viewAllCios(request):
    role = None
    display_name = None
    uploads = UploadedFile.objects.all()
    cios = CIO.objects.all()

    if request.user.is_authenticated:
        display_name = request.user.email or request.user.username

        if hasattr(request.user, "profile"):
            role = request.user.profile.role

    return render(request, "view_all_cios.html", {
        "role": role,
        "display_name": display_name,
        "uploads": uploads,
        "cios": cios,
    })


@login_required
@block_user_admin
def request_membership(request, cio_id):
    cio = get_object_or_404(CIO, id=cio_id)
    profile = request.user.profile

    if profile.role != "student":
        messages.error(request, "Only students can request CIO membership.")
        return redirect("cio_homepage", cio_id=cio.id)

    if cio.leaderships.filter(profile=profile, is_active=True).exists():
        messages.info(request, "You are already a leader of this CIO.")
        return redirect("cio_homepage", cio_id=cio.id)

    if cio.memberships.filter(profile=profile, is_active=True).exists():
        messages.info(request, "You are already a member of this CIO.")
        return redirect("cio_homepage", cio_id=cio.id)

    if MembershipRequest.objects.filter(profile=profile, cio=cio, status="pending").exists():
        messages.info(request, "You already have a pending request for this CIO.")
        return redirect("cio_homepage", cio_id=cio.id)

    if request.method == "POST":
        msg = request.POST.get("message", "").strip()
        MembershipRequest.objects.update_or_create(
            profile=profile, cio=cio,
            defaults={"message": msg, "status": "pending"},
        )
        messages.success(request, "Your membership request has been sent!")
        return redirect("cio_homepage", cio_id=cio.id)

    return render(request, "request_membership.html", {"cio": cio})


@login_required
@block_user_admin
def handle_membership_request(request, request_id, action):
    mem_request = get_object_or_404(MembershipRequest, id=request_id, status="pending")
    cio = mem_request.cio
    profile = request.user.profile

    if not cio.leaderships.filter(profile=profile, is_active=True).exists():
        return HttpResponseForbidden("Only CIO leaders can manage membership requests.")

    requester_user = mem_request.profile.user

    if action == "approve":
        mem_request.status = "approved"
        mem_request.save()
        CIOMembership.objects.get_or_create(
            profile=mem_request.profile, cio=cio,
            defaults={"is_active": True},
        )
        dm_body = f"Your request to join {cio.name} has been approved! Welcome aboard."
        messages.success(request, f"Approved {requester_user.username} as a member.")
    elif action == "reject":
        mem_request.status = "rejected"
        mem_request.save()
        dm_body = f"Your request to join {cio.name} has been declined."
        messages.info(request, f"Rejected {requester_user.username}'s request.")
    else:
        return redirect("messages_inbox")

    conv = get_or_create_conversation(request.user, requester_user)
    Message.objects.create(conversation=conv, sender=request.user, body=dm_body)

    return redirect("messages_inbox")