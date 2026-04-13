from django.http import HttpResponseForbidden
from functools import wraps


def block_user_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.profile.role == 'user_admin':
            return HttpResponseForbidden("User Admin cannot access this feature")
        return view_func(request, *args, **kwargs)
    return wrapper

def user_admin_only(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # ONLY check role — assume user is already logged in
        if request.user.profile.role != "user_admin":
            return HttpResponseForbidden("User Admins only")
        return view_func(request, *args, **kwargs)
    return wrapper