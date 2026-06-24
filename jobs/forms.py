from django import forms
from .models import JobPost, Resume  # ✅ FIXED: Import both models

class ResumeUploadForm(forms.Form):
    resume = forms.FileField()

class JobPostForm(forms.ModelForm):
    class Meta:
        model = JobPost
        fields = [
            'title',
          
            'location',
            'job_type',
            'salary_range',
            'description',
            'required_skills',  # If same as requirements
            'benefits',
            'contact_email'
        ]


class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['name', 'email', 'file']
