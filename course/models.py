from django.db import models



class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title

    def get_price(self, status):
        if status == 0:
            return self.price
        discount = (status/100) * self.price
        return self.price - discount


class Content(models.Model):
    course = models.ForeignKey(Course, related_name='contents', on_delete=models.CASCADE)  # Связь с курсом
    title = models.CharField(max_length=255)  # Заголовок контента
    content_file = models.FileField(upload_to='course_contents/', blank=True,
                                    null=True)  # Файл контента (например, видео или документ)
    description = models.TextField(blank=True, null=True)  # Описание контента
    order = models.PositiveIntegerField(default=0)  # Порядок отображения контента

    class Meta:
        ordering = ['order']  # Сортировка по порядку отображения

    def __str__(self):
        return f"{self.title}"



