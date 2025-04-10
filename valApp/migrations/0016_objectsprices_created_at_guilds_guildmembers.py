# Generated by Django 5.1.7 on 2025-04-10 18:57

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('valApp', '0015_objectsprices'),
    ]

    operations = [
        migrations.AddField(
            model_name='objectsprices',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='Guilds',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=200)),
                ('name', models.CharField(max_length=200)),
                ('avatar', models.CharField(max_length=500)),
                ('tag', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('language', models.CharField(max_length=100)),
                ('members', models.IntegerField()),
                ('announce', models.TextField()),
                ('leader', models.CharField(max_length=200)),
                ('usdc', models.FloatField()),
                ('ranking', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('race', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='valApp.races')),
            ],
        ),
        migrations.CreateModel(
            name='GuildMembers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('kkey', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=500)),
                ('uuidGuild', models.CharField(max_length=500)),
                ('points', models.IntegerField()),
                ('artisan', models.IntegerField()),
                ('alchemist', models.IntegerField()),
                ('architect', models.IntegerField()),
                ('blacksmith', models.IntegerField()),
                ('engineer', models.IntegerField()),
                ('explorer', models.IntegerField()),
                ('jeweler', models.IntegerField()),
                ('miner', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('idGuild', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='valApp.guilds')),
            ],
        ),
    ]
