from django.db import models



class SignedPeople(models.Model):
    user_id = models.CharField(primary_key=True, editable=False)
    username = models.CharField(blank=True, max_length=120)
    subscription = models.CharField(blank=True)
    status = models.BooleanField(default=False)
    update_up = models.DateTimeField(auto_now=True)
    create_up = models.DateTimeField(auto_now_add=True)
    action_count = models.PositiveIntegerField(default=0)

