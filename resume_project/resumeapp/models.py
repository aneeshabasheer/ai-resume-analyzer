from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. USER PROFILE MODEL
# Extends standard Django User model to store extra profile details.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_pic = models.ImageField(upload_to='profiles/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    skills = models.TextField(null=True,blank=True,help_text="Enter your skills comma-separated")
    education = models.TextField(null=True, blank=True)
    experience = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signals to automatically create UserProfile when User is registered
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Ensure profile exists before saving, just in case
    if not hasattr(instance, 'profile'):
        UserProfile.objects.create(user=instance)
    instance.profile.save()


# 2. RESUME MODEL
# Stores uploaded resume metadata and extracted raw text.
class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=200, default="My Resume")
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    raw_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.file.name.split('/')[-1]}"


# 3. JOB DESCRIPTION MODEL
# Stores job descriptions added by admins to match resumes against.
# class JobDescription(models.Model):
#     title = models.CharField(max_length=100)
#     company = models.CharField(max_length=100)
#     description = models.TextField()
#     required_skills = models.TextField(help_text="Enter skills comma-separated")
#     experience_required = models.IntegerField(help_text="Required experience in years")
#     location = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.title} at {self.company}"


# 4. RESUME ANALYSIS MODEL
# Stores the parsed resume text analysis, matching score, and suggestions.
class ResumeAnalysis(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='analyses')
    
    
    job_title = models.CharField(max_length=200, blank=True, null=True)
    job_description = models.TextField(blank=True, null=True)
    
    score = models.IntegerField(default=0)
    parsed_name = models.CharField(max_length=100, blank=True, null=True)
    parsed_email = models.CharField(max_length=100, blank=True, null=True)
    parsed_phone = models.CharField(max_length=20, blank=True, null=True)
    
    # Store lists as JSON
    extracted_skills = models.JSONField(default=list, blank=True)
    matched_skills = models.JSONField(default=list, blank=True)
    missing_skills = models.JSONField(default=list, blank=True)
    
    suggestions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        title = self.job_title if self.job_title else "Generic Job"
        return f"Analysis: {self.resume.user.username} for {title} ({self.score}%)"


# 5. CHAT HISTORY MODEL
# Stores user dialogues with the rule-based career guidance chatbot.
class ChatHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats')
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat: {self.user.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
