# jobs/models.py
from django.db import models
from accounts.models import CustomUser
from django.conf import settings

class JobPost(models.Model):
    company = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'is_company': True})
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=50, default='Full-time')
    salary_range = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    required_skills = models.TextField()
    benefits = models.TextField(blank=True)
    contact_email = models.EmailField(default='hr@example.com')
    posted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} at {self.company.username}"
    
    def get_skills_list(self):
        """Return a list of skills split by comma"""
        if self.required_skills:
            return [skill.strip() for skill in self.required_skills.split(',')]
        return []
    
    def get_short_description(self):
        """Return truncated description for preview"""
        if len(self.description) > 150:
            return self.description[:150] + "..."
        return self.description
    
    def get_posted_date(self):
        """Return formatted posted date"""
        return self.posted_at.strftime('%B %d, %Y')

class Resume(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_file_size(self):
        """Return file size in human readable format"""
        if self.file:
            size = self.file.size
            if size < 1024:
                return f"{size} bytes"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "Unknown"
    
    def get_uploaded_date(self):
        """Return formatted upload date"""
        return self.uploaded_at.strftime('%B %d, %Y at %I:%M %p')

# ✅ FIXED: JobApplication now uses JobPost instead of Job
class JobApplication(models.Model):
    APPLICATION_STATUS = [
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    ]
    
    # Changed from Job to JobPost
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE)  # ✅ FIXED
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cover_letter = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS, default='applied')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['job', 'applicant']
    
    def __str__(self):
        return f"{self.applicant.username} applied for {self.job.title}"

# ❌ You can REMOVE this Job model if you're not using it
# class Job(models.Model):
#     title = models.CharField(max_length=200)
#     company = models.CharField(max_length=200)
#     location = models.CharField(max_length=100)
#     description = models.TextField()
#     requirements = models.TextField()
#     salary = models.CharField(max_length=100, blank=True)
#     posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     
#     def __str__(self):
#         return f"{self.title} at {self.company}"