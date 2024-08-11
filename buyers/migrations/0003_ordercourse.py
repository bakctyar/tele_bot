# Generated by Django 5.0.7 on 2024-08-10 13:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('buyers', '0002_rename_id_user_signedpeople_user_id'),
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_up', models.DateTimeField(auto_now=True)),
                ('create_up', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='course.course')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='buyers.signedpeople')),
            ],
            options={
                'unique_together': {('user', 'course')},
            },
        ),
    ]
