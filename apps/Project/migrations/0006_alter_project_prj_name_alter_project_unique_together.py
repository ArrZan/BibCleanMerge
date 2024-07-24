# Generated by Django 4.2.13 on 2024-07-23 13:29

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Project', '0005_alter_projectfilesentries_pfe_authors_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='prj_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='project',
            unique_together={('id_usuario', 'prj_name')},
        ),
    ]
