from django.contrib import admin
from django.contrib.auth import get_user_model as User
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Person  # Import Person model

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username', 'scout_display_name']

class PersonAdmin(admin.ModelAdmin):
    list_display = ['first_name']  # Adjust fields based on your Person model
    search_fields = ['first_name']  # Fields to search
    ordering = ['-created_at']  # Default ordering

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Person, PersonAdmin)
