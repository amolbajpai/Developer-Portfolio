from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ("name", "email", "subject", "message")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Your name",
                    "autocomplete": "name",
                    "class": "field-input",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "you@example.com",
                    "autocomplete": "email",
                    "class": "field-input",
                }
            ),
            "subject": forms.TextInput(
                attrs={"placeholder": "Subject", "class": "field-input"}
            ),
            "message": forms.Textarea(
                attrs={
                    "placeholder": "Write your message here...",
                    "rows": 5,
                    "class": "field-input",
                }
            ),
        }


class ContactOTPForm(forms.Form):
    code = forms.CharField(
        min_length=6,
        max_length=6,
        widget=forms.TextInput(
            attrs={
                "placeholder": "6-digit code",
                "class": "field-input",
                "inputmode": "numeric",
                "autocomplete": "one-time-code",
            }
        ),
    )
