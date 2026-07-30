from django.db import models
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, Resume
import os

# 1. USER REGISTRATION FORM
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)



# 2. USER UPDATE FORM
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


# 3. PROFILE UPDATE FORM
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_pic', 'phone_number', 'bio', 'skills', 'education', 'experience']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., Python, Django, HTML, CSS'}),
            'education': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., BCA from ABC University (2024)'}),
            'experience': forms.Textarea(attrs={'rows': 2, 'placeholder': 'e.g., Python Intern at XYZ Corp (6 months)'}),
        }


# 4. RESUME UPLOAD FORM
class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            ext = os.path.splitext(file.name)[1].lower()
            valid_extensions = ['.pdf', '.docx']
            if ext not in valid_extensions:
                raise forms.ValidationError("Unsupported file format! Please upload a PDF (.pdf) or Word Document (.docx).")
            
            # Restrict file size to 5MB (5 * 1024 * 1024 bytes)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size is too large! Maximum file size allowed is 5MB.")
        return file

