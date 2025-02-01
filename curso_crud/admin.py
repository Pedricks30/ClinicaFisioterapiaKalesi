from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, DocumentType, AccessLevel

# Registrar el modelo CustomUser con UserAdmin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'email', 'age', 'phone', 'telephone_prefix', 'address1', 'address2', 'country', 'birthdate', 'document_type','document_number', 'access_level')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'age', 'phone', 'telephone_prefix', 'address1', 'address2', 'country', 'birthdate','document_type','document_number', 'access_level', 'is_staff', 'is_superuser'),
        }),
    )

# Registrar los modelos en el admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DocumentType)
admin.site.register(AccessLevel)