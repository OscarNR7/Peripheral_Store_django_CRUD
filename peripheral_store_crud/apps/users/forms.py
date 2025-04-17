from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import User, Profile

# SignUp Form
class CustomUserCreationForm(UserCreationForm):
    '''
    Form for user registration
    '''
    class Meta:
        model = User
        fields = ('email','first_name','last_name')
        widgets = {
            "email": forms.EmailInput(attrs={'placeholder': 'Email address'}),
            "first_name": forms.TextInput(attrs={'placeholder': 'First name'}),
            "last_name": forms.TextInput(attrs={'placeholder': 'Last name'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].help_text = None

# Login Form
class CustomUserLoginForm(AuthenticationForm):
    '''
    Form for logging in registered users
    '''
    username = forms.EmailField(label='Email', widget=forms.EmailInput({'placeholder': 'Email address'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class CustomUserChangeForm(UserChangeForm):
    '''
    Form for editing user data
    '''
    password = None  # To hide the password field

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone_number")
        widgets = {
            "email": forms.EmailInput(attrs={'placeholder': 'Email address'}),
            "first_name": forms.TextInput(attrs={'placeholder': 'First name'}),
            "last_name": forms.TextInput(attrs={'placeholder': 'Last name'}),
            "phone_number": forms.TextInput(attrs={'placeholder': 'Phone number'}),
        }

class ProfileForm(forms.ModelForm):
    '''
    Form for editing user profile
    '''
    class Meta:
        model = Profile
        fields = ("bio", "avatar", "date_of_birth", "gender", "newsletter_subscription")
        widgets = {
            "bio": forms.Textarea(attrs={'placeholder': 'Tell us about yourself...'}),
            "date_of_birth": forms.DateInput(attrs={'type': 'date'}),
        }
