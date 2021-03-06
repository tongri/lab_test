# Generated by Django 3.1.6 on 2021-04-13 13:25

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0003_auto_20210412_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogger',
            name='birthday',
            field=models.DateField(default=datetime.date(2021, 4, 13)),
        ),
        migrations.AlterField(
            model_name='blogger',
            name='user',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='reader',
            name='is_eighteen',
            field=models.BooleanField(blank=True, default=False),
        ),
        migrations.AlterField(
            model_name='reader',
            name='user',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='images/')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='boards.topic')),
            ],
        ),
    ]
