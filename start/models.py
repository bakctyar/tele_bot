from django.db import models



class SubscriptionOptions(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)


    def __str__(self):
        return self.title