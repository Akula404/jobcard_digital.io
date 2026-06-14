# jobcard/views_auth.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import UserProfile

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            profile = UserProfile.objects.get(user=user)

            if profile.role == "supervisor":
                return redirect("jobcard:supervisor_dashboard")
            else:
                return redirect("jobcard:operator_entry")

        return render(request, "login.html", {"error": "Invalid credentials"})

    return render(request, "login.html")