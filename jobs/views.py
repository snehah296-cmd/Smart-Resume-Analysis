from django.shortcuts import render, redirect, get_object_or_404  # Add get_object_or_404
from .forms import JobPostForm
from django.contrib.auth.decorators import login_required
from .models import JobPost, JobApplication, Resume  # Add JobApplication here
import PyPDF2
import io
from django.core.files.storage import default_storage
from django.conf import settings
from .forms import ResumeUploadForm
from .forms import ResumeForm
import fitz  # PyMuPDF
from django.contrib.auth import logout
from django.contrib import messages

# Remove the duplicate import since you already imported Resume above
# from .models import Resume  # Remove this duplicate line
job_roles = {
    "Data Scientist": {"python", "machine learning", "statistics", "data analysis"},
    "Web Developer": {"html", "css", "javascript", "react"},
}




@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('home')  # Make sure 'home' is a valid URL name in your urls.py


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






# @login_required
# def upload_resume(request):
#     if request.user.is_jobseeker:
#         matched_jobs = []
#         skills = []

#         if request.method == 'POST':
#             form = ResumeUploadForm(request.POST, request.FILES)
#             if form.is_valid():
#                 resume = request.FILES['resume']
#                 text = extract_text_from_pdf(resume)
#                 skills = extract_skills_from_text(text)

#                 all_jobs = JobPost.objects.all()
#                 for job in all_jobs:
#                     required = [s.strip().lower() for s in job.required_skills.split(',')]
#                     match_score = len(set(skills).intersection(required))
#                     if match_score > 0:
#                         matched_jobs.append((job, match_score))

#                 matched_jobs.sort(key=lambda x: x[1], reverse=True)
#         else:
#             form = ResumeUploadForm()

#         return render(request, 'jobs/match_jobs.html', {
#             'form': form,
#             'skills': skills,
#             'matched_jobs': matched_jobs
#         })
#     else:
#         return redirect('dashboard')


# def extract_text_from_pdf(file):
#     reader = PyPDF2.PdfReader(file)
#     text = ""
#     for page in reader.pages:
#         text += page.extract_text() or ""
#     return text.lower()


# def extract_skills_from_text(text):
#     keywords = ['python', 'java', 'django', 'react', 'sql', 'html', 'css', 'machine learning', 'ai', 'excel']
#     found_skills = [kw for kw in keywords if kw in text]
#     return found_skills





@login_required
def post_job(request):
    print(f"=== POST_JOB VIEW CALLED ===")
    print(f"User: {request.user}")
    print(f"Is company: {getattr(request.user, 'is_company', False)}")
    print(f"Request method: {request.method}")
    
    if request.user.is_company:
        if request.method == 'POST':
            print("POST request received")
            form = JobPostForm(request.POST)
            print(f"Form data: {request.POST}")
            
            # Remove 'company' from the form if it's being validated
            if form.is_valid():
                print("Form is VALID ✓")
                job = form.save(commit=False)
                job.company = request.user  # Set company here
                print(f"Job object created: {job}")
                print(f"Job title: {job.title}")
                print(f"Job company: {job.company}")
                job.save()
                print(f"Job saved successfully! Job ID: {job.id}")
                return redirect('company_jobs')
            else:
                print("Form is INVALID ✗")
                print(f"Form errors: {form.errors}")
        else:
            print("GET request - displaying empty form")
            form = JobPostForm()
        return render(request, 'jobs/post_job.html', {'form': form})
    else:
        print("User is NOT a company - redirecting to dashboard")
        return redirect('dashboard')
#@login_required
#def company_jobs(request):
#    if request.user.is_company:
#        jobs = JobPost.objects.filter(company=request.user)
#        return render(request, 'jobs/company_jobs.html', {'jobs': jobs})
#    else:
#        return redirect('dashboard')


    


@login_required
def company_jobs(request):
    jobs = JobPost.objects.filter(company=request.user)
    print(f"User: {request.user}")
    print(f"Is company: {getattr(request.user, 'is_company', False)}")
    print(f"Number of jobs found: {jobs.count()}")
    print(f"Jobs: {list(jobs)}")
    
    for job in jobs:
        if job.required_skills:
            job.skills_list = [skill.strip() for skill in job.required_skills.split(',')]
        else:
            job.skills_list = []
    return render(request, 'jobs/company_jobs.html', {'jobs': jobs})

# Alternative approach if you want to process skills in the view instead:
@login_required
def company_jobs_with_processing(request):
    jobs = JobPost.objects.filter(company=request.user)
    
    # Process skills for each job if you prefer to do it in the view
    for job in jobs:
        if job.required_skills:
            job.skills_list = [skill.strip() for skill in job.required_skills.split(',')]
        else:
            job.skills_list = []
    
    return render(request, 'jobs/company_jobs.html', {'jobs': jobs})
    



@login_required
def browse_jobs(request):
    """Show all available jobs for job seekers to apply"""
    if request.user.is_jobseeker:
        jobs = JobPost.objects.all().order_by('-posted_at')
        
        # Process skills for each job
        for job in jobs:
            if job.required_skills:
                job.skills_list = [skill.strip() for skill in job.required_skills.split(',')]
            else:
                job.skills_list = []
        
        return render(request, 'jobs/browse_jobs.html', {'jobs': jobs})
    else:
        return redirect('dashboard')


@login_required
def apply_job(request, job_id):
    if request.user.is_jobseeker:
        job = get_object_or_404(JobPost, id=job_id)  # Use get_object_or_404 instead of get()
        
        # Check if already applied
        if JobApplication.objects.filter(job=job, applicant=request.user).exists():
            messages.warning(request, f"You have already applied for {job.title}")
        else:
            JobApplication.objects.create(job=job, applicant=request.user)
            messages.success(request, f"Successfully applied for {job.title}!")
        
        return redirect('browse_jobs')
    else:
        return redirect('dashboard')