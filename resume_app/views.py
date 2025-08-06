from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import logout
from .models import Resume, ResumeAnalysis, CareerAdvice, JobMatch
from .forms import ResumeUploadForm, JobSearchForm, UserRegistrationForm
from .resume_analyzer import ResumeParser, CareerAdvisor, JobMatcher
import os


def home(request):
    """Home page view"""
    return render(request, 'resume_app/home.html')


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'resume_app/register.html', {'form': form})


def logout_view(request):
    """Custom logout view that works with both GET and POST requests"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('resume_app:home')


@login_required
def upload_resume(request):
    """View for uploading a resume"""
    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create resume object but don't save to DB yet
            resume = form.save(commit=False)
            # Add user to resume
            resume.user = request.user
            # Save resume to DB
            resume.save()
            
            messages.success(request, 'Resume uploaded successfully!')
            return redirect('resume_app:analyze_resume', resume_id=resume.id)
    else:
        form = ResumeUploadForm()
    
    return render(request, 'resume_app/upload_resume.html', {'form': form})


@login_required
def analyze_resume(request, resume_id):
    """View for analyzing a resume"""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Check if analysis already exists
    try:
        analysis = resume.analysis
        # Analysis exists, redirect to results
        return render(request, 'resume_app/analysis_results.html', {
            'resume': resume,
            'analysis': analysis
        })
    except ResumeAnalysis.DoesNotExist:
        # Analysis doesn't exist, create it
        try:
            # Get file path
            file_path = resume.file.path
            
            # Parse resume
            parser = ResumeParser()
            analysis_results = parser.parse_resume(file_path)
            
            # Create analysis object
            analysis = ResumeAnalysis.objects.create(
                resume=resume,
                skills=analysis_results['skills'],
                education=analysis_results['education'],
                experience=analysis_results['experience'],
                summary=analysis_results['summary']
            )
            
            messages.success(request, 'Resume analyzed successfully!')
            return render(request, 'resume_app/analysis_results.html', {
                'resume': resume,
                'analysis': analysis
            })
        except Exception as e:
            messages.error(request, f'Error analyzing resume: {str(e)}')
            return redirect('resume_app:upload_resume')


@login_required
def career_advice(request, resume_id):
    """View for providing career advice based on resume analysis"""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Check if analysis exists
    try:
        analysis = resume.analysis
    except ResumeAnalysis.DoesNotExist:
        messages.error(request, 'Resume must be analyzed first!')
        return redirect('resume_app:analyze_resume', resume_id=resume.id)
    
    # Check if career advice already exists
    try:
        advice = resume.career_advice
        # Advice exists, show it
        return render(request, 'resume_app/career_advice.html', {
            'resume': resume,
            'advice': advice
        })
    except CareerAdvice.DoesNotExist:
        # Advice doesn't exist, create it
        try:
            # Generate career advice
            advisor = CareerAdvisor()
            advice_results = advisor.generate_career_advice({
                'skills': analysis.skills,
                'education': analysis.education,
                'experience': analysis.experience,
                'summary': analysis.summary
            })
            
            # Create advice object
            advice = CareerAdvice.objects.create(
                resume=resume,
                strengths=advice_results['strengths'],
                weaknesses=advice_results['weaknesses'],
                recommended_skills=advice_results['recommended_skills'],
                career_paths=advice_results['career_paths'],
                advice=advice_results['advice']
            )
            
            messages.success(request, 'Career advice generated successfully!')
            return render(request, 'resume_app/career_advice.html', {
                'resume': resume,
                'advice': advice
            })
        except Exception as e:
            messages.error(request, f'Error generating career advice: {str(e)}')
            return redirect('resume_app:analyze_resume', resume_id=resume.id)


@login_required
def job_match(request, resume_id):
    """View for matching resume with job descriptions"""
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    
    # Check if analysis exists
    try:
        analysis = resume.analysis
    except ResumeAnalysis.DoesNotExist:
        messages.error(request, 'Resume must be analyzed first!')
        return redirect('resume_app:analyze_resume', resume_id=resume.id)
    
    if request.method == 'POST':
        form = JobSearchForm(request.POST)
        if form.is_valid():
            job_title = form.cleaned_data['job_title']
            company = form.cleaned_data['company']
            job_description = form.cleaned_data['job_description']
            
            try:
                # Match job
                matcher = JobMatcher()
                match_results = matcher.match_job(
                    {
                        'full_text': analysis.summary,
                        'skills': analysis.skills
                    },
                    job_title,
                    company,
                    job_description
                )
                
                # Create job match object
                job_match = JobMatch.objects.create(
                    resume=resume,
                    job_title=match_results['job_title'],
                    company=match_results['company'],
                    match_percentage=match_results['match_percentage'],
                    job_description=match_results['job_description'],
                    skills_matched=match_results['skills_matched'],
                    skills_missing=match_results['skills_missing']
                )
                
                messages.success(request, 'Job match analysis completed!')
                # Redirect to job match results page
                return redirect('resume_app:job_match_detail', match_id=job_match.id)
            except Exception as e:
                messages.error(request, f'Error matching job: {str(e)}')
    else:
        form = JobSearchForm()
    
    # Get previous job matches
    previous_matches = JobMatch.objects.filter(resume=resume).order_by('-created_at')
    
    return render(request, 'resume_app/job_match.html', {
        'resume': resume,
        'form': form,
        'previous_matches': previous_matches
    })


@login_required
def job_match_detail(request, match_id):
    """View for displaying detailed information about a specific job match"""
    job_match = get_object_or_404(JobMatch, id=match_id, resume__user=request.user)
    
    # Prepare data for skill gap chart
    matching_skills = job_match.skills_matched.split(',') if job_match.skills_matched else []
    missing_skills = job_match.skills_missing.split(',') if job_match.skills_missing else []
    
    # Create data for chart
    skill_labels = []
    user_skill_values = []
    required_skill_values = []
    
    # Add matching skills
    for skill in matching_skills:
        if skill.strip():
            skill_labels.append(skill.strip())
            user_skill_values.append(100)  # User has this skill
            required_skill_values.append(100)  # Job requires this skill
    
    # Add missing skills
    for skill in missing_skills:
        if skill.strip():
            skill_labels.append(skill.strip())
            user_skill_values.append(0)  # User doesn't have this skill
            required_skill_values.append(100)  # Job requires this skill
    
    # Calculate match percentages for different categories
    job_match.skills_match_percentage = round(len(matching_skills) / (len(matching_skills) + len(missing_skills)) * 100) if matching_skills or missing_skills else 0
    job_match.experience_match_percentage = round(job_match.match_percentage * 0.9)  # Example calculation
    job_match.education_match_percentage = round(job_match.match_percentage * 1.1)  # Example calculation
    
    # Generate recommendations based on match percentage
    recommendations = []
    if job_match.match_percentage < 80:
        recommendations.append("Focus on developing the missing skills listed above.")
    if job_match.match_percentage < 70:
        recommendations.append("Consider tailoring your resume to highlight relevant experience for this role.")
    if job_match.match_percentage < 60:
        recommendations.append("Look for training or certification opportunities in the required skill areas.")
    if job_match.match_percentage < 50:
        recommendations.append("This role may require significant upskilling. Consider intermediate positions as stepping stones.")
    
    job_match.recommendations = recommendations
    
    # Convert data to JSON for chart.js
    import json
    skill_labels_json = json.dumps(skill_labels)
    user_skill_values_json = json.dumps(user_skill_values)
    required_skill_values_json = json.dumps(required_skill_values)
    
    return render(request, 'resume_app/job_match_detail.html', {
        'job_match': job_match,
        'skill_labels': skill_labels_json,
        'user_skill_values': user_skill_values_json,
        'required_skill_values': required_skill_values_json
    })


@login_required
def dashboard(request):
    """Dashboard view showing user's resumes and analyses"""
    # Get user's resumes
    resumes = Resume.objects.filter(user=request.user).order_by('-uploaded_at')
    
    # Count analyzed resumes
    analyzed_resumes_count = Resume.objects.filter(user=request.user, analysis__isnull=False).count()
    
    return render(request, 'resume_app/dashboard.html', {
        'resumes': resumes,
        'analyzed_resumes_count': analyzed_resumes_count
    })
