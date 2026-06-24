from django.urls import path
from . import views

urlpatterns = [
    path('upload-resume/', views.upload_resume, name='upload_resume'),
    path('post/', views.post_job, name='post_job'),
    path('my-jobs/', views.company_jobs, name='company_jobs'),
    path('jobs/browse/', views.browse_jobs, name='browse_jobs'),
    path('jobs/apply/<int:job_id>/', views.apply_job, name='apply_job'),
]
