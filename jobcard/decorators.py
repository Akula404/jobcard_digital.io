from django.http import HttpResponseForbidden
from .models import UserProfile

def role_required(required_role):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Not logged in")

            try:
                profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                return HttpResponseForbidden("No role assigned")

            if profile.role != required_role:
                return HttpResponseForbidden("Not allowed")

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator