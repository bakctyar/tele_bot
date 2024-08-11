from django.contrib import admin

from .models import Course

@admin.register(Course)
class AdminCourse(admin.ModelAdmin):
    list_display = ['title', 'description', 'price', 'created_at', 'updated_at', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title']


