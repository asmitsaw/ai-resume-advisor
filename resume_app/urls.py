from django.urls import path
from . import views

app_name = 'resume_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_resume, name='upload_resume'),
    path('analyze/<int:resume_id>/', views.analyze_resume, name='analyze_resume'),
    path('career_advice/<int:resume_id>/', views.career_advice, name='career_advice'),
    path('job_match/<int:resume_id>/', views.job_match, name='job_match'),
    path('job_match_detail/<int:match_id>/', views.job_match_detail, name='job_match_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
]