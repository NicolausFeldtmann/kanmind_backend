from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'get_user')
    def get_user(self, obj):
        return obj.user
    get_user.short_description = 'User'