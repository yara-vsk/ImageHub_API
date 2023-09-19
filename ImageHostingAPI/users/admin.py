from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from .models import CustomUser, Tier, Thumbnail


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = CustomUser


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('tier',)}),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Tier)
admin.site.register(Thumbnail)