from django.contrib import admin

from .models import DissatisfiedUser, TemporaryData

@admin.register(DissatisfiedUser)
class AdminDissatisfiedUser(admin.ModelAdmin):
    list_display = ('user_telegram_id', 'user_name', 'question_user', 'create_up')


@admin.register(TemporaryData)
class AdminTemporaryData(admin.ModelAdmin):
    list_display = ('file_unique_id', 'user_telegram_id', 'user_name', 'email', 'create_up','number','image')


