# Generated by Django 5.1.7 on 2025-04-04 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('valApp', '0011_alter_objects_description_alter_objects_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='objects',
            name='nftImage',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
