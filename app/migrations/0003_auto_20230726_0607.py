# Generated by Django 3.2.7 on 2023-07-26 06:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20230320_0704'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accrualscalculationmodel',
            options={'verbose_name': 'Калькуляция начислений', 'verbose_name_plural': 'Калькуляций начислений'},
        ),
        migrations.AlterModelOptions(
            name='courtmoscow',
            options={'verbose_name': 'Судебный участок (центр)', 'verbose_name_plural': 'Судебные участки (центр)'},
        ),
        migrations.AlterModelOptions(
            name='courtmoscowregion',
            options={'verbose_name': 'Судебный участок (область)', 'verbose_name_plural': 'Судебные участки (область)'},
        ),
        migrations.AlterModelOptions(
            name='historytemplate',
            options={'verbose_name': 'История создания шаблонов', 'verbose_name_plural': 'История создания шаблонов'},
        ),
        migrations.AlterModelOptions(
            name='keyrate',
            options={'verbose_name': 'Ключевая ставка', 'verbose_name_plural': 'Ключевая ставка'},
        ),
        migrations.AlterModelOptions(
            name='membermodel',
            options={'verbose_name': 'Член товарищества', 'verbose_name_plural': 'Члены товарищества'},
        ),
        migrations.AlterModelOptions(
            name='membersfeemodel',
            options={'verbose_name': 'Членский взнос', 'verbose_name_plural': 'Членские взносы'},
        ),
        migrations.AlterModelOptions(
            name='penaltycalculationmodel',
            options={'verbose_name': 'Калькуляция пени', 'verbose_name_plural': 'Калькуляций пени'},
        ),
        migrations.AlterModelOptions(
            name='protocolmodel',
            options={'verbose_name': 'Протокол собрания', 'verbose_name_plural': 'Протоколы собрания'},
        ),
        migrations.AddField(
            model_name='membermodel',
            name='date_of_birth',
            field=models.DateField(default=datetime.datetime(2023, 7, 26, 6, 7, 24, 2580)),
        ),
        migrations.AddField(
            model_name='membermodel',
            name='date_of_issue',
            field=models.DateField(default=datetime.datetime(2023, 7, 26, 6, 7, 24, 2520)),
        ),
        migrations.AddField(
            model_name='membermodel',
            name='divison_code',
            field=models.CharField(default='000-000', max_length=7),
        ),
        migrations.AddField(
            model_name='membermodel',
            name='issued',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AddField(
            model_name='membermodel',
            name='place_of_birth',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='membermodel',
            name='series_number_doc',
            field=models.CharField(default='00 00 № 000000', max_length=15),
        ),
    ]
