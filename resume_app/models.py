from django.db import models
from django.contrib.auth.models import User
import os


def resume_upload_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f'resumes/user_{instance.user.id}/{filename}'


class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to=resume_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def filename(self):
        return os.path.basename(self.file.name)
    
    def file_extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension


class ResumeAnalysis(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='analysis')
    skills = models.JSONField(default=dict)
    experience = models.JSONField(default=dict)
    education = models.JSONField(default=dict)
    summary = models.TextField(blank=True, null=True)
    analyzed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Analysis for {self.resume.title}"


class CareerAdvice(models.Model):
    resume = models.OneToOneField(Resume, on_delete=models.CASCADE, related_name='career_advice')
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    recommended_skills = models.JSONField(default=list)
    career_paths = models.JSONField(default=list)
    advice = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Career Advice for {self.resume.title}"


class JobMatch(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='job_matches')
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    match_percentage = models.FloatField()
    job_description = models.TextField(blank=True, null=True)
    skills_matched = models.JSONField(default=list)
    skills_missing = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.job_title} - {self.match_percentage}% match"
