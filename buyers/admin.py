from django.contrib import admin

from .models import SignedPeople, OrderCourse

@admin.register(SignedPeople)
class AdminSignedPeople(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'subscription', 'status', 'create_up', 'update_up', 'action_count')
    list_filter = ('status', 'subscription')
    search_fields = ('user_id', 'username')
    ordering = ('create_up',)



@admin.register(OrderCourse)
class OrderCourse(admin.ModelAdmin):
    list_display = ('user', 'course', 'create_up', 'update_up')