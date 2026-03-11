from django.shortcuts import render


def homepage(request):

    role = None

    if request.user.is_authenticated and hasattr(request.user, "profile"):
        role = request.user.profile.role

    return render(request, "homepage.html", {"role": role})
