# Generated by Django 4.2.13 on 2024-06-25 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='prj_autosave',
            field=models.BooleanField(default=False),
        ),
    ]
