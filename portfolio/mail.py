from django.core.mail import EmailMessage, get_connection

from .models import Profile, SiteSettings


class EmailNotConfigured(Exception):
    pass


def _smtp():
    config = SiteSettings.load()
    if not config.is_email_configured():
        raise EmailNotConfigured("Email is not configured in Site settings.")
    from_email = config.default_from_email.strip() or config.email_host_user.strip()
    connection = get_connection(
        host=config.email_host,
        port=config.email_port,
        username=config.email_host_user,
        password=config.email_host_password,
        use_tls=config.email_use_tls,
        use_ssl=config.email_use_ssl,
        fail_silently=False,
    )
    return config, connection, from_email


def send_otp_email(to_email, code):
    _config, connection, from_email = _smtp()
    email = EmailMessage(
        subject="Your portfolio contact verification code",
        body=(
            "Hi,\n\n"
            "Use this 6-digit code to confirm that this email belongs to you:\n\n"
            "    {}\n\n"
            "This code expires in 10 minutes. If you did not submit the contact form, "
            "you can ignore this message.\n"
        ).format(code),
        from_email=from_email,
        to=[to_email],
        connection=connection,
    )
    email.send()


def send_contact_email(message):
    config, connection, from_email = _smtp()
    profile = Profile.objects.first()
    recipient = (
        config.contact_recipient.strip()
        or (profile.email if profile else "")
        or config.email_host_user.strip()
    )
    if not recipient:
        raise EmailNotConfigured("No contact inbox is configured.")

    email = EmailMessage(
        subject="Portfolio contact: {}".format(message.subject),
        body=(
            "Verified contact message\n\n"
            "Name: {}\nEmail: {}\nSubject: {}\n\n{}".format(
                message.name, message.email, message.subject, message.message
            )
        ),
        from_email=from_email,
        to=[recipient],
        reply_to=[message.email],
        connection=connection,
    )
    email.send()
