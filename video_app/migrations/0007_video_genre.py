# Generated by Django 5.1.6 on 2025-04-05 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_app', '0006_alter_video_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='video',
            name='genre',
            field=models.CharField(choices=[
                ('action', 'Action'), ('comedy', 'Comedy'),
                ('drama', 'Drama'), ('sci-fi', 'Sci-Fi'),
                ('horror', 'Horror'), ('documentary', 'Documentary')
            ], default='action', max_length=30),
        ),
    ]
