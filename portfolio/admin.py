from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import (
    Certification,
    ChatLog,
    ChatSession,
    ContactMessage,
    Education,
    Experience,
    ExperienceBullet,
    Profile,
    Project,
    SiteSettings,
    Skill,
)


class ExperienceBulletInline(admin.TabularInline):
    model = ExperienceBullet
    extra = 1


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "professional_title", "eyebrow_text", "focus_text", "email", "phone", "city")


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = "__all__"
        widgets = {
            "google_api_key": forms.TextInput(
                attrs={"autocomplete": "off", "style": "width: 42em"}
            ),
            "gemini_model": forms.TextInput(attrs={"style": "width: 28em"}),
            "email_host_user": forms.TextInput(attrs={"style": "width: 28em"}),
            "email_host_password": forms.TextInput(
                attrs={"autocomplete": "off", "style": "width: 28em"}
            ),
            "default_from_email": forms.TextInput(attrs={"style": "width: 28em"}),
            "contact_recipient": forms.TextInput(attrs={"style": "width: 28em"}),
        }


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    form = SiteSettingsForm
    list_display = (
        "gemini_model",
        "api_key_preview",
        "email_host_user",
        "email_host",
        "email_port",
        "contact_recipient",
    )
    fieldsets = (
        (
            "Chatbot",
            {
                "fields": ("google_api_key", "gemini_model"),
                "description": "Gemini API key and model name used by the portfolio chatbot.",
            },
        ),
        (
            "Email",
            {
                "fields": (
                    "email_host",
                    "email_port",
                    "email_use_tls",
                    "email_use_ssl",
                    "email_host_user",
                    "email_host_password",
                    "default_from_email",
                    "contact_recipient",
                ),
                "description": "SMTP settings for the contact form. For Gmail use smtp.gmail.com, port 587, TLS, and an app password.",
            },
        ),
    )

    def api_key_preview(self, obj):
        key = (obj.google_api_key or "").strip()
        if not key:
            return "Not set"
        if len(key) <= 8:
            return "Set"
        return "{}…{}".format(key[:4], key[-4:])

    api_key_preview.short_description = "Gemini API key"

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        return redirect(
            reverse("admin:portfolio_sitesettings_change", args=[obj.pk])
        )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = (
        "job_title",
        "company",
        "start_date",
        "end_date",
        "is_current",
        "sort_order",
    )
    list_filter = ("is_current", "company")
    search_fields = ("company", "job_title")
    inlines = [ExperienceBulletInline]


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "sort_order")
    list_filter = ("category",)
    search_fields = ("name",)


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("degree", "institution", "field_of_study", "end_year")


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("title", "issuer", "issued_on")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "is_featured", "sort_order")
    list_filter = ("is_featured",)
    search_fields = ("title", "tech_stack")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("subject", "name", "email", "is_verified", "created_at", "is_read")
    list_filter = ("is_verified", "is_read")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = (
        "name",
        "email",
        "subject",
        "message",
        "created_at",
        "is_verified",
        "verification_expires_at",
        "verification_attempts",
    )


class ChatLogInline(admin.TabularInline):
    model = ChatLog
    extra = 0
    readonly_fields = ("role", "content", "created_at")
    can_delete = False


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ("session_key", "created_at", "updated_at")
    search_fields = ("session_key",)
    inlines = [ChatLogInline]


admin.site.site_header = "Developer Portfolio Admin"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Content management"
