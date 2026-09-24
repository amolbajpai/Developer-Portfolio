from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand

from portfolio.models import (
    Certification,
    ContactMessage,
    Education,
    Experience,
    ExperienceBullet,
    Profile,
    Project,
    Skill,
)


class Command(BaseCommand):
    help = "Export portfolio tables to an Excel workbook."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            default="portfolio_export.xlsx",
            help="Output .xlsx path (default: portfolio_export.xlsx)",
        )

    def handle(self, *args, **options):
        output = Path(options["output"])
        sheets = {
            "profile": self._profile_rows(),
            "experience": self._experience_rows(),
            "experience_bullets": self._bullet_rows(),
            "skills": list(Skill.objects.values("id", "name", "category", "sort_order")),
            "education": list(
                Education.objects.values(
                    "id",
                    "degree",
                    "institution",
                    "field_of_study",
                    "start_year",
                    "end_year",
                    "description",
                    "sort_order",
                )
            ),
            "certifications": list(
                Certification.objects.values(
                    "id", "title", "issuer", "issued_on", "sort_order"
                )
            ),
            "projects": list(
                Project.objects.values(
                    "id",
                    "title",
                    "short_description",
                    "description",
                    "tech_stack",
                    "github_url",
                    "live_url",
                    "is_featured",
                    "sort_order",
                )
            ),
            "contact_messages": list(
                ContactMessage.objects.values(
                    "id", "name", "email", "subject", "message", "created_at", "is_read"
                )
            ),
        }
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            for name, rows in sheets.items():
                frame = pd.DataFrame(rows)
                frame.to_excel(writer, sheet_name=name, index=False)
        self.stdout.write(self.style.SUCCESS(f"Exported portfolio data to {output}"))

    def _profile_rows(self):
        rows = []
        for item in Profile.objects.all():
            rows.append(
                {
                    "id": item.id,
                    "full_name": item.full_name,
                    "professional_title": item.professional_title,
                    "eyebrow_text": item.eyebrow_text,
                    "summary": item.summary,
                    "years_of_experience": item.years_of_experience,
                    "city": item.city,
                    "state": item.state,
                    "pincode": item.pincode,
                    "phone": item.phone,
                    "email": item.email,
                    "linkedin_url": item.linkedin_url,
                    "github_url": item.github_url,
                    "focus_label": item.focus_label,
                    "focus_text": item.focus_text,
                }
            )
        return rows

    def _experience_rows(self):
        rows = []
        for item in Experience.objects.all():
            rows.append(
                {
                    "id": item.id,
                    "company": item.company,
                    "job_title": item.job_title,
                    "city": item.city,
                    "state": item.state,
                    "start_date": item.start_date,
                    "end_date": item.end_date,
                    "is_current": item.is_current,
                    "sort_order": item.sort_order,
                }
            )
        return rows

    def _bullet_rows(self):
        rows = []
        for item in ExperienceBullet.objects.select_related("experience"):
            rows.append(
                {
                    "id": item.id,
                    "experience_id": item.experience_id,
                    "company": item.experience.company,
                    "job_title": item.experience.job_title,
                    "text": item.text,
                    "sort_order": item.sort_order,
                }
            )
        return rows
