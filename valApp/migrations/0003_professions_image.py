# Generated by Django 5.1.7 on 2025-03-28 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('valApp', '0002_objects_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='professions',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='professions/images/'),
        ),
    ]
