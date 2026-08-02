from django.urls import path
from . import views
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 1. Landing and Auth
    
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # 2. Main Dashboard & Upload

    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('upload/', views.upload_view, name='upload_resume'),
    path('delete-resume/<int:resume_id>/', views.delete_resume_view, name='delete_resume'),
    
    # 3. Resume Analysis Result and PDF report

    path('result/<int:analysis_id>/', views.result_view, name='result'),
    path('result/<int:analysis_id>/download/', views.download_report_view, name='download_report'),
    path('delete-analysis/<int:analysis_id>/', views.delete_analysis_view, name='delete_analysis'),
    
    # 4. Secondary pages: History, Chatbot, Profile

    path('history/', views.history_view, name='history'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('clear-chat/', views.clear_chat_history, name='clear_chat'),
    
    path('profile/', views.profile_view, name='profile'),
    path('delete-account/', views.delete_account_view, name='delete_account'),
    
    # 5. Job CRUD (Job Management)

    path('jobs/', views.analyze_jd_view, name='jobs'),
    path('analyze-jd/', views.analyze_jd_view, name='analyze_jd'),

    # 6. Reset password

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),       
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),       
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
