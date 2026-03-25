from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CIOForm
from .models import CIOMembership, CIO, Review
from .forms import ReviewForm
from django.http import HttpResponseRedirect


def homepage(request):
    role = None
    display_name = None

    if request.user.is_authenticated:
        display_name = request.user.email or request.user.username

        if hasattr(request.user, "profile"):
            role = request.user.profile.role

    return render(request, "home.html", {
        "role": role,
        "display_name": display_name,
    })

@login_required
def profile(request):
    return render(request, "profile.html", {
        "profile": request.user.profile
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
def create_review(request):
    profile =request.user.profile
    if profile.role not in ["student", "exec"]:
        messages.error(request, "You do not have permission to create a review for a CIO.")
        return redirect("profile")
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():

            #this checks if the current user submitted a review for the cio - if they already submitted
            #a ,the page will display an error message will appear
            if Review.objects.filter(profile=profile,cio=form.cleaned_data["cio"]).exists():
                messages.error(request, "Review already exists. Please choose a different CIO from the list.")
                return redirect("create_review")

            Review.objects.create(
                profile=request.user.profile,
                cio=form.cleaned_data["cio"],
                comment=form.cleaned_data["comment"]
            )
            messages.success(request, "Review has been created successfully.")
            return redirect("profile")
    else:
        form = ReviewForm()
    return render(request, "create_review.html", {"form": form})