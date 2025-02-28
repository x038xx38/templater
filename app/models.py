from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User
from datetime import datetime
import os


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    # return 'user_{0}/{1}'.format(instance.company.id, filename)
    return os.path.join(str(instance.company_id_id), filename)


class CompanyModel(models.Model):
    company_name = models.CharField(max_length=100)
    company_inn = models.CharField(max_length=10)
    company_ogrn = models.CharField(max_length=13)
    full_company_name = models.CharField(max_length=100)
    fio_manager = models.CharField(max_length=100)
    position_manager = models.CharField(max_length=50)
    full_address = models.CharField(max_length=100)
    phone = models.CharField(max_length=18)
    email = models.EmailField(max_length=50)
    user_snt = models.OneToOneField(User, on_delete=models.CASCADE)
    # penalty_id = models.ForeignKey(PenaltyModel, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.company_name

    class Meta:
        verbose_name = 'СНТ'
        verbose_name_plural = 'СНТ'


class PenaltyModel(models.Model):
    description = models.CharField(max_length=100)
    date_start = models.DateField(unique=True, null=True)
    attachment = models.FileField(upload_to=user_directory_path, blank=True)
    rate = models.FloatField()
    company_id = models.ForeignKey(CompanyModel, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.description

    class Meta:
        verbose_name = 'Начисления'
        verbose_name_plural = 'Начисления'


class BankModel(models.Model):
    bank_name = models.CharField(max_length=70)
    bik_bank = models.CharField(max_length=9)
    inn_bank = models.CharField(max_length=10)
    kpp = models.CharField(max_length=9)
    correspondent_acc = models.CharField(max_length=20)
    checking_acc = models.CharField(max_length=20)
    company_id = models.ForeignKey(CompanyModel, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.bank_name

    class Meta:
        verbose_name = 'Банковские реквизиты'
        verbose_name_plural = 'Банковские реквизиты'


class AgentModel(models.Model):
    CHOICE_DOC = (
        ('0', 'Доверенность'),
        ('1', 'Протокол'),
    )
    first_name = models.CharField(max_length=20)
    second_name = models.CharField(max_length=20)
    third_name = models.CharField(max_length=20)
    position = models.CharField(max_length=50)
    phone = models.CharField(max_length=18, blank=True)
    address = models.CharField(max_length=70, blank=True)
    doc = models.CharField(max_length=1, choices=CHOICE_DOC, default='1')
    num_doc = models.CharField(max_length=15, blank=True)
    date_doc = models.DateField(null=True)
    file_doc = models.FileField(upload_to=user_directory_path, blank=True)
    active = models.BooleanField(null=True, default=False)
    company_id = models.ForeignKey(CompanyModel, on_delete=models.CASCADE)

    def __unicode__(self):
        return self.second_name

    class Meta:
        verbose_name = 'Председатель'
        verbose_name_plural = 'Председатели'


class MembersFeeModel(models.Model):
    CHOICE_TYPE = (
        # ('0', '---'),
        ('0', 'Членский взнос'),
        ('1', 'Целевой взнос'),
    )
    CHOICE_PAYMENT = (
        ('1', 'Ежемесячные'),
        ('2', 'Ежеквартальные'),
        ('3', 'Ежегодные'),
    )
    num_doc = models.CharField(max_length=50)
    date_doc = models.DateField()
    date_start = models.DateField(blank=True, null=True)
    date_finish = models.DateField(blank=True, null=True)
    type_fee = models.CharField(max_length=1, choices=CHOICE_TYPE, default='0')
    payment_period = models.CharField(max_length=1, choices=CHOICE_PAYMENT, default='1')
    day_accrual = models.CharField(max_length=2)    # день начисления (называться будет как Дата начислени)
    amount_fee = models.FloatField()
    obj_fee = models.CharField(max_length=100)   # цель взноса (остановились на простом текстовом поле)
    attachment = models.FileField(upload_to=user_directory_path, blank=True)
    comment = models.TextField(max_length=150, blank=True)
    company_id = models.ForeignKey(CompanyModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Членский взнос'
        verbose_name_plural = 'Членские взносы'


class DebtCharges(models.Model):
    date_payment = models.DateField()
    # sum_payment = models.FloatField()
    id_member_fee = models.ForeignKey(MembersFeeModel, on_delete=models.CASCADE)


class MemberModel(models.Model):
    CHOICE_STATUS = (
        ('0', 'Не член товарищества'),
        ('1', 'Член товарищества'),
    )
    first_name = models.CharField(max_length=40)
    second_name = models.CharField(max_length=40)
    third_name = models.CharField(max_length=40)
    email = models.EmailField(max_length=50, blank=True, null=True)
    phone = models.CharField(
        max_length=18,
        blank=True)
    address = models.CharField(max_length=150)
    status = models.CharField(
        max_length=1,
        choices=CHOICE_STATUS,
        blank=True,
        default='1'
    )
    # Добавление дополнительных полей
    issued = models.CharField(max_length=255, default='')
    date_of_issue = models.DateField(blank=True, null=True, default=datetime.today())
    division_code = models.CharField(max_length=7, default='000-000')
    series_number_doc = models.CharField(max_length=15, default='00 00 № 000000')
    date_of_birth = models.DateField(blank=True, null=True,default=datetime.today())
    place_of_birth = models.CharField(max_length=100, default='')

    company_id = models.ForeignKey(CompanyModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Член товарищества'
        verbose_name_plural = 'Члены товарищества'


class LandModel(models.Model):
    number = models.CharField(max_length=10)
    kadastr_number = models.CharField(max_length=30)
    land_address = models.CharField(max_length=150)
    comment = models.TextField(max_length=200, blank=True)
    attachment = models.FileField(upload_to=user_directory_path, blank=True)
    members = models.ManyToManyField(MemberModel, related_name='lands', through='OwnershipModel', blank=True)
    company_id = models.ForeignKey(CompanyModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.land_address

    class Meta:
        verbose_name = 'Земельный участок'
        verbose_name_plural = 'Земельные участки'

    # @classmethod
    # def add_land(cls, current_member, new_land):
    #     new_land.members.add(current_member)
    #
    # @classmethod
    # def del_land(cls, current_member, cancel_land):
    #     cancel_land.members.remove(current_member)


class OwnershipModel(models.Model):
    member = models.ForeignKey(MemberModel, on_delete=models.CASCADE)
    land = models.ForeignKey(LandModel, on_delete=models.CASCADE)
    start_hold = models.DateField(blank=True, null=True)
    end_hold = models.DateField(blank=True, null=True)
    comment = models.TextField(max_length=200, blank=True)
    attachment = models.FileField(upload_to=user_directory_path, blank=True)


class DebtsModel(models.Model):
    CHOICE_ACC = (
        ('0', 'Автоматические начисления'),
        ('1', 'На дату окончания задолженности'),
    )
    CHOICE_DOC = (
        ('0', 'Членский взнос'),
        ('1', 'Целевой взнос'),
    )
    start_debt = models.DateField()
    end_debt = models.DateField(blank=True, null=True)
    type_accuals = models.CharField(max_length=1, choices=CHOICE_ACC, default='0')
    type_doc = models.CharField(max_length=1, choices=CHOICE_DOC, default='0')
    sum = models.FloatField(blank=True, null=True)
    land = models.ForeignKey(LandModel, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.start_debt) + ' - ' + str(self.end_debt)

    class Meta:
        verbose_name = 'Задолженность'
        verbose_name_plural = 'Задолженности'


class PenaltyCalculationModel(models.Model):
    date = models.CharField(max_length=30)
    date_start = models.DateField()
    date_finish = models.DateField()
    rate = models.FloatField()
    type = models.CharField(max_length=1)
    days = models.IntegerField()
    sum = models.FloatField()
    sum_edit = models.IntegerField()
    debt = models.ForeignKey(DebtsModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Калькуляция пени'
        verbose_name_plural = 'Калькуляций пени'


class AccrualsCalculationModel(models.Model):
    date_start = models.DateField()
    date_finish = models.DateField()
    type = models.CharField(max_length=20)
    type_num = models.CharField(max_length=1)
    sum = models.FloatField()
    sum_edit = models.IntegerField()
    debt = models.ForeignKey(DebtsModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Калькуляция начислений'
        verbose_name_plural = 'Калькуляций начислений'


class PaymentsModel(models.Model):
    CHOICE_DOC = (
        ('0', 'Членский взнос'),
        ('1', 'Целевой взнос'),
    )
    fio = models.CharField(max_length=100)
    date_payment = models.DateField()
    type_payment = models.CharField(max_length=1, choices=CHOICE_DOC, default='0')
    sum_payment = models.FloatField()
    comment = models.TextField(max_length=200, blank=True)
    land = models.ForeignKey(LandModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.fio + ' - ' + str(self.sum_payment)

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'


class ScanCompanyModel(models.Model):
    ustav = models.FileField(upload_to=user_directory_path, blank=True)
    ogrn = models.FileField(upload_to=user_directory_path, blank=True)
    inn = models.FileField(upload_to=user_directory_path, blank=True)
    yegryul = models.FileField(upload_to=user_directory_path, blank=True)
    company_id = models.ForeignKey(CompanyModel, on_delete=models.CASCADE)


class ProtocolModel(models.Model):
    number = models.CharField(max_length=20)
    date_start = models.DateField()
    date_finish = models.DateField()
    renta = models.FloatField()
    company_id = models.ForeignKey(CompanyModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Протокол собрания'
        verbose_name_plural = 'Протоколы собрания'


class Credits(models.Model):
    date_start = models.DateField()
    date_finish = models.DateField(blank=True, null=True)
    summa = models.FloatField()
    land_id = models.ForeignKey(LandModel, on_delete=models.CASCADE)
    meeting_id = models.ForeignKey(ProtocolModel, on_delete=models.CASCADE)
    member_id = models.ForeignKey(MemberModel, on_delete=models.CASCADE)


class CourtMoscow(models.Model):
    id_court = models.CharField(max_length=36, null=True)
    code = models.CharField(max_length=10, null=True)
    number = models.IntegerField(null=True)
    full_name = models.CharField(max_length=40, null=True)
    polygon_data = models.MultiPolygonField(srid=4326)
    short_name = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=50, null=True)
    phones = models.CharField(max_length=20, null=True)
    phone_info = models.CharField(max_length=20, null=True)
    territorial_info = models.TextField(null=True)
    judge_fio = models.CharField(max_length=40, null=True)
    dinner_time = models.CharField(max_length=50, null=True)
    week_ends = models.CharField(max_length=50, null=True)
    counsulting_hours = models.CharField(max_length=50, null=True)
    business_hours = models.CharField(max_length=50, null=True)
    email = models.CharField(max_length=30, null=True)
    court_latitude = models.FloatField(null=True)
    court_longitude = models.FloatField(null=True)

    class Meta:
        verbose_name = 'Судебный участок (центр)'
        verbose_name_plural = 'Судебные участки (центр)'


class CourtMoscowRegion(models.Model):
    short_name = models.CharField(max_length=40, null=True)
    region_name = models.CharField(max_length=40, null=True)
    code = models.CharField(max_length=10, null=True)
    address = models.CharField(max_length=50, null=True)
    phones = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=20, null=True)
    url = models.CharField(max_length=20, null=True)

    class Meta:
        verbose_name = 'Судебный участок (область)'
        verbose_name_plural = 'Судебные участки (область)'


class HistoryTemplate(models.Model):
    date_template = models.DateTimeField(unique=False, null=True)
    name_template = models.CharField(max_length=100)
    file_template = models.FileField(upload_to=user_directory_path, null=True)
    member_id = models.ForeignKey(MemberModel, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'История создания шаблонов'
        verbose_name_plural = 'История создания шаблонов'


class HistoryDoc(models.Model):
    view_template = models.CharField(max_length=40)
    pretrial = models.FileField(null=True)
    judicial = models.FileField(null=True)
    court_order = models.FileField(null=True)
    credit_id = models.ForeignKey(Credits, on_delete=models.CASCADE)


class KeyRate(models.Model):
    date = models.DateField(unique=True)
    rate = models.FloatField()

    class Meta:
        verbose_name = 'Ключевая ставка'
        verbose_name_plural = 'Ключевая ставка'
