# jobcard/views_auth.py

import hashlib
import hmac
import secrets

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils import timezone


OTP_LENGTH = 6
OTP_VALIDITY_SECONDS = 300  # 5 minutes
MAX_OTP_ATTEMPTS = 5


def _generate_otp():
    """
    Generate a cryptographically secure 6-digit OTP.
    """
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_otp(otp):
    """
    Hash the OTP using Django's SECRET_KEY.
    The actual OTP is never stored in the session.
    """
    return hmac.new(
        settings.SECRET_KEY.encode(),
        otp.encode(),
        hashlib.sha256
    ).hexdigest()


def login_view(request):

    if request.user.is_authenticated:
        return redirect("jobcard:role_redirect")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            return render(
                request,
                "registration/login.html",
                {
                    "error": "Please enter both username and password."
                }
            )

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is None:
            return render(
                request,
                "registration/login.html",
                {
                    "error": "Invalid username or password."
                }
            )

        if not user.is_active:
            return render(
                request,
                "registration/login.html",
                {
                    "error": "This account has been deactivated."
                }
            )

        # -------------------------------------------------
        # EMAIL REQUIREMENT
        # -------------------------------------------------

        if not user.email:
            return render(
                request,
                "registration/login.html",
                {
                    "error": (
                        "This account does not have a registered email address. "
                        "Please contact the system administrator."
                    )
                }
            )

        # -------------------------------------------------
        # GENERATE OTP
        # -------------------------------------------------

        otp = _generate_otp()

        request.session["otp_user_id"] = user.id
        request.session["otp_hash"] = _hash_otp(otp)
        request.session["otp_created_at"] = timezone.now().timestamp()
        request.session["otp_attempts"] = 0
        request.session["otp_next"] = request.POST.get("next", "")

        request.session.modified = True

        # -------------------------------------------------
        # SEND OTP
        # -------------------------------------------------

        try:

            send_mail(
                subject="Your Digital Job Card verification code",
                message=(
                    f"Hello {user.get_full_name() or user.username},\n\n"
                    f"Your verification code is: {otp}\n\n"
                    f"This code will expire in 5 minutes.\n\n"
                    f"If you did not attempt to sign in, please contact "
                    f"the system administrator."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        except Exception as e:

            print("EMAIL OTP ERROR:", repr(e))

            request.session.pop("otp_user_id", None)
            request.session.pop("otp_hash", None)
            request.session.pop("otp_created_at", None)
            request.session.pop("otp_attempts", None)
            request.session.pop("otp_next", None)

            return render(
                request,
                "registration/login.html",
                {
                    "error": f"Email error: {e}"
                }
            )

        # -------------------------------------------------
        # EMAIL SENT SUCCESSFULLY
        # -------------------------------------------------

        return redirect("jobcard:verify_otp")

    # -------------------------------------------------
    # GET REQUEST
    # -------------------------------------------------

    return render(
        request,
        "registration/login.html"
    )


def verify_otp(request):

    user_id = request.session.get("otp_user_id")
    stored_hash = request.session.get("otp_hash")
    created_at = request.session.get("otp_created_at")
    attempts = request.session.get("otp_attempts", 0)

    # -------------------------------------------------
    # CHECK OTP SESSION
    # -------------------------------------------------

    if not user_id or not stored_hash or not created_at:
        messages.error(
            request,
            "Your verification session has expired. Please sign in again."
        )
        return redirect("jobcard:login")

    # -------------------------------------------------
    # CHECK EXPIRATION
    # -------------------------------------------------

    elapsed = timezone.now().timestamp() - float(created_at)

    if elapsed > OTP_VALIDITY_SECONDS:

        request.session.pop("otp_user_id", None)
        request.session.pop("otp_hash", None)
        request.session.pop("otp_created_at", None)
        request.session.pop("otp_attempts", None)

        messages.error(
            request,
            "Your verification code has expired. Please sign in again."
        )

        return redirect("jobcard:login")

    # -------------------------------------------------
    # CHECK ATTEMPT LIMIT
    # -------------------------------------------------

    if attempts >= MAX_OTP_ATTEMPTS:

        request.session.pop("otp_user_id", None)
        request.session.pop("otp_hash", None)
        request.session.pop("otp_created_at", None)
        request.session.pop("otp_attempts", None)

        messages.error(
            request,
            "Too many incorrect verification attempts. Please sign in again."
        )

        return redirect("jobcard:login")

    if request.method == "POST":

        otp = request.POST.get("otp", "").strip()

        if not otp.isdigit() or len(otp) != OTP_LENGTH:

            request.session["otp_attempts"] = attempts + 1

            return render(
                request,
                "registration/verify_otp.html",
                {
                    "error": "Enter the 6-digit verification code."
                }
            )

        supplied_hash = _hash_otp(otp)

        if not hmac.compare_digest(supplied_hash, stored_hash):

            request.session["otp_attempts"] = attempts + 1

            remaining = MAX_OTP_ATTEMPTS - (attempts + 1)

            return render(
                request,
                "registration/verify_otp.html",
                {
                    "error": (
                        f"Invalid verification code. "
                        f"{remaining} attempt(s) remaining."
                    )
                }
            )

        # -------------------------------------------------
        # OTP SUCCESSFUL
        # -------------------------------------------------

        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            user = User.objects.get(
                id=user_id,
                is_active=True
            )
        except User.DoesNotExist:

            request.session.flush()

            messages.error(
                request,
                "The user account could not be found."
            )

            return redirect("jobcard:login")

        # -------------------------------------------------
        # NOW ACTUALLY LOG THE USER IN
        # -------------------------------------------------

        login(request, user)

        next_url = request.session.get("otp_next")

        # Remove OTP information
        request.session.pop("otp_user_id", None)
        request.session.pop("otp_hash", None)
        request.session.pop("otp_created_at", None)
        request.session.pop("otp_attempts", None)
        request.session.pop("otp_next", None)

        # -------------------------------------------------
        # REDIRECT
        # -------------------------------------------------

        if next_url:
            return redirect(next_url)

        return redirect("jobcard:role_redirect")

    return render(
        request,
        "registration/verify_otp.html"
    )