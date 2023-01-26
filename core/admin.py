from django.contrib import admin
from core.models import User


class UserAdmin(admin.ModelAdmin):
    """Custom user admin."""
    ordering = ('id',)


admin.site.register(User, UserAdmin)
