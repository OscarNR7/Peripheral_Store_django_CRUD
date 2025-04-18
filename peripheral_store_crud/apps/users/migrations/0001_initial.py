# Generated by Django 5.2 on 2025-04-18 03:08

import apps.users.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('first_name', models.CharField(max_length=150, verbose_name='First Name')),
                ('last_name', models.CharField(max_length=150, verbose_name='Last Name')),
                ('is_active', models.BooleanField(default=True, verbose_name='Is Active')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='Date Joined')),
                ('last_login', models.DateTimeField(auto_now=True, verbose_name='Last Login')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Is Verified')),
                ('phone_number', models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone Number')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'ordering': ['-date_joined'],
            },
            managers=[
                ('objects', apps.users.models.CustomUserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, null=True, verbose_name='Biography')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='users/avatars/', verbose_name='Avatar')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='Date of Birth')),
                ('gender', models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other'), ('N', 'Prefer not to say')], max_length=1, null=True, verbose_name='Gender')),
                ('newsletter_subscription', models.BooleanField(default=False, verbose_name='Newsletter Subscription')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'User profiles',
            },
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_type', models.CharField(choices=[('billing', 'Billing Address'), ('shipping', 'Shipping Address')], max_length=50, verbose_name='Address Type')),
                ('is_default', models.BooleanField(default=False, verbose_name='Is Default')),
                ('name', models.CharField(max_length=300, verbose_name='Full name')),
                ('street_address1', models.CharField(max_length=300, verbose_name='Street Address 1')),
                ('street_address2', models.CharField(blank=True, max_length=300, null=True, verbose_name='Street Address 2')),
                ('city', models.CharField(max_length=100, verbose_name='City')),
                ('state_province', models.CharField(max_length=100, verbose_name='State/Province')),
                ('postal_code', models.CharField(max_length=20, verbose_name='Postal Code')),
                ('country', models.CharField(max_length=100, verbose_name='Country')),
                ('phone', models.CharField(max_length=20, verbose_name='Phone Number')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Address',
                'verbose_name_plural': 'Addresses',
                'ordering': ['-created_at'],
                'unique_together': {('user', 'address_type', 'is_default')},
            },
        ),
    ]
