import json
import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.shortcuts import redirect, render
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from .ai_agent import generate_reply
from .forms import ContactForm, ContactOTPForm
from .mail import EmailNotConfigured, send_contact_email, send_otp_email
from .models import (
    Certification,
    ChatLog,
    ChatSession,
    ContactMessage,
    Education,
    Experience,
    Profile,
    Project,
    SiteSettings,
    Skill,
)

OTP_MINUTES = 10
OTP_MAX_ATTEMPTS = 5


def mask_email(email):
    local, _, domain = email.partition("@")
    if not domain:
        return email
    if len(local) <= 2:
        shown = local[:1] + "*"
    else:
        shown = local[:2] + "***"
    return "{}@{}".format(shown, domain)


def _issue_otp(message):
    code = "{:06d}".format(secrets.randbelow(1000000))
    message.verification_code = make_password(code)
    message.verification_expires_at = timezone.now() + timedelta(minutes=OTP_MINUTES)
    message.verification_attempts = 0
    message.is_verified = False
    message.save(
        update_fields=[
            "verification_code",
            "verification_expires_at",
            "verification_attempts",
            "is_verified",
        ]
    )
    send_otp_email(message.email, code)


def _pending_message(request):
    message_id = request.session.get("pending_contact_id")
    if not message_id:
        return None
    try:
        message = ContactMessage.objects.get(pk=message_id, is_verified=False)
    except ContactMessage.DoesNotExist:
        request.session.pop("pending_contact_id", None)
        return None
    return message


def _portfolio_context(contact_form=None, contact_error=False, otp_form=None):
    skills = list(Skill.objects.all())
    skills_by_category = []
    for value, label in Skill.CATEGORY_CHOICES:
        group = [skill for skill in skills if skill.category == value]
        if group:
            skills_by_category.append((label, group))
    return {
        "profile": Profile.objects.first(),
        "experiences": Experience.objects.prefetch_related("bullets").all(),
        "skills_by_category": skills_by_category,
        "education_list": Education.objects.all(),
        "certifications": Certification.objects.all(),
        "projects": Project.objects.filter(is_featured=True),
        "contact_form": contact_form or ContactForm(),
        "otp_form": otp_form or ContactOTPForm(),
        "chat_configured": SiteSettings.load().is_chat_configured(),
        "contact_error": contact_error,
    }


def home(request):
    context = _portfolio_context()
    context["contact_success"] = request.session.pop("contact_success", False)
    context["contact_email_error"] = request.session.pop("contact_email_error", False)
    context["otp_error"] = request.session.pop("otp_error", False)
    pending = _pending_message(request)
    context["pending_contact"] = pending
    context["pending_email_masked"] = mask_email(pending.email) if pending else ""
    return render(request, "portfolio/home.html", context)


@require_POST
def contact(request):
    form = ContactForm(request.POST)
    if form.is_valid():
        item = form.save(commit=False)
        item.is_verified = False
        item.save()
        try:
            _issue_otp(item)
            request.session["pending_contact_id"] = item.id
        except EmailNotConfigured:
            item.delete()
            request.session["contact_email_error"] = (
                "Email is not configured. Open Admin → API and email configuration."
            )
        except Exception:
            item.delete()
            request.session["contact_email_error"] = (
                "Could not send a verification code. Check SMTP settings in Admin."
            )
        return redirect("/#contact")
    context = _portfolio_context(contact_form=form, contact_error=True)
    return render(request, "portfolio/home.html", context)


@require_POST
def contact_verify(request):
    pending = _pending_message(request)
    form = ContactOTPForm(request.POST)
    if pending is None:
        request.session["otp_error"] = "No pending message to verify."
        return redirect("/#contact")
    if not form.is_valid():
        context = _portfolio_context(otp_form=form)
        context["pending_contact"] = pending
        context["pending_email_masked"] = mask_email(pending.email)
        return render(request, "portfolio/home.html", context)

    code = form.cleaned_data["code"].strip()
    if pending.verification_attempts >= OTP_MAX_ATTEMPTS:
        request.session["otp_error"] = "Too many attempts. Request a new code."
        return redirect("/#contact")
    if (
        not pending.verification_expires_at
        or timezone.now() > pending.verification_expires_at
    ):
        request.session["otp_error"] = "That code has expired. Request a new code."
        return redirect("/#contact")

    pending.verification_attempts += 1
    pending.save(update_fields=["verification_attempts"])
    if not check_password(code, pending.verification_code):
        request.session["otp_error"] = "That code is not correct."
        return redirect("/#contact")

    pending.is_verified = True
    pending.verification_code = ""
    pending.save(update_fields=["is_verified", "verification_code"])
    try:
        send_contact_email(pending)
        request.session["contact_success"] = True
    except Exception:
        request.session["contact_email_error"] = (
            "Email was verified, but the message could not be delivered. Try again later."
        )
    request.session.pop("pending_contact_id", None)
    return redirect("/#contact")


@require_POST
def contact_resend(request):
    pending = _pending_message(request)
    if pending is None:
        request.session["otp_error"] = "No pending message to verify."
        return redirect("/#contact")
    try:
        _issue_otp(pending)
    except Exception:
        request.session["otp_error"] = "Could not resend the verification code."
    return redirect("/#contact")


def _get_or_create_session(session_key):
    if not session_key:
        session_key = str(uuid.uuid4())
    session, _created = ChatSession.objects.get_or_create(session_key=session_key)
    return session


@require_POST
def chat_api(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    message = (payload.get("message") or "").strip()
    session_key = (payload.get("session_key") or "").strip()
    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)

    session = _get_or_create_session(session_key)
    history = list(
        reversed(
            list(
                session.messages.order_by("-created_at")[: settings.CHAT_HISTORY_LIMIT]
            )
        )
    )

    ChatLog.objects.create(session=session, role="user", content=message)

    if not SiteSettings.load().is_chat_configured():
        reply = "The chat service is not configured."
        ChatLog.objects.create(session=session, role="assistant", content=reply)
        return JsonResponse(
            {
                "error": "Gemini API key is not configured in Site settings.",
                "reply": reply,
                "session_key": session.session_key,
            },
            status=503,
        )

    try:
        reply = generate_reply(history, message)
    except Exception:
        reply = "The chat service is temporarily unavailable. Please try again later."
        ChatLog.objects.create(session=session, role="assistant", content=reply)
        return JsonResponse(
            {
                "error": "The chat service is temporarily unavailable.",
                "reply": reply,
                "session_key": session.session_key,
            },
            status=502,
        )

    ChatLog.objects.create(session=session, role="assistant", content=reply)
    session.save(update_fields=["updated_at"])
    return JsonResponse({"reply": reply, "session_key": session.session_key})


@require_GET
def chat_history(request):
    session_key = (request.GET.get("session_key") or "").strip()
    if not session_key:
        return JsonResponse({"messages": [], "session_key": ""})

    try:
        session = ChatSession.objects.get(session_key=session_key)
    except ChatSession.DoesNotExist:
        return JsonResponse({"messages": [], "session_key": session_key})

    messages = [
        {"role": item.role, "content": item.content}
        for item in session.messages.order_by("created_at")
    ]
    return JsonResponse({"messages": messages, "session_key": session.session_key})
