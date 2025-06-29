from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DocumentType, AccessLevel, Specialties
from django.utils.html import format_html

# Registrar el modelo CustomUser con UserAdmin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'display_profile_image')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {
            'fields': (
                'first_name', 'last_name', 'email', 'age', 'phone_number', 
                'address1', 'address2', 'country', 'birthdate', 'document_type', 
                'document_number', 'access_level', 'specialties','profile_image'
            )
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Fechas importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 'first_name', 'last_name', 
                'age', 'phone_number', 'address1', 'address2', 'country', 
                'birthdate', 'document_type', 'document_number', 'access_level','specialties', 
                'is_staff', 'is_superuser', 'profile_image'
            ),
        }),
    )

    def display_profile_image(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" width="50" height="50" />', obj.profile_image.url)
        return "No image"
    
    display_profile_image.short_description = 'Imagen de perfil'

# Registrar los modelos en el admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DocumentType)
admin.site.register(AccessLevel)
admin.site.register(Specialties)