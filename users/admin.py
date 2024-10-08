from django.contrib import admin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group


class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("username",)}),
        ("Permission",  {"fields": ("is_staff", "is_admin")}),
    )
    add_fieldsets = (
        (None,
         {
             "classes": ["wide"],
             "fields": ("email", "username", "password1", "password2")
         },
         ),
    )
    search_fields = ("email", "username")
    list_display = ("user_id", "email", "username", "is_active", "is_staff", "is_admin")
    ordering = ("username",)

    list_filter = ("is_admin",)
    filter_horizontal = [ ]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.unregister(Group)

