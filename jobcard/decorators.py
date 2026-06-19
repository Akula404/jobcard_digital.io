from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from functools import wraps
from .models import UserProfile


def role_required(role):

    def decorator(view_func):

        @wraps(view_func)
        @login_required(login_url="/jobcard/login/")
        def wrapper(request, *args, **kwargs):

            profile = UserProfile.objects.filter(
                user=request.user
            ).first()

            if not profile:
                return render(
                    request,
                    "auth_required.html",
                    status=403
                )

            # Developer bypass
            if profile.role == "developer":
                return view_func(request, *args, **kwargs)

            if profile.role != role:
                return render(
                    request,
                    "auth_required.html",
                    status=403
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator