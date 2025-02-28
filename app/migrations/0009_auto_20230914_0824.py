# Generated by Django 3.2.7 on 2023-09-14 08:24

import app.models
import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20230914_0242'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historytemplate',
            name='file_template',
            field=models.FileField(null=True, upload_to=app.models.user_directory_path),
        ),
        migrations.AlterField(
            model_name='membermodel',
            name='date_of_birth',
            field=models.DateField(blank=True, default=datetime.datetime(2023, 9, 14, 8, 24, 33, 253479), null=True),
        ),
        migrations.AlterField(
            model_name='membermodel',
            name='date_of_issue',
            field=models.DateField(blank=True, default=datetime.datetime(2023, 9, 14, 8, 24, 33, 253440), null=True),
        ),
    ]
