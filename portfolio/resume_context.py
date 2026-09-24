from .models import (
    Certification,
    Education,
    Experience,
    Profile,
    Project,
    Skill,
)


def build_resume_context():
    profile = Profile.objects.first()
    if not profile:
        return "No portfolio profile has been published yet."

    lines = [
        f"Name: {profile.full_name}",
        f"Title: {profile.professional_title}",
        f"Years of experience: {profile.years_of_experience}",
        f"Location: {profile.location_display}",
        f"Phone: {profile.phone}",
        f"Email: {profile.email}",
    ]
    if profile.linkedin_url:
        lines.append(f"LinkedIn: {profile.linkedin_url}")
    if profile.github_url:
        lines.append(f"GitHub: {profile.github_url}")
    if profile.eyebrow_text:
        lines.append(f"Headline: {profile.eyebrow_text}")
    if profile.focus_text:
        label = profile.focus_label or "Focus"
        lines.append(f"{label}: {profile.focus_text}")
    lines.extend(["", "Summary:", profile.summary, "", "Experience:"])

    for job in Experience.objects.prefetch_related("bullets").all():
        location = f" ({job.location_display})" if job.location_display else ""
        lines.append(f"- {job.job_title} at {job.company}{location}, {job.date_range}")
        for bullet in job.bullets.all():
            lines.append(f"  * {bullet.text}")

    lines.append("")
    lines.append("Skills:")
    for skill in Skill.objects.all():
        lines.append(f"- {skill.name} ({skill.get_category_display()})")

    lines.append("")
    lines.append("Education:")
    for edu in Education.objects.all():
        years = ""
        if edu.start_year or edu.end_year:
            years = f" ({edu.start_year or ''}–{edu.end_year or ''})"
        institution = f", {edu.institution}" if edu.institution else ""
        field = f" in {edu.field_of_study}" if edu.field_of_study else ""
        lines.append(f"- {edu.degree}{field}{institution}{years}")
        if edu.description:
            lines.append(f"  {edu.description}")

    lines.append("")
    lines.append("Certifications:")
    for cert in Certification.objects.all():
        issuer = f" — {cert.issuer}" if cert.issuer else ""
        lines.append(f"- {cert.title}{issuer}")

    projects = Project.objects.filter(is_featured=True)
    if projects.exists():
        lines.append("")
        lines.append("Projects:")
        for project in projects:
            lines.append(f"- {project.title}: {project.short_description or project.description}")
            if project.tech_stack:
                lines.append(f"  Tech: {project.tech_stack}")

    return "\n".join(lines)
