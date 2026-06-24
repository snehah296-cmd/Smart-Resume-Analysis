from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),                             # Home page
    path('upload/', views.upload_resume, name='upload_resume'),    # Upload Resume page
    path('resumes/', views.my_resumes, name='my_resumes'),         # Resume list page
    path('logout/', views.logout_view, name='logout_view'),        # Logout
]
