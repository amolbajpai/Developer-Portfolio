from django.db import models


class Profile(models.Model):
    full_name = models.CharField(max_length=150)
    professional_title = models.CharField(max_length=200)
    eyebrow_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short line above the name, for example: Available for challenging Python & GenAI work",
    )
    summary = models.TextField()
    years_of_experience = models.DecimalField(max_digits=4, decimal_places=1)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    focus_label = models.CharField(max_length=50, blank=True, default="Focus")
    focus_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="Hero card focus line, for example: Generative AI · LangGraph · Python backends",
    )
    photo = models.ImageField(upload_to="profile/", blank=True, null=True)
    resume_file = models.FileField(upload_to="resume/", blank=True, null=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profile"

    def __str__(self):
        return self.full_name

    @property
    def location_display(self):
        parts = [self.city, self.state]
        if self.pincode:
            parts.append(self.pincode)
        return ", ".join(part for part in parts if part)


class Experience(models.Model):
    company = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Experience"
        verbose_name_plural = "Experience"
        ordering = ["sort_order", "-start_date"]

    def __str__(self):
        return f"{self.job_title} — {self.company}"

    @property
    def date_range(self):
        start = self.start_date.strftime("%b %Y")
        if self.is_current or not self.end_date:
            return f"{start} — Present"
        return f"{start} — {self.end_date.strftime('%b %Y')}"

    @property
    def location_display(self):
        return ", ".join(part for part in [self.city, self.state] if part)


class ExperienceBullet(models.Model):
    experience = models.ForeignKey(
        Experience, related_name="bullets", on_delete=models.CASCADE
    )
    text = models.TextField()
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Experience bullet"
        verbose_name_plural = "Experience bullets"
        ordering = ["sort_order", "id"]

    def __str__(self):
        return self.text[:80]


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ("genai", "Generative AI"),
        ("backend", "Backend"),
        ("database", "Database & Data"),
        ("cloud", "Cloud & DevOps"),
        ("observability", "Observability"),
        ("testing", "Testing & Quality"),
        ("frontend", "Frontend"),
        ("process", "Process"),
    ]

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=32, choices=CATEGORY_CHOICES)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        ordering = ["category", "sort_order", "name"]
        unique_together = ("name", "category")

    def __str__(self):
        return self.name


class Education(models.Model):
    degree = models.CharField(max_length=150)
    institution = models.CharField(max_length=200, blank=True)
    field_of_study = models.CharField(max_length=150, blank=True)
    start_year = models.PositiveIntegerField(blank=True, null=True)
    end_year = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Education"
        verbose_name_plural = "Education"
        ordering = ["sort_order", "-end_year"]

    def __str__(self):
        return self.degree


class Certification(models.Model):
    title = models.CharField(max_length=200)
    issuer = models.CharField(max_length=150, blank=True)
    issued_on = models.DateField(blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title


class Project(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    tech_stack = models.CharField(max_length=255, blank=True)
    github_url = models.URLField(blank=True)
    live_url = models.URLField(blank=True)
    image = models.ImageField(upload_to="projects/", blank=True, null=True)
    is_featured = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["sort_order", "title"]

    def __str__(self):
        return self.title

    @property
    def tech_list(self):
        if not self.tech_stack:
            return []
        return [item.strip() for item in self.tech_stack.split(",") if item.strip()]


class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=128, blank=True)
    verification_expires_at = models.DateTimeField(blank=True, null=True)
    verification_attempts = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Contact message"
        verbose_name_plural = "Contact messages"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} — {self.name}"


class ChatSession(models.Model):
    session_key = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Chat session"
        verbose_name_plural = "Chat sessions"
        ordering = ["-updated_at"]

    def __str__(self):
        return self.session_key


class ChatLog(models.Model):
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    session = models.ForeignKey(
        ChatSession, related_name="messages", on_delete=models.CASCADE
    )
    role = models.CharField(max_length=16, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Chat log"
        verbose_name_plural = "Chat logs"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.role}: {self.content[:60]}"


class SiteSettings(models.Model):
    google_api_key = models.CharField(
        "Gemini API key",
        max_length=255,
        blank=True,
        help_text="Google Gemini API key used by the chatbot.",
    )
    gemini_model = models.CharField(
        "Gemini model name",
        max_length=100,
        default="gemini-2.0-flash",
        help_text="Example: gemini-2.0-flash",
    )
    email_host = models.CharField("SMTP host", max_length=255, default="smtp.gmail.com")
    email_port = models.PositiveIntegerField("SMTP port", default=587)
    email_use_tls = models.BooleanField("Use TLS", default=True)
    email_use_ssl = models.BooleanField("Use SSL", default=False)
    email_host_user = models.CharField(
        "Email ID",
        max_length=254,
        blank=True,
        help_text="SMTP username / from mailbox.",
    )
    email_host_password = models.CharField(
        "Email password",
        max_length=255,
        blank=True,
        help_text="SMTP password or Gmail app password.",
    )
    default_from_email = models.CharField(
        "From email",
        max_length=254,
        blank=True,
        help_text="Leave blank to use Email ID.",
    )
    contact_recipient = models.CharField(
        "Contact inbox",
        max_length=254,
        blank=True,
        help_text="Where contact-form messages are delivered. Leave blank to use the profile email.",
    )

    class Meta:
        verbose_name = "API and email configuration"
        verbose_name_plural = "API and email configuration"

    def __str__(self):
        return "Site settings"

    @classmethod
    def load(cls):
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj

    def is_chat_configured(self):
        return bool(self.google_api_key.strip() and self.gemini_model.strip())

    def is_email_configured(self):
        return bool(
            self.email_host.strip()
            and self.email_host_user.strip()
            and self.email_host_password.strip()
        )
