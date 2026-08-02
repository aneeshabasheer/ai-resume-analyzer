from .nlp_parser import extract_skills_with_spacy
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Avg

from .models import UserProfile, Resume, ResumeAnalysis, ChatHistory
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, ResumeUploadForm
from .resume_parser import parse_resume_file
from .utils import  generate_suggestions, get_default_comparison_scores, calculate_match
from .chatbot import get_chatbot_response

# ==========================================
# 1. LANDING AND AUTHENTICATION VIEWS
# ==========================================

def home(request):
    """
    Renders the modern home page landing view.
    Redirects to dashboard if already logged in.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def register_view(request):
    """
    Handles user registration using Django's UserRegisterForm.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username}! You can now login.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please check the errors below.")
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


# def login_view(request):
#     """
#     Handles user login using standard Django AuthenticationForm.
#     """
#     if request.user.is_authenticated:
#         return redirect('dashboard')
        
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 messages.success(request, f"Welcome back, {username}!")
#                 return redirect('dashboard')
#         else:
#             messages.error(request, "Invalid username or password.")
#     else:
#         form = AuthenticationForm()
#     return render(request, 'login.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            username = form.cleaned_data.get('username')
            messages.success(request, f"Welcome back, {username}!")
            return redirect('dashboard')
        else:
            print("Login Form Errors:", form.errors)
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login.html', {'form': form})



def logout_view(request):
    """
    Logs out the user and redirects to home.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


# ==========================================
# 2. MAIN DASHBOARD & RESUME UPLOAD
# ==========================================

from django.db.models import Avg

@login_required
def dashboard_view(request):
    user = request.user
    
    total_uploaded = Resume.objects.filter(user=user).count()
    
    user_analyses = ResumeAnalysis.objects.filter(resume__user=user)
    
    jobs_matched = user_analyses.filter(score__gte=50).count()
    
    total_analyses_count = user_analyses.count()
    
    avg_score_query = user_analyses.aggregate(Avg('score'))
    average_score = int(avg_score_query['score__avg']) if avg_score_query['score__avg'] is not None else 0
    
    context = {
        'total_uploaded': total_uploaded,
        'jobs_matched': jobs_matched,
        'average_score': average_score,
        'reports_generated': total_analyses_count, 
        'recent_analyses': user_analyses.order_by('-created_at')[:5],
        'active_menu': 'dashboard'
    }
    return render(request, 'dashboard.html', context)


@login_required
def upload_view(request):
    user_resumes = Resume.objects.filter(user=request.user).order_by('-id') 

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES)
        
        # 1. Manual File Validation (PDF & Size check)
        uploaded_file = request.FILES.get('file') 
        if uploaded_file:
            if not uploaded_file.name.lower().endswith(('.pdf', '.docx', '.doc')):
                messages.error(request, "Only PDF or DOCX files are allowed!")
                return render(request, 'upload.html', {'form': form, 'user_resumes': user_resumes, 'active_menu': 'upload'})
            
            if uploaded_file.size > 5 * 1024 * 1024:
                messages.error(request, "File size exceeds 5MB limit!")
                return render(request, 'upload.html', {'form': form, 'user_resumes': user_resumes, 'active_menu': 'upload'})

        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save() 

            try:
                file_path = resume.file.path
                parsed_data = parse_resume_file(file_path)
                
                resume.raw_text = parsed_data.get('text', '')
                resume.save()
                
                messages.success(request, "Resume uploaded and parsed successfully! Now match it with a Job Description.")
                return redirect('jobs')  

            except Exception as e:
                print("Parsing Error:", e)
                messages.success(request, "Resume uploaded! Now match it with a Job Description.")
                return redirect('jobs')

        else:
            messages.error(request, "Error uploading resume. Check file format (PDF/DOCX) and size (<5MB).")
    else:
        form = ResumeUploadForm()
        
    return render(request, 'upload.html', {
        'form': form, 
        'user_resumes': user_resumes, 
        'active_menu': 'upload'
    })
# ==========================================
# 3. RESULT VIEW & PDF REPORT DOWNLOAD
# ==========================================


def calculate_dynamic_role_scores(user_skills):
    if isinstance(user_skills, str):
        user_skills_list = [s.strip().lower() for s in user_skills.split(',')]
    elif isinstance(user_skills, list):
        user_skills_list = [str(s).strip().lower() for s in user_skills]
    else:
        user_skills_list = []

    job_requirements = {
        'Python Developer': ['python', 'django', 'flask', 'sql', 'rest api', 'git', 'html', 'css'],
        'Backend Developer': ['python', 'java', 'node', 'sql', 'postgresql', 'mongodb', 'rest api', 'docker'],
        'Data Analyst': ['python', 'sql', 'excel', 'pandas', 'numpy', 'power bi', 'tableau', 'statistics'],
        'Machine Learning Engineer': ['python', 'machine learning', 'deep learning', 'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn']
    }

    dynamic_scores = {}

    for role, req_skills in job_requirements.items():
        if not user_skills_list:
            dynamic_scores[role] = 0
            continue

        matched = [skill for skill in req_skills if any(u_skill in skill or skill in u_skill for u_skill in user_skills_list)]
        
        # Percentage calculation: (Matched skills / Total required) * 100
        score = int((len(matched) / len(req_skills)) * 100)
        
        dynamic_scores[role] = max(score, 15) if len(matched) > 0 else 10

    return dynamic_scores


@login_required
def result_view(request, analysis_id):
    """
    Renders detailed results of a specific resume analysis.
    Passes comparative dynamic chart data to Chart.js in the template.
    """
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id, resume__user=request.user)
    
    comparison_scores = calculate_dynamic_role_scores(analysis.extracted_skills)
    
    current_job_title = analysis.job.title if hasattr(analysis, 'job') and analysis.job else "Python Developer"
    if current_job_title in comparison_scores:
        comparison_scores[current_job_title] = analysis.score

    other_analyses = ResumeAnalysis.objects.filter(resume=analysis.resume).exclude(id=analysis.id).order_by('-score')
    
    context = {
        'analysis': analysis,
        'other_analyses': other_analyses,
        'chart_labels': json.dumps(list(comparison_scores.keys())),
        'chart_data': json.dumps(list(comparison_scores.values())),
        'active_menu': 'jobs'
    }
    return render(request, 'result.html', context)


@login_required
def download_report_view(request, analysis_id):
    """
    Generates a clean text file report summarizing the resume analysis.
    Works natively on all setups without ReportLab dependency errors.
    """
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id, resume__user=request.user)
    
    # Safely get job title or description if present
    job_role = getattr(analysis, 'job_title', None) or "Job Description Matching"
    
    # Format the report text
    report_lines = [
        "============================================================",
        "              AI RESUME ANALYZER - REPORT CARD              ",
        "============================================================",
        f"Generated On       : {analysis.created_at.strftime('%Y-%m-%d %H:%M')}",
        f"Candidate Name     : {getattr(analysis, 'parsed_name', None) or analysis.resume.user.username}",
        f"Candidate Email    : {getattr(analysis, 'parsed_email', None) or analysis.resume.user.email}",
        f"Candidate Phone    : {getattr(analysis, 'parsed_phone', None) or 'N/A'}",
        "------------------------------------------------------------",
        f"Target Job Role    : {job_role}",
        f"Match Score        : {analysis.score}%",
        "============================================================",
        "",
        "EXTRACTED SKILLS FROM RESUME:",
        ", ".join(analysis.extracted_skills) if getattr(analysis, 'extracted_skills', None) else "None found",
        "",
        "MATCHED SKILLS WITH JOB REQUIREMENT:",
        ", ".join(analysis.matched_skills) if getattr(analysis, 'matched_skills', None) else "None",
        "",
        "MISSING SKILLS (TO ACQUIRE):",
        ", ".join(analysis.missing_skills) if getattr(analysis, 'missing_skills', None) else "None! Excellent coverage.",
        "",
        "------------------------------------------------------------",
        "RECOMMENDATIONS & SUGGESTIONS:",
        getattr(analysis, 'suggestions', None) or "No additional suggestions.",
        "",
        "============================================================",
        "               Thank you for using AI Resume Analyzer       ",
        "============================================================"
    ]
    
    report_text = "\n".join(report_lines)
    
    response = HttpResponse(report_text, content_type='text/plain')
    filename = f"Resume_Analysis_{analysis.resume.user.username}_{analysis.id}.txt"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



# ==========================================
# 4. HISTORY, CHATBOT, AND PROFILE VIEWS
# ==========================================

@login_required
def history_view(request):
    """
    Displays a historical table of all resume analyses made by the user.
    """
    # Fetch analyses and group/order by date
    analyses = ResumeAnalysis.objects.filter(resume__user=request.user).order_by('-created_at')
    
    return render(request, 'history.html', {
        'analyses': analyses,
        'active_menu': 'history'
    })


# =============================================================================
# Delete Analysis history
# =============================================================================

@login_required
def delete_analysis_view(request, analysis_id):
    analysis = get_object_or_404(ResumeAnalysis, id=analysis_id, resume__user=request.user)
    analysis.delete()
    
    messages.success(request, "Analysis record deleted successfully!")
    return redirect('history') 


# =============================================================================
# 2. Delete Resume (Resume delete from upload page)
# =============================================================================

@login_required
def delete_resume_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    resume.delete()  
    
    messages.success(request, "Resume deleted successfully!")
    return redirect('upload_resume')


# ==============================================================
# Chatbot view
# ==============================================================

@login_required
def chatbot_view(request):
    """
    Renders chatbot window and handles AJAX request to exchange messages.
    """
    if request.method == 'POST':
        # AJAX query
        user_message = request.POST.get('message', '').strip()
        if user_message:
            # Generate rule-based response
            bot_response = get_chatbot_response(user_message)
            
            # Save to Database ChatHistory
            ChatHistory.objects.create(
                user=request.user,
                message=user_message,
                response=bot_response
            )
            return JsonResponse({'response': bot_response})
        return JsonResponse({'error': 'Empty message'}, status=400)
        
    # Get previous chat history for current user
    chats = ChatHistory.objects.filter(user=request.user).order_by('timestamp')
    
    return render(request, 'chatbot.html', {
        'chats': chats,
        'active_menu': 'chatbot'
    })


# ============================================
# Profile View
# ============================================

from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages

@login_required
def profile_view(request):
    """
    Displays and edits user profile details.
    """
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)
        
    total_uploaded = Resume.objects.filter(user=user).count()
    
    
    avg_score_query = ResumeAnalysis.objects.filter(resume__user=user).aggregate(Avg('score'))
    avg_score = int(avg_score_query['score__avg']) if avg_score_query['score__avg'] is not None else 0
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'total_uploaded': total_uploaded,  # In HTML {{ total_uploaded }}
        'avg_score': avg_score,            # In HTML {{ avg_score }}%
        'active_menu': 'profile'
    }
    return render(request, 'profile.html', context)

# ============================================================
# Delete user profile account
# ============================================================

from django.contrib.auth import logout

@login_required
def delete_account_view(request):
    """
    Allows a logged-in user to permanently delete their account and associated data.
    """
    if request.method == 'POST':
        user = request.user
        ResumeAnalysis.objects.filter(resume__user=user).delete()
        Resume.objects.filter(user=user).delete()
        user.delete()
        logout(request)
        
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('login')  

    return redirect('profile')



# ==========================================
# 5.  clear_chat_history
# ==========================================


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ChatHistory

def clear_chat_history(request):

    if request.method == 'POST' and request.user.is_authenticated:
        try:  
            ChatHistory.objects.filter(user=request.user).delete()
            if 'chat_history' in request.session:
                del request.session['chat_history']
                
            return JsonResponse({'status': 'success', 'message': 'Chat history cleared!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'invalid request'}, status=400)




# ============================================================
# 6. To check the matches of entered job escription and resume
# ============================================================


import re
from pypdf import PdfReader
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Resume, ResumeAnalysis

import spacy
from spacy.matcher import PhraseMatcher

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    import spacy.cli
    spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

SKILL_DATABASE = [
    "Python", "Django", "Flask", "React", "Node.js", "JavaScript", "JS",
    "HTML", "HTML5", "CSS", "CSS3", "PostgreSQL", "MySQL", "SQL", "MongoDB", "AWS", 
    "Docker", "Git", "GitHub", "REST API", "Communication", "Problem Solving", "Teamwork",
    "C", "C++", "Java", "OOPs", "B.Tech", "M.Tech", "BCA", "MCA"
]

def extract_skills_spacy(text):
    if not text or len(str(text).strip()) == 0:
        return []
        
    text_str = str(text).lower()
    extracted_skills = set()
    
    # 1. Simple Flexible Search (Primary & Bulletproof)
    for skill in SKILL_DATABASE:
        skill_lower = skill.lower()
        # Word boundary pattern that catches special characters (C++, Node.js, etc.)
        pattern = r'(?:^|[^\w])' + re.escape(skill_lower) + r'(?:[^\w]|$)'
        if re.search(pattern, text_str):
            extracted_skills.add(skill)

    # 2. SpaCy PhraseMatcher (Secondary)
    try:
        doc = nlp(str(text))
        matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
        patterns = [nlp.make_doc(skill) for skill in SKILL_DATABASE]
        matcher.add("SKILL_PATTERN", patterns)
        
        matches = matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            matched_text = span.text.strip().lower()
            for skill in SKILL_DATABASE:
                if skill.lower() == matched_text:
                    extracted_skills.add(skill)
    except Exception as e:
        print("SpaCy Matcher Log Error:", e)

    return list(extracted_skills)


@login_required
def analyze_jd_view(request):
    user_resumes = Resume.objects.filter(user=request.user).order_by('-id')

    if request.method == 'POST':
        job_title = request.POST.get('job_title', '')
        job_description = request.POST.get('job_description', '')
        selected_resume_id = request.POST.get('selected_resume')

        user_resume = None
        if selected_resume_id:
            user_resume = Resume.objects.filter(id=selected_resume_id, user=request.user).first()
        else:
            user_resume = user_resumes.first() 

        if job_description and user_resume:
            resume_text = ""
            
            # 1. Ultra-Robust PDF Extraction Logic
            if user_resume.file:
                try:
                    # Method A: Direct File Read
                    user_resume.file.open('rb')
                    reader = PdfReader(user_resume.file)
                    extracted_pages = []
                    for page in reader.pages:
                        txt = page.extract_text()
                        if txt:
                            extracted_pages.append(txt)
                    resume_text = " ".join(extracted_pages)
                    user_resume.file.close()
                except Exception as e:
                    print("PDF Method A Failed:", e)
                    
                if not resume_text and hasattr(user_resume.file, 'path'):
                    try:
                        # Method B: Path Based Read
                        reader = PdfReader(user_resume.file.path)
                        resume_text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
                    except Exception as e:
                        print("PDF Method B Failed:", e)

            # Fallback to Database Raw Text if PDF extraction failed
            if not resume_text.strip() and user_resume.raw_text:
                resume_text = str(user_resume.raw_text)

            # --- DEBUG LOGS ---
            print("\n==========================================")
            print(f"SELECTED RESUME ID: {user_resume.id}")
            print(f"EXTRACTED TEXT LENGTH: {len(resume_text)}")
            print(f"TEXT PREVIEW: {resume_text[:200]}")
            print("==========================================\n")

            # 2. Extract Skills
            extracted_skills = extract_skills_spacy(resume_text)
            jd_keywords_found = extract_skills_spacy(job_description)

            # Debug extracted skills
            print(f"RESUME SKILLS EXTRACTED: {extracted_skills}")
            print(f"JD SKILLS EXTRACTED: {jd_keywords_found}")

            # 3. Case-Insensitive Skill Categorization Logic
            resume_skills_lower = [str(s).lower().strip() for s in extracted_skills]

            matched_keywords = []
            missing_keywords = []

            for jd_skill in jd_keywords_found:
                clean_skill = str(jd_skill).strip()
                if clean_skill.lower() in resume_skills_lower:
                    matched_keywords.append(clean_skill)
                else:
                    missing_keywords.append(clean_skill)

            # Deduplicate & Format
            formatted_extracted = list(set([str(s).strip() for s in extracted_skills]))
            formatted_matched = list(set(matched_keywords))
            formatted_missing = list(set(missing_keywords))

            # 4. Dynamic Score Calculation
            total_found = len(set([str(s).lower().strip() for s in jd_keywords_found]))
            total_matched = len(formatted_matched)

            if total_found > 0:
                calc_percentage = (total_matched / total_found) * 100
                raw_score = int(calc_percentage)
                match_score = max(15, min(raw_score, 95))
            else:
                match_score = 40

            # 5. Save Analysis to Database
            analysis = ResumeAnalysis.objects.create(
                resume=user_resume,
                job_title=job_title,
                job_description=job_description,
                score=match_score,
                extracted_skills=formatted_extracted,
                matched_skills=formatted_matched,     
                missing_skills=formatted_missing      
            )

            context = {
                'analyzed': True,
                'user_resumes': user_resumes,
                'job_title': job_title,
                'job_description': job_description,
                'selected_resume_id': user_resume.id,
                'match_score': match_score,
                'extracted_keywords': formatted_extracted,
                'matched_keywords': formatted_matched,
                'missing_keywords': formatted_missing,
                'analysis': analysis
            }
            return render(request, 'analyze_jd.html', context)

    context = {
        'analyzed': False,
        'user_resumes': user_resumes
    }
    return render(request, 'analyze_jd.html', context)