# Generated by Django 5.1.7 on 2025-04-11 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('valApp', '0020_alter_guildmembers_address_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guildmembers',
            name='heroLvl',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='guildmembers',
            name='professionMastery',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='guildmembers',
            name='weeklyCrafts',
            field=models.IntegerField(default=0),
        ),
    ]
