from django.contrib import admin
from .models import UserProfile, Resume, ResumeAnalysis, ChatHistory

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'skills', 'education')
    search_fields = ('user__username', 'user__email', 'phone_number', 'skills')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'file', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('user__username', 'file')

# @admin.register(JobDescription)
# class JobDescriptionAdmin(admin.ModelAdmin):
#     list_display = ('title', 'company', 'experience_required', 'location', 'created_at')
#     list_filter = ('location', 'experience_required')
#     search_fields = ('title', 'company', 'required_skills')

@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('resume', 'job_title', 'score', 'parsed_name', 'parsed_email', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('parsed_name', 'parsed_email', 'resume__user__username')

@admin.register(ChatHistory)
class ChatHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_excerpt', 'response_excerpt', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'message', 'response')
    
    def message_excerpt(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_excerpt.short_description = 'User Message'
    
    def response_excerpt(self, obj):
        # Strip HTML tags for clean admin display
        clean_text = obj.response.replace('<br>', ' ').replace('<b>', '').replace('</b>', '').replace('<ul>', '').replace('</ul>', '').replace('<li>', '').replace('</li>', '')
        return clean_text[:50] + '...' if len(clean_text) > 50 else clean_text
    response_excerpt.short_description = 'Bot Response'
