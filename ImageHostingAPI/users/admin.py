from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser, Tier, Thumbnail



class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("tier",)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ("tier",)


class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('tier',)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
            (None, {'fields': ('tier',)}),
    )


admin.site.register(Tier)
admin.site.register(Thumbnail)
admin.site.register(CustomUser, CustomUserAdmin)