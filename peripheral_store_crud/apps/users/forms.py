from  django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from .models import User, Profile

#SignUp Formulario
class CustomUserCreationForm(UserCreationForm):
    '''
    Formulario para el registro de usuarios
    '''
    class Meta:
        model = User
        fields = ('email','first_name','last_name')
        widgets = {
            "email": forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
            "first_name": forms.TextInput(attrs={'placeholder': 'Nombre'}),
            "last_name": forms.TextInput(attrs={'placeholder': 'Apellido'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in self.fields:
            self.fields[field_name].help_text = None

#Login Formulario
class CustomUserLoginForm(AuthenticationForm):
    '''
    Formulario para el login de usuarios ya registrados
    '''
    username = forms.EmailField(label='Email', widget=forms.EmailInput({'placeholder': 'Correo electrónico'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}))

class CustomUserChangeForm(UserChangeForm):
    '''
    Formulario para editar los datos del usuario
    '''
    password = None #Para ocultar la contraseña

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone_number")
        widgets = {
            "email": forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
            "first_name": forms.TextInput(attrs={'placeholder': 'Nombre'}),
            "last_name": forms.TextInput(attrs={'placeholder': 'Apellido'}),
            "phone_number": forms.TextInput(attrs={'placeholder': 'Número de teléfono'}),
        }

class ProfileForm(forms.ModelForm):
    '''
    Formulario para editar el perfil del usuario
    '''
    class Meta:
        model = Profile
        fields = ("bio", "avatar", "date_of_birth", "gender", "newsletter_subscription")
        widgets = {
            "bio": forms.Textarea(attrs={'placeholder': 'Cuéntanos sobre ti...'}),
            "date_of_birth": forms.DateInput(attrs={'type': 'date'}),
        }