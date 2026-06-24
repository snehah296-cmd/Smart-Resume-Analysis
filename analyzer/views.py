from .forms import ResumeForm
from django.shortcuts import render


from .models import Resume  # Make sure you import your Resume model
from django.contrib.auth import logout
from django.contrib import messages

from django.contrib.auth.decorators import login_required
import fitz  # PyMuPDF
job_roles = {
    "Data Scientist": {"python", "machine learning", "statistics", "data analysis"},
    "Web Developer": {"html", "css", "javascript", "react"},
}



@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return render(request, 'analyzer/home.html')


def home(request):
    return render(request, 'analyzer/home.html')  # or 'home.html' depending on your template structure

def my_resumes(request):
    resumes = Resume.objects.all().order_by('-uploaded_at')  # Or filter by user if applicable
    return render(request, 'my_resumes.html', {'resumes': resumes})


def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_skills(text):
    words = set(text.lower().split())
    found_skills = set()
    for role_keywords in job_roles.values():
        found_skills |= role_keywords & words
    return found_skills

def match_job_role(skills):
    best_match = ""
    highest_score = 0
    for role, keywords in job_roles.items():
        match_count = len(skills & keywords)
        score = match_count / len(keywords)
        if score > highest_score:
            best_match = role
            highest_score = score
    return best_match, round(highest_score * 100, 2)

def upload_resume(request):
    result = None
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save()
            text = extract_text_from_pdf(resume.file.path)
            skills = extract_skills(text)

            role, score = match_job_role(skills)
            role_keywords = set(job_roles[role]) if role else set()

            matched_skills = sorted(list(role_keywords.intersection(skills)))
            unmatched_resume_skills = sorted(list(skills - role_keywords))
            missing_job_skills = sorted(list(role_keywords - skills))

            resume.score = score
            resume.matched_role = role
            resume.save()

            result = {
                'role': role,
                'score': score,
                'matched_skills': matched_skills,
                'unmatched_resume_skills': unmatched_resume_skills,
                'missing_job_skills': missing_job_skills
            }
    else:
        form = ResumeForm()
    return render(request, 'upload.html', {'form': form, 'result': result})