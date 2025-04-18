from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Profile, Address

# Register your models here.
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'
class AddressInline(admin.TabularInline):
    model = Address
    extra = 0
    fields = ('address_type', 'is_default', 'city', 'country', 'phone')
    readonly_fields = ('created_at', 'updated_at')

# Admins
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user_email', 'address_type_display', 'is_default', 'truncated_address')
    list_filter = ('address_type', 'is_default', 'country')
    search_fields = ('user__email', 'city', 'country')
    readonly_fields = ('created_at', 'updated_at')
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Usuario'
    
    def address_type_display(self, obj):
        return obj.get_address_type_display()
    address_type_display.short_description = 'Tipo'
    
    def truncated_address(self, obj):
        return f"{obj.city}, {obj.country}"
    truncated_address.short_description = 'Dirección'

# User Admin (actualizado)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline, AddressInline)
    list_display = ('email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_verified')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')}
        ),
    )

admin.site.register(User, UserAdmin)