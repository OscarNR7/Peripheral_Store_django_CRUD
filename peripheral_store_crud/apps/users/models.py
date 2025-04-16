from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.text import slugify
from django.urls import reverse


# Create your models here.
class CustomUserManager(BaseUserManager):
    '''
    Modelo del usuario sin username field
    '''
    use_in_migrations = True

    def _create_user(self, email, password=None, **extra_fields):
        '''
        Metodo para crear un usuario dando el email y password
        '''
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_user(self, email, password=None, **extra_fields):
        '''
        Metodo apra crear un usuario regular
        '''
        extra_fields.setdefault('is_staff',False)
        extra_fields.setdefault('is_superuser',False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password=None, **extra_fields):
        '''
        Metodo para crear un superusuario
        '''
        extra_fields.setdefault('is_staff',True)
        extra_fields.setdefault('is_superuser',True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self._create_user(email,password, **extra_fields)
    
class User(AbstractUser):
    '''
    Modelo de usuario con email como username field
    '''
    username = None
    email = models.EmailField(unique=True, verbose_name='email')
    first_name = models.CharField(max_length=150, verbose_name='First Name')
    last_name = models.CharField(max_length=150, verbose_name='Last Name')
    is_active = models.BooleanField(default=True, verbose_name='Is Active')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Date Joined')
    last_login = models.DateTimeField(auto_now=True, verbose_name='Last Login')
    is_verified = models.BooleanField(default=False, verbose_name='Is Verified')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='Phone Number')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.email
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    def get_absolute_url(self):
        return reverse('users:user_detail', kwargs={'pk': self.pk})

class Profile(models.Model):
    '''
    Modelo para el perfil de los usuarios regsitrados
    '''
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name='User')
    bio = models.TextField(blank=True, null=True, verbose_name='Biography')
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Avatar')
    date_of_birth = models.DateField(blank=True, null=True, verbose_name='Date of Birth')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='Gender')
    newsletter_subscription = models.BooleanField(default=False, verbose_name='Newsletter Subscription')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'User profiles'

    def __str__(self):
        return f'Profile of {self.user.get_full_name()}'