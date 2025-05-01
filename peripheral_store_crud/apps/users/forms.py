from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import User, Profile, Address

# SignUp Form
class CustomUserCreationForm(UserCreationForm):
    '''Form para el regsitro de suuarios'''
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
    '''Form para logearse'''
    username = forms.EmailField(
        label='Email', 
        widget=forms.EmailInput({'placeholder': 'Email address', 'class': 'w-full px-3 py-2 border rounded-md'}),
        error_messages={'required': 'Please enter your email address.'}
    )
    password = forms.CharField(
        label='Password', 
        widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'w-full px-3 py-2 border rounded-md'}),
        error_messages={'required': 'Please enter your password.'}
    )
    
    error_messages = {
        'invalid_login': 'The email or password you entered is incorrect. Please try again.',
        'inactive': 'This account is inactive. Please contact support for assistance.',
    }

class CustomUserChangeForm(UserChangeForm):
    '''Form para editar la informacion de suaurios'''
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
    '''form para editar el perfil del suaurio'''
    class Meta:
        model = Profile
        fields = ("bio", "avatar", "date_of_birth", "gender", "newsletter_subscription")
        widgets = {
            "bio": forms.Textarea(attrs={'placeholder': 'Tell us about yourself...'}),
            "date_of_birth": forms.DateInput(attrs={'type': 'date'}),
        }
class AddressForm(forms.ModelForm):
    '''form para gestionar las direcciones'''
    class Meta:
        model = Address
        exclude = ('user', 'created_at', 'updated_at')
        widgets = {
            "name": forms.TextInput(attrs={'placeholder': 'Full name'}),
            "street_address1": forms.TextInput(attrs={'placeholder': 'Street Address 1'}),
            "street_address2": forms.TextInput(attrs={'placeholder': 'Street Address 2 (optional)'}),
            "city": forms.TextInput(attrs={'placeholder': 'City'}),
            "state_province": forms.TextInput(attrs={'placeholder': 'State/Province'}),
            "postal_code": forms.TextInput(attrs={'placeholder': 'Postal code'}),
            "country": forms.TextInput(attrs={'placeholder': 'Country'}),
            "phone": forms.TextInput(attrs={'placeholder': 'Phone number'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance