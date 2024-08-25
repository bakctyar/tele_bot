from django.contrib import admin
from .models import SubscriptionOptions

@admin.register(SubscriptionOptions)
class AdminSubscriptionOptions(admin.ModelAdmin):
    list_display = ['title','slug', 'description', 'price', 'discount']
    prepopulated_fields = {'slug': ('title',)}

