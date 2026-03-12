from django.shortcuts import render


def homepage(request):
    role = None
    display_name = None

    if request.user.is_authenticated:
        display_name = request.user.email or request.user.username

        if hasattr(request.user, "profile"):
            role = request.user.profile.role

    return render(request, "homepage.html", {
        "role": role,
        "display_name": display_name,
    })