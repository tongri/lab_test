# Generated by Django 3.1.6 on 2021-04-15 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0010_auto_20210415_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='file_field',
            field=models.ImageField(upload_to='static/img/'),
        ),
    ]
