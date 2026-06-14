from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

def login_view(request):

    error = None

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect("dashboard")

        error = "Invalid username or password"

    return render(
        request,
        "login.html",
        {"error": error}
    )


@login_required
def dashboard_view(request):

    is_supervisor = request.user.groups.filter(
        name="Supervisor"
    ).exists()

    context = {
        "is_supervisor": is_supervisor
    }

    return render(
        request,
        "dashboard.html",
        context
    )