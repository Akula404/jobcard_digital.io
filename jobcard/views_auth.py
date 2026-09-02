import hashlib
import hmac
import secrets
import logging
import resend

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.utils import timezone


# ============================================================
# LOGGING
# ============================================================

logger = logging.getLogger(__name__)


# ============================================================
# OTP SETTINGS
# ============================================================

OTP_LENGTH = 6
OTP_VALIDITY_SECONDS = 300  # 5 minutes
MAX_OTP_ATTEMPTS = 5


# ============================================================
# OTP HELPERS
# ============================================================

def _generate_otp():
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_otp(otp):
    return hmac.new(
        settings.SECRET_KEY.encode(),
        otp.encode(),
        hashlib.sha256
    ).hexdigest()


# ============================================================
# LOGIN
# ============================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect("jobcard:role_redirect")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        logger.info(
            "LOGIN START: username=%r",
            username
        )

        # ----------------------------------------------------
        # Validate input
        # ----------------------------------------------------

        if not username or not password:
            return render(
                request,
                "registration/login.html",
                {
                    "error": "Please enter both username and password."
                }
            )

        # ----------------------------------------------------
        # AUTHENTICATE USER
        # ----------------------------------------------------

        try:

            logger.info(
                "LOGIN: attempting authenticate() for %r",
                username
            )

            user = authenticate(
                request,
                username=username,
                password=password
            )

            logger.info(
                "LOGIN: authenticate() completed. user=%r",
                user
            )

        except Exception as e:

            logger.exception(
                "LOGIN AUTHENTICATE ERROR"
            )

            return render(
                request,
                "registration/login.html",
                {
                    "error": (
                        f"Authentication error: {e}"
                    )
                }
            )

        # ----------------------------------------------------
        # INVALID USER
        # ----------------------------------------------------

        if user is None:

            logger.warning(
                "LOGIN FAILED: invalid username/password for %r",
                username
            )

            return render(
                request,
                "registration/login.html",
                {
                    "error": "Invalid username or password."
                }
            )

        # ----------------------------------------------------
        # ACTIVE CHECK
        # ----------------------------------------------------

        if not user.is_active:

            logger.warning(
                "LOGIN FAILED: inactive user %r",
                username
            )

            return render(
                request,
                "registration/login.html",
                {
                    "error": "This account has been deactivated."
                }
            )

        # ----------------------------------------------------
        # EMAIL CHECK
        # ----------------------------------------------------

        logger.info(
            "LOGIN: user email configured=%s",
            bool(user.email)
        )

        if not user.email:

            return render(
                request,
                "registration/login.html",
                {
                    "error": (
                        "This account does not have a registered email "
                        "address. Please contact the system administrator."
                    )
                }
            )

        # ----------------------------------------------------
        # GENERATE OTP
        # ----------------------------------------------------

        try:

            otp = _generate_otp()

            logger.info(
                "LOGIN: OTP generated successfully"
            )

        except Exception as e:

            logger.exception(
                "OTP GENERATION ERROR"
            )

            return render(
                request,
                "registration/login.html",
                {
                    "error": f"OTP generation error: {e}"
                }
            )

        # ----------------------------------------------------
        # SAVE OTP TO SESSION
        # ----------------------------------------------------

        try:

            logger.info(
                "LOGIN: saving OTP information to session"
            )

            request.session["otp_user_id"] = user.id
            request.session["otp_hash"] = _hash_otp(otp)
            request.session["otp_created_at"] = timezone.now().timestamp()
            request.session["otp_attempts"] = 0
            request.session["otp_next"] = request.POST.get("next", "")

            request.session.modified = True

            logger.info(
                "LOGIN: OTP session data saved"
            )

        except Exception as e:

            logger.exception(
                "SESSION SAVE ERROR"
            )

            return render(
                request,
                "registration/login.html",
                {
                    "error": f"Session error: {e}"
                }
            )

        # ----------------------------------------------------
        # EMAIL CONFIGURATION DIAGNOSTICS
        # ----------------------------------------------------

        logger.info(
            "EMAIL CONFIG: host=%r",
            getattr(settings, "EMAIL_HOST", None)
        )

        logger.info(
            "EMAIL CONFIG: port=%r",
            getattr(settings, "EMAIL_PORT", None)
        )

        logger.info(
            "EMAIL CONFIG: username configured=%s",
            bool(getattr(settings, "EMAIL_HOST_USER", None))
        )

        logger.info(
            "EMAIL CONFIG: password configured=%s",
            bool(getattr(settings, "EMAIL_HOST_PASSWORD", None))
        )

        logger.info(
            "EMAIL CONFIG: default_from_email=%r",
            getattr(settings, "DEFAULT_FROM_EMAIL", None)
        )

        logger.info(
            "EMAIL CONFIG: recipient=%r",
            user.email
        )

        # ----------------------------------------------------
        # SEND OTP USING RESEND
        # ----------------------------------------------------

        try:

            logger.info(
                "EMAIL OTP: about to send email using Resend"
            )

            if not settings.RESEND_API_KEY:
                raise Exception(
                    "RESEND_API_KEY is not configured."
                )

            resend.api_key = settings.RESEND_API_KEY

            email_response = resend.Emails.send({
                "from": settings.DEFAULT_FROM_EMAIL,

                "to": [user.email],

                "subject": "Your Digital Job Card verification code",

                "html": f"""
                    <div style="font-family: Arial, sans-serif;">

                        <h2>Digital Job Card System</h2>

                        <p>
                            Hello {user.get_full_name() or user.username},
                        </p>

                        <p>
                            Your verification code is:
                        </p>

                        <h1>{otp}</h1>

                        <p>
                            This code will expire in 5 minutes.
                        </p>

                        <p>
                            If you did not attempt to sign in,
                            please contact the system administrator.
                        </p>

                    </div>
                """
            })

            logger.info(
                "EMAIL OTP: Resend accepted email: %r",
                email_response
            )

        except Exception as e:

            logger.exception(
                "RESEND EMAIL OTP ERROR"
            )

            request.session.pop("otp_user_id", None)
            request.session.pop("otp_hash", None)
            request.session.pop("otp_created_at", None)
            request.session.pop("otp_attempts", None)
            request.session.pop("otp_next", None)

            return render(
                request,
                "registration/login.html",
                {
                    "error": (
                        "Unable to send verification email. "
                        f"Email server error: {e}"
                    )
                }
            )

           

        # ----------------------------------------------------
        # REDIRECT TO OTP PAGE
        # ----------------------------------------------------

        logger.info(
            "LOGIN: redirecting user to OTP verification"
        )

        return redirect("jobcard:verify_otp")

    # ========================================================
    # GET REQUEST
    # ========================================================

    return render(
        request,
        "registration/login.html"
    )


# ============================================================
# VERIFY OTP
# ============================================================

def verify_otp(request):

    logger.info(
        "OTP VERIFY: request received. method=%s",
        request.method
    )

    user_id = request.session.get("otp_user_id")
    stored_hash = request.session.get("otp_hash")
    created_at = request.session.get("otp_created_at")
    attempts = request.session.get("otp_attempts", 0)

    # --------------------------------------------------------
    # SESSION CHECK
    # --------------------------------------------------------

    if not user_id or not stored_hash or not created_at:

        logger.warning(
            "OTP VERIFY: missing OTP session data"
        )

        messages.error(
            request,
            "Your verification session has expired. Please sign in again."
        )

        return redirect("jobcard:login")

    # --------------------------------------------------------
    # EXPIRY CHECK
    # --------------------------------------------------------

    elapsed = timezone.now().timestamp() - float(created_at)

    if elapsed > OTP_VALIDITY_SECONDS:

        logger.warning(
            "OTP VERIFY: OTP expired"
        )

        request.session.pop("otp_user_id", None)
        request.session.pop("otp_hash", None)
        request.session.pop("otp_created_at", None)
        request.session.pop("otp_attempts", None)

        messages.error(
            request,
            "Your verification code has expired. Please sign in again."
        )

        return redirect("jobcard:login")

    # --------------------------------------------------------
    # ATTEMPT LIMIT
    # --------------------------------------------------------

    if attempts >= MAX_OTP_ATTEMPTS:

        logger.warning(
            "OTP VERIFY: maximum attempts reached"
        )

        request.session.pop("otp_user_id", None)
        request.session.pop("otp_hash", None)
        request.session.pop("otp_created_at", None)
        request.session.pop("otp_attempts", None)

        messages.error(
            request,
            "Too many incorrect verification attempts. Please sign in again."
        )

        return redirect("jobcard:login")

    # --------------------------------------------------------
    # POST OTP
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # INVALID OTP
        # ----------------------------------------------------

        if not hmac.compare_digest(
            supplied_hash,
            stored_hash
        ):

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

        # ----------------------------------------------------
        # GET USER
        # ----------------------------------------------------

        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:

            logger.info(
                "OTP VERIFY: retrieving user id=%s",
                user_id
            )

            user = User.objects.get(
                id=user_id,
                is_active=True
            )

        except User.DoesNotExist:

            logger.warning(
                "OTP VERIFY: user does not exist"
            )

            request.session.flush()

            messages.error(
                request,
                "The user account could not be found."
            )

            return redirect("jobcard:login")

        except Exception as e:

            logger.exception(
                "OTP VERIFY: database error retrieving user"
            )

            return render(
                request,
                "registration/verify_otp.html",
                {
                    "error": f"Database error: {e}"
                }
            )

        # ----------------------------------------------------
        # LOGIN USER
        # ----------------------------------------------------

        try:

            logger.info(
                "OTP VERIFY: calling django login()"
            )

            login(
                request,
                user
            )

            logger.info(
                "OTP VERIFY: django login() completed"
            )

        except Exception as e:

            logger.exception(
                "DJANGO LOGIN ERROR"
            )

            return render(
                request,
                "registration/verify_otp.html",
                {
                    "error": f"Login error: {e}"
                }
            )

        # ----------------------------------------------------
        # NEXT URL
        # ----------------------------------------------------

        next_url = request.session.get("otp_next")

        # ----------------------------------------------------
        # CLEAR OTP SESSION
        # ----------------------------------------------------

        request.session.pop("otp_user_id", None)
        request.session.pop("otp_hash", None)
        request.session.pop("otp_created_at", None)
        request.session.pop("otp_attempts", None)
        request.session.pop("otp_next", None)

        logger.info(
            "OTP VERIFY: OTP session cleared"
        )

        # ----------------------------------------------------
        # REDIRECT
        # ----------------------------------------------------

        if next_url:

            logger.info(
                "OTP VERIFY: redirecting to next URL=%r",
                next_url
            )

            return redirect(next_url)

        logger.info(
            "OTP VERIFY: redirecting to role_redirect"
        )

        return redirect(
            "jobcard:role_redirect"
        )

    # ========================================================
    # GET OTP PAGE
    # ========================================================

    return render(
        request,
        "registration/verify_otp.html"
    )