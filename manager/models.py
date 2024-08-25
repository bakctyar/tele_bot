from django.db import models



class DissatisfiedUser(models.Model) :
    user_telegram_id = models.CharField()
    user_name = models.CharField()
    question_user = models.TextField()
    create_up = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'user_telegram_id: {self.user_telegram_id}  user_name: {self.user_name}'


class TemporaryData(models.Model):
    user_telegram_id = models.CharField()
    file_unique_id = models.CharField(primary_key=True, editable=True)
    user_name = models.CharField()
    email = models.EmailField(blank=True)
    number = models.CharField(blank=True)
    image = models.ImageField(upload_to='images/')
    create_up = models.DateTimeField(auto_now_add=True)