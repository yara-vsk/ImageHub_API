from django.contrib import admin
from .models import CustomUser, Tier, Thumbnail

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Tier)
admin.site.register(Thumbnail)