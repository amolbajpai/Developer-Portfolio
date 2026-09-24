from datetime import datetime
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from portfolio.models import (
    Certification,
    Education,
    Experience,
    ExperienceBullet,
    Profile,
    Project,
    Skill,
)


def _clean(value):
    if pd.isna(value):
        return None
    return value


def _date(value):
    value = _clean(value)
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if hasattr(value, "to_pydatetime"):
        return value.to_pydatetime().date()
    return pd.to_datetime(value).date()


def _bool(value, default=False):
    value = _clean(value)
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


class Command(BaseCommand):
    help = "Import portfolio tables from an Excel workbook created by export_portfolio."

    def add_arguments(self, parser):
        parser.add_argument("workbook", help="Path to the .xlsx file")

    def handle(self, *args, **options):
        path = Path(options["workbook"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        sheets = pd.read_excel(path, sheet_name=None, engine="openpyxl")
        with transaction.atomic():
            self._import_profile(sheets.get("profile"))
            self._import_experience(sheets.get("experience"), sheets.get("experience_bullets"))
            self._import_skills(sheets.get("skills"))
            self._import_education(sheets.get("education"))
            self._import_certifications(sheets.get("certifications"))
            self._import_projects(sheets.get("projects"))
        self.stdout.write(self.style.SUCCESS(f"Imported portfolio data from {path}"))

    def _import_profile(self, frame):
        if frame is None or frame.empty:
            return
        row = frame.iloc[0]
        Profile.objects.update_or_create(
            email=str(row["email"]),
            defaults={
                "full_name": row.get("full_name", ""),
                "professional_title": row.get("professional_title", ""),
                "eyebrow_text": str(row.get("eyebrow_text") or ""),
                "summary": row.get("summary", ""),
                "years_of_experience": row.get("years_of_experience") or 0,
                "city": row.get("city", "") or "",
                "state": row.get("state", "") or "",
                "pincode": str(row.get("pincode") or ""),
                "phone": str(row.get("phone") or ""),
                "linkedin_url": str(row.get("linkedin_url") or ""),
                "github_url": str(row.get("github_url") or ""),
                "focus_label": str(row.get("focus_label") or "Focus"),
                "focus_text": str(row.get("focus_text") or ""),
            },
        )

    def _import_experience(self, experience_frame, bullet_frame):
        if experience_frame is None:
            return
        ExperienceBullet.objects.all().delete()
        Experience.objects.all().delete()
        id_map = {}
        for _, row in experience_frame.iterrows():
            job = Experience.objects.create(
                company=row.get("company") or "",
                job_title=row.get("job_title") or "",
                city=row.get("city") or "",
                state=row.get("state") or "",
                start_date=_date(row.get("start_date")),
                end_date=_date(row.get("end_date")),
                is_current=_bool(row.get("is_current")),
                sort_order=int(row.get("sort_order") or 0),
            )
            old_id = _clean(row.get("id"))
            if old_id is not None:
                id_map[int(old_id)] = job
        if bullet_frame is None:
            return
        for _, row in bullet_frame.iterrows():
            old_id = _clean(row.get("experience_id"))
            job = id_map.get(int(old_id)) if old_id is not None else None
            if not job:
                continue
            ExperienceBullet.objects.create(
                experience=job,
                text=row.get("text") or "",
                sort_order=int(row.get("sort_order") or 0),
            )

    def _import_skills(self, frame):
        if frame is None:
            return
        Skill.objects.all().delete()
        for _, row in frame.iterrows():
            Skill.objects.create(
                name=row.get("name") or "",
                category=row.get("category") or "backend",
                sort_order=int(row.get("sort_order") or 0),
            )

    def _import_education(self, frame):
        if frame is None:
            return
        Education.objects.all().delete()
        for _, row in frame.iterrows():
            Education.objects.create(
                degree=row.get("degree") or "",
                institution=row.get("institution") or "",
                field_of_study=row.get("field_of_study") or "",
                start_year=_clean(row.get("start_year")),
                end_year=_clean(row.get("end_year")),
                description=row.get("description") or "",
                sort_order=int(row.get("sort_order") or 0),
            )

    def _import_certifications(self, frame):
        if frame is None:
            return
        Certification.objects.all().delete()
        for _, row in frame.iterrows():
            Certification.objects.create(
                title=row.get("title") or "",
                issuer=row.get("issuer") or "",
                issued_on=_date(row.get("issued_on")),
                sort_order=int(row.get("sort_order") or 0),
            )

    def _import_projects(self, frame):
        if frame is None:
            return
        Project.objects.all().delete()
        for _, row in frame.iterrows():
            Project.objects.create(
                title=row.get("title") or "",
                short_description=row.get("short_description") or "",
                description=row.get("description") or "",
                tech_stack=row.get("tech_stack") or "",
                github_url=str(row.get("github_url") or ""),
                live_url=str(row.get("live_url") or ""),
                is_featured=_bool(row.get("is_featured"), default=True),
                sort_order=int(row.get("sort_order") or 0),
            )
