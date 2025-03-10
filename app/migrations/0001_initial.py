# Generated by Django 3.2.7 on 2023-03-20 06:53

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=100)),
                ('company_inn', models.CharField(max_length=10)),
                ('company_ogrn', models.CharField(max_length=13)),
                ('full_company_name', models.CharField(max_length=100)),
                ('fio_manager', models.CharField(max_length=100)),
                ('position_manager', models.CharField(max_length=50)),
                ('full_address', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=18)),
                ('email', models.EmailField(max_length=50)),
                ('user_snt', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Компания',
                'verbose_name_plural': 'Компании',
            },
        ),
        migrations.CreateModel(
            name='CourtMoscow',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_court', models.CharField(max_length=36, null=True)),
                ('code', models.CharField(max_length=10, null=True)),
                ('number', models.IntegerField(null=True)),
                ('full_name', models.CharField(max_length=40, null=True)),
                ('polygon_data', django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326)),
                ('short_name', models.CharField(max_length=20, null=True)),
                ('address', models.CharField(max_length=50, null=True)),
                ('phones', models.CharField(max_length=20, null=True)),
                ('phone_info', models.CharField(max_length=20, null=True)),
                ('territorial_info', models.TextField(null=True)),
                ('judge_fio', models.CharField(max_length=40, null=True)),
                ('dinner_time', models.CharField(max_length=50, null=True)),
                ('week_ends', models.CharField(max_length=50, null=True)),
                ('counsulting_hours', models.CharField(max_length=50, null=True)),
                ('business_hours', models.CharField(max_length=50, null=True)),
                ('email', models.CharField(max_length=30, null=True)),
                ('court_latitude', models.FloatField(null=True)),
                ('court_longitude', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CourtMoscowRegion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=40, null=True)),
                ('region_name', models.CharField(max_length=40, null=True)),
                ('code', models.CharField(max_length=10, null=True)),
                ('address', models.CharField(max_length=50, null=True)),
                ('phones', models.CharField(max_length=20, null=True)),
                ('email', models.CharField(max_length=20, null=True)),
                ('url', models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Credits',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateField()),
                ('date_finish', models.DateField(blank=True, null=True)),
                ('summa', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='DebtsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_debt', models.DateField()),
                ('end_debt', models.DateField(blank=True, null=True)),
                ('type_accuals', models.CharField(choices=[('0', 'Автоматические начисления'), ('1', 'На дату окончания задолженности')], default='0', max_length=1)),
                ('type_doc', models.CharField(choices=[('0', 'Членский взнос'), ('1', 'Целевой взнос')], default='0', max_length=1)),
                ('sum', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='KeyRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('rate', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='LandModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=10)),
                ('kadastr_number', models.CharField(max_length=30)),
                ('land_address', models.CharField(max_length=150)),
                ('comment', models.TextField(blank=True, max_length=200)),
                ('attachment', models.FileField(blank=True, upload_to='')),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.companymodel')),
            ],
        ),
        migrations.CreateModel(
            name='MemberModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=40)),
                ('second_name', models.CharField(max_length=40)),
                ('third_name', models.CharField(max_length=40)),
                ('email', models.EmailField(max_length=50)),
                ('phone', models.CharField(blank=True, max_length=18)),
                ('address', models.CharField(max_length=150)),
                ('status', models.CharField(blank=True, choices=[('0', 'Не член товарищества'), ('1', 'Член товарищества')], default='1', max_length=1)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.companymodel')),
            ],
        ),
        migrations.CreateModel(
            name='ScanCompanyModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ustav', models.FileField(blank=True, upload_to='')),
                ('ogrn', models.FileField(blank=True, upload_to='')),
                ('inn', models.FileField(blank=True, upload_to='')),
                ('yegryul', models.FileField(blank=True, upload_to='')),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.companymodel')),
            ],
        ),
        migrations.CreateModel(
            name='ProtocolModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.CharField(max_length=20)),
                ('date_start', models.DateField()),
                ('date_finish', models.DateField()),
                ('renta', models.FloatField()),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.companymodel')),
            ],
        ),
        migrations.CreateModel(
            name='PenaltyModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100)),
                ('date_start', models.DateField(null=True, unique=True)),
                ('attachment', models.FileField(blank=True, upload_to='')),
                ('rate', models.FloatField()),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.companymodel')),
            ],
        ),
        migrations.CreateModel(
            name='PenaltyCalculationModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.CharField(max_length=30)),
                ('date_start', models.DateField()),
                ('date_finish', models.DateField()),
                ('rate', models.FloatField()),
                ('type', models.CharField(max_length=1)),
                ('days', models.IntegerField()),
                ('sum', models.FloatField()),
                ('sum_edit', models.IntegerField()),
                ('debt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.debtsmodel')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentsModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fio', models.CharField(max_length=100)),
                ('date_payment', models.DateField()),
                ('type_payment', models.CharField(choices=[('0', 'Членский взнос'), ('1', 'Целевой взнос')], default='0', max_length=1)),
                ('sum_payment', models.FloatField()),
                ('comment', models.TextField(blank=True, max_length=200)),
                ('land', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.landmodel')),
            ],
        ),
        migrations.CreateModel(
            name='OwnershipModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_hold', models.DateField(blank=True, null=True)),
                ('end_hold', models.DateField(blank=True, null=True)),
                ('comment', models.TextField(blank=True, max_length=200)),
                ('attachment', models.FileField(blank=True, upload_to='')),
                ('land', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.landmodel')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.membermodel')),
            ],
        ),
        migrations.CreateModel(
            name='MembersFeeModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num_doc', models.CharField(max_length=50)),
                ('date_doc', models.DateField()),
                ('date_start', models.DateField(blank=True, null=True)),
                ('date_finish', models.DateField(blank=True, null=True)),
                ('type_fee', models.CharField(choices=[('0', 'Членский взнос'), ('1', 'Целевой взнос')], default='0', max_length=1)),
                ('payment_period', models.CharField(choices=[('1', 'Ежемесячные'), ('2', 'Ежеквартальные'), ('3', 'Ежегодные')], default='1', max_length=1)),
                ('day_accrual', models.CharField(max_length=2)),
                ('amount_fee', models.FloatField()),
                ('obj_fee', models.CharField(max_length=100)),
                ('attachment', models.FileField(blank=True, upload_to='')),
                ('comment', models.TextField(blank=True, max_length=150)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.companymodel')),
            ],
        ),
        migrations.AddField(
            model_name='landmodel',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='lands', through='app.OwnershipModel', to='app.MemberModel'),
        ),
        migrations.CreateModel(
            name='HistoryTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_template', models.DateTimeField(null=True)),
                ('name_template', models.CharField(max_length=100)),
                ('file_template', models.FileField(null=True, upload_to='')),
                ('member_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.membermodel')),
            ],
        ),
        migrations.CreateModel(
            name='HistoryDoc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view_template', models.CharField(max_length=40)),
                ('pretrial', models.FileField(null=True, upload_to='')),
                ('judicial', models.FileField(null=True, upload_to='')),
                ('court_order', models.FileField(null=True, upload_to='')),
                ('credit_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.credits')),
            ],
        ),
        migrations.AddField(
            model_name='debtsmodel',
            name='land',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.landmodel'),
        ),
        migrations.CreateModel(
            name='DebtCharges',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_payment', models.DateField()),
                ('id_member_fee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.membersfeemodel')),
            ],
        ),
        migrations.AddField(
            model_name='credits',
            name='land_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.landmodel'),
        ),
        migrations.AddField(
            model_name='credits',
            name='meeting_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.protocolmodel'),
        ),
        migrations.AddField(
            model_name='credits',
            name='member_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.membermodel'),
        ),
        migrations.CreateModel(
            name='BankModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=70)),
                ('bik_bank', models.CharField(max_length=9)),
                ('inn_bank', models.CharField(max_length=10)),
                ('kpp', models.CharField(max_length=9)),
                ('correspondent_acc', models.CharField(max_length=20)),
                ('checking_acc', models.CharField(max_length=20)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.companymodel')),
            ],
        ),
        migrations.CreateModel(
            name='AgentModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=20)),
                ('second_name', models.CharField(max_length=20)),
                ('third_name', models.CharField(max_length=20)),
                ('position', models.CharField(max_length=50)),
                ('phone', models.CharField(blank=True, max_length=18)),
                ('address', models.CharField(blank=True, max_length=70)),
                ('doc', models.CharField(choices=[('0', 'Доверенность'), ('1', 'Протокол')], default='1', max_length=1)),
                ('num_doc', models.CharField(blank=True, max_length=15)),
                ('date_doc', models.DateField(null=True)),
                ('file_doc', models.FileField(blank=True, upload_to='')),
                ('active', models.BooleanField(default=False, null=True)),
                ('company_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.companymodel')),
            ],
        ),
        migrations.CreateModel(
            name='AccrualsCalculationModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateField()),
                ('date_finish', models.DateField()),
                ('type', models.CharField(max_length=20)),
                ('type_num', models.CharField(max_length=1)),
                ('sum', models.FloatField()),
                ('sum_edit', models.IntegerField()),
                ('debt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.debtsmodel')),
            ],
        ),
    ]
