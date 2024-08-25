# Generated by Django 5.0.7 on 2024-08-13 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TemporaryData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_telegram_id', models.CharField()),
                ('user_name', models.CharField()),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('number', models.CharField(blank=True)),
                ('image', models.ImageField(upload_to='')),
                ('create_up', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
