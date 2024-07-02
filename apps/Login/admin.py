from django.contrib import admin

from .models import User

class TableUser(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'last_login', 'date_joined']
    search_fields = ['username']
    list_per_page = 5

admin.site.register(User,TableUser)
