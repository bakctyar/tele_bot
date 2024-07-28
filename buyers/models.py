from django.db import models
from django.contrib.auth.models import AbstractUser


class SignedPeople(AbstractUser):

    # это поле было добавленно, что бы устанавливать статус лиц приобритивших подписку
    status = models.CharField()
