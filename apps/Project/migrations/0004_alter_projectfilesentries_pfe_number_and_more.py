# Generated by Django 4.2.13 on 2024-07-08 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Project', '0003_alter_base_articles_alter_base_books_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectfilesentries',
            name='pfe_number',
            field=models.CharField(default=0, max_length=20),
        ),
        migrations.AlterField(
            model_name='projectfilesentries',
            name='pfe_pages',
            field=models.CharField(default=0, max_length=20),
        ),
        migrations.AlterField(
            model_name='projectfilesentries',
            name='pfe_volume',
            field=models.CharField(default=0, max_length=10),
        ),
        migrations.AlterField(
            model_name='projectfilesentries',
            name='pfe_year',
            field=models.CharField(default=0, max_length=4),
        ),
    ]
