from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Resume, JobMatch


class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Resume Title'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file extension
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'docx', 'doc', 'txt']:
                raise forms.ValidationError("Only PDF, DOCX, DOC, and TXT files are allowed.")
            # Check file size (5MB limit)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be under 5MB.")
        return file


class JobSearchForm(forms.Form):
    job_title = forms.CharField(max_length=255, required=True, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job Title'}))
    company = forms.CharField(max_length=255, required=False,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company (Optional)'}))
    job_description = forms.CharField(required=True,
                                     widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Paste job description here', 'rows': 5}))


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True,
                           widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        # Add Bootstrap classes to the default fields
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email