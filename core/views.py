from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CIOForm
from .models import CIOMembership


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