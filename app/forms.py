from datetime import timedelta

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Row, Column, Submit, Field, ButtonHolder, Button, Fieldset, HTML, Hidden
from crispy_forms.bootstrap import FormActions, PrependedText, FieldWithButtons, StrictButton
from app.models import *


class JudicialTmpForm(forms.Form):
    """
        Шаблон для мульти-формы "Исковое заявление".
        С его помощью я формирую конечный документ.
    """
    org_name = forms.CharField(label='Наименование СНТ', max_length=100, )
    org_inn = forms.CharField(label='ИНН СНТ', max_length=50, )
    org_ogrn = forms.CharField(label='ОГРН СНТ', max_length=50, )
    org_full_address = forms.CharField(label='Адрес СНТ', max_length=100, )

    # Представитель
    agent_name = forms.CharField(label='Представитель СНТ', max_length=50, )
    agent_address = forms.CharField(label='Адрес представителя СНТ', max_length=50, )
    agent_phone = forms.CharField(label='Телефон представителя СНТ', max_length=50, )

    # Банковские реквизиты
    # bank_name = forms.CharField(max_length=100, label='Наименование банка',)
    # bank_bik = forms.CharField(max_length=100, label='БИК',)
    # bank_inn = forms.CharField(max_length=100, label='ИНН',)
    # bank_kpp = forms.CharField(max_length=100, label='КПП',)
    # bank_correspondent_acc = forms.CharField(max_length=100, label='Корреспондетский счет',)


class PretrialTmpForm(forms.Form):
    """
        Шаблон для Мульти-формы "Досудебная претензия"
        С его помощью формируем готовый документ
    """
    member_name = forms.CharField(label='ФИО должника', max_length=100, )
    address_land = forms.CharField(label='Адрес земельного участка', max_length=100, )
    num_land = forms.CharField(label='Номер земельного участка', max_length=10, )
    cadastr_num = forms.CharField(label='Кадастровый номер', max_length=30, )

    # Задолженность
    amount_debt = forms.CharField(label='Сумма задолженности', max_length=15, )
    start_debt = forms.CharField(label='Начало задолжености', max_length=15, )
    end_debt = forms.CharField(label='Конец задолженности', max_length=15, )

    # company_name = forms.CharField(label='Наименование СНТ', max_length=50,)
    # fio_manager = forms.CharField(label='Председатель', max_length=50,)
    # company_contact = forms.CharField(label='Контакты', max_length=50,)

    # Протокол собрания
    protocol_create = forms.CharField(label='Дата принятия протокола', max_length=15, )
    protocol_period = forms.CharField(label='Период протокола', max_length=15, )
    protocol_renta = forms.CharField(label='Сумма взносов(меся)', max_length=15, )

    # Банковские реквизиты
    # bank_name = forms.CharField(label='Наименование банка', max_length=100,)
    # bank_bik = forms.CharField(label='БИК', max_length=100,)
    # bank_inn = forms.CharField(label='ИНН', max_length=100,)
    # bank_kpp = forms.CharField(label='КПП', max_length=100,)
    # bank_ogrn = forms.CharField(label='ОГРН', max_length=100,)
    # bank_correspondent_acc = forms.CharField(label='Корреспондетский счет', max_length=100,)
    # bank_payment_acc = forms.CharField(label='Расчетный счет', max_length=100,)Co


class MemberForm(forms.ModelForm):
    """
        Член товарищества
    """
    first_name = forms.CharField(
        label='Имя: ',
        max_length=40,
        # widget=forms.TextInput(attrs={'placeholder': 'Имя'})
    )
    second_name = forms.CharField(
        label='Фамилия: ',
        max_length=40,
        # widget=forms.TextInput(attrs={'placeholder': 'Фамилия'})
    )
    third_name = forms.CharField(
        label='Отчество: ',
        max_length=40,
        # widget=forms.TextInput(attrs={'placeholder': 'Отчество'})
    )
    phone = forms.CharField(
        label='Номер телефона: ',
        max_length=18,
        widget=forms.TextInput(attrs={'data-mask': '+7 (000) 000-00-00',
                                      'placeholder': '+7 (000) 000-00-00'}),
        required=False
    )
    email = forms.CharField(
        label='Электронная почта: ',
        max_length=50,
        required=False
    )
    status = forms.CharField(
        label='Статус',
        max_length=1,
        widget=forms.Select(choices=MemberModel.CHOICE_STATUS),
        initial='1'
    )

    address = forms.CharField(
        label='Адрес регистрации: ',
        max_length=100
    )

    issued = forms.CharField(
        label='Кем выдан: ',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 2, 'cols': 20,
            }
        )
    )

    date_of_issue = forms.DateField(
        label='Дата выдачи: ',
        input_formats=['%d.%m.%Y'],
        required=False
    )

    division_code = forms.CharField(
        label='Код подразделения: ',
        max_length=7,
        widget=forms.TextInput(attrs={'data-mask': '000-000',
                                      'placeholder': '000-000'}),
        required=False
    )

    series_number_doc = forms.CharField(
        label='Серия и номер паспорта: ',
        max_length=15,
        widget=forms.TextInput(attrs={'data-mask': '00 00 № 000000',
                                      'placeholder': '00 00 № 000000'}),
        required=False
    )

    date_of_birth = forms.DateField(
        label='Дата рождения: ',
        input_formats=['%d.%m.%Y'],
        required=False
    )

    place_of_birth = forms.CharField(
        label='Место рождения: ',
        max_length=100,
        required=False
    )

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        Div(
            Div('second_name', css_class='col'),
            Div('first_name', css_class='col'),
            css_class='row'
        ),
        Div(
            Div('third_name', css_class='col'),
            Div('status', css_class='col'),
            css_class='row'
        ),
        Div('address'),
        Div('series_number_doc'),
        Div(
            Div('division_code', css_class='col'),
            Div('date_of_issue', css_class='col'),
            css_class='row'
        ),
        Div('issued'),
        Div(
            Div('date_of_birth', css_class='col'),
            Div('place_of_birth', css_class='col'),
            css_class='row'
        ),
        Div(
            Div('phone', css_class='col'),
            Div('email', css_class='col'),
            css_class='row'
        )
    )

    class Meta:
        model = MemberModel
        fields = ['first_name', 'second_name', 'third_name', 'email', 'phone', 'address',
                  'series_number_doc', 'division_code', 'date_of_issue', 'issued', 'date_of_birth', 'place_of_birth',
                  'status', 'id']


class OwnershipForm(forms.ModelForm):
    start_hold = forms.DateField(
        label='C даты: ',
        input_formats=['%d.%m.%Y'],
        widget=forms.TextInput(
            attrs={
                # 'class': 'form-control-sm',
            }
        )
    )

    end_hold = forms.DateField(
        label='По дату: ',
        input_formats=['%d.%m.%Y'],
        widget=forms.TextInput(
            attrs={
                # 'class': 'form-control-sm',
            }
        )
    )

    comment = forms.CharField(
        label='Комментарий: ',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 2, 'cols': 20,
                # 'class': 'form-control-sm',
            }
        )
    )

    attachment = forms.FileField(
        label='Приложение: ',
        required=False,

        widget=forms.FileInput(
            attrs={
                'accept': 'application/pdf',
                # 'class': 'form-control-sm',
            }

        )
    )

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        Row(
            Column('start_hold'),
            Column('end_hold'),
        ),
        Field('attachment'),
        Field('comment'),
    )

    class Meta:
        model = OwnershipModel
        fields = ['start_hold', 'end_hold', 'comment', 'attachment']


class CreditForm(forms.ModelForm):
    date_start = forms.DateField(
        label='Начало задолженности',
        input_formats=['%d.%m.%Y'],
    )
    date_finish = forms.DateField(
        label='Конец задолженности',
        input_formats=['%d.%m.%Y'],
    )
    summa = forms.FloatField(label='Сумма задолженности')

    class Meta:
        model = Credits
        fields = ['date_start', 'date_finish', 'summa', 'land_id', 'meeting_id']


class LandsForm(forms.ModelForm):
    number = forms.CharField(
        label='Номер участка: ',
        max_length=10,
        widget=forms.TextInput(
            attrs={
                # 'class': 'form-control-sm',
            }
        )
    )
    kadastr_number = forms.CharField(
        label='Кадастровый номер: ',
        max_length=30,
        widget=forms.TextInput(
            attrs={
                'data-mask': '00:00:0000000:0000',
                'placeholder': 'XX:XX:ХХХХХХХ:ХХХХ',
                # 'class': 'form-control-sm',
            }),
    )
    land_address = forms.CharField(
        label='Адрес участка: ',
        max_length=150,
        widget=forms.TextInput(
            attrs={
                # 'class': 'form-control-sm',
            }
        )
    )

    comment = forms.CharField(
        label='Комментарий: ',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 2, 'cols': 20,
                # 'class': 'form-control-sm',
            }
        )
    )

    attachment = forms.FileField(
        label='Приложение: ',
        required=False,
        widget=forms.FileInput(
            attrs={
                'accept': 'application/pdf',
                # 'class': 'form-control-sm ',
            }
        )
    )

    helper = FormHelper()
    helper.form_method = 'POST'
    # helper.label_class = 'form-control-sm m-0 p-0'
    helper.layout = Layout(
        Row(
            Column('number', css_class='col-sm-6 mb-0'),
            Column('kadastr_number', css_class='col-sm-6 mb-0'),
            css_class='form-row'
        ),
        Row(
            Column('land_address'),
        ),
        Field('attachment'),
        Field('comment'),
        Hidden('id_land', '')
    )

    class Meta:
        model = LandModel
        fields = ['number', 'kadastr_number', 'land_address', 'comment', 'attachment']


class ProtocolForm(forms.ModelForm):
    """
        Форма для создания Протоколов собрания
    """
    number = forms.IntegerField(label='Номер протокола')
    date_start = forms.DateField(label='Начало действия', input_formats=['%d.%m.%Y'], required=False)
    date_finish = forms.DateField(label='Окончание действия', input_formats=['%d.%m.%Y'], required=False)
    renta = forms.FloatField(label='Размер взносов (мес)')

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        Div(
            Div('number', css_class='col'),
            Div('date_start', css_class='col'),
            css_class='row'
        ),
        Div(
            Div('renta', css_class='col'),
            Div('date_finish', css_class='col'),
            css_class='row'
        ),
        FormActions(
            Submit('save_meeting', 'Сохранить', css_class="btn-primary pull-right"),
        )
    )

    class Meta:
        model = ProtocolModel
        fields = ['number', 'date_start', 'date_finish', 'renta']


class DebitForm(forms.ModelForm):
    class Meta:
        model = DebtsModel
        fields = ['start_debt', 'end_debt', 'sum', 'type_accuals', 'type_doc']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', '')
        super(DebitForm, self).__init__(*args, **kwargs)

        # staff_reviewers = User.objects.staff().only('full_name', 'pk')

        self.fields['land'] = forms.ModelChoiceField(
            label='Участок: ',
            # choices=LandModel.objects.all().values_list('land_address')
            widget=forms.Select,
            queryset=LandModel.objects.filter(company_id__user_snt=user)
        )

    start_debt = forms.DateField(
        label='Начало задолженности: ',
        input_formats=['%d.%m.%Y']
    )

    end_debt = forms.DateField(
        label='Конец задолженности: ',
        required=False,
        input_formats=['%d.%m.%Y']
    )

    type_accuals = forms.CharField(
        label='Способ начисления: ',
        required=False,
        initial='0',
        widget=forms.RadioSelect(choices=DebtsModel.CHOICE_ACC)
    )

    type_doc = forms.CharField(
        label='Тип взноса: ',
        max_length=1,
        required=False,
        widget=forms.Select(choices=DebtsModel.CHOICE_DOC),
        initial='0'
    )

    sum = forms.FloatField(
        required=False,
        label='Сумма задолженности: '
    )

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        Row(
            Column('start_debt'),
            Column('end_debt'),
        ),
        Field('sum'),
        Field('land'),
        Field('type_doc'),
        Field('type_accuals')
    )


class PaymentForm(forms.ModelForm):
    class Meta:
        model = PaymentsModel
        fields = ['date_payment', 'type_payment', 'sum_payment', 'fio', 'comment']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', '')
        super(PaymentForm, self).__init__(*args, **kwargs)
        self.fields['land'] = forms.ModelChoiceField(
            label='Участок: ',
            widget=forms.Select,
            queryset=LandModel.objects.filter(company_id__user_snt=user)
        )

    date_payment = forms.DateField(
        label='Дата платежа: ',
        input_formats=['%d.%m.%Y']
    )

    type_payment = forms.CharField(
        label='Тип взноса: ',
        max_length=1,
        required=False,
        widget=forms.Select(choices=PaymentsModel.CHOICE_DOC),
        initial='0'
    )

    sum_payment = forms.FloatField(
        label='Сумма платежа: '
    )

    fio = forms.CharField(
        label='Имя плательщика: ',
        max_length=150,
    )

    comment = forms.CharField(
        label='Комментарий: ',
        required=False,
        widget=forms.Textarea(
            attrs={
                'rows': 2, 'cols': 20,
            }
        )
    )

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        Row(
            Column('date_payment'),
            Column('sum_payment'),
        ),
        Field('type_payment'),
        Field('fio'),
        Field('land'),
        Field('comment'),
    )


class InputInnForm(forms.Form):
    inn = forms.CharField(
        label='ИНН: ',
        max_length=10,
        help_text='ИНН организации содержит 10 знаков'
    )

    helper = FormHelper()
    # helper.form_method = 'post'
    # helper.form_id = 'find-inn'
    # helper.form_action = '/app/company'
    helper.layout = Layout(
        Div(
            Div('inn', css_class='col pr-0'),
            HTML(
                '<div class="col-auto" style="margin-top:36px; margin-left:0px"><button type="button" name="find_inn"'
                ' id="submit-id-find-inn" class="btn btn-primary">'
                '<i class="fas fa-search"></i>&nbsp;&nbsp;Поиск</button></div>'),
            css_class='row',
        )
    )


class InputBikForm(forms.Form):
    bik = forms.CharField(
        label='БИК: ',
        max_length=9,
        help_text='БИК банка содержит 9 знаков'
    )

    helper = FormHelper()
    helper.layout = Layout(
        Div(
            Div('bik', css_class='col pr-0'),
            HTML(
                '<div class="col-auto" style="margin-top:36px; margin-left:0px"><button type="button" name="find_bik"'
                ' id="submit-id-find-bik" class="btn btn-primary">'
                '<i class="fas fa-search"></i>&nbsp;&nbsp;Поиск</button></div>'),
            css_class='row',
        )
    )


class MainSettingsForm(forms.ModelForm):
    class Meta:
        model = CompanyModel
        fields = ['company_name', 'company_inn', 'company_ogrn', 'full_company_name', 'fio_manager',
                  'position_manager', 'full_address', 'phone', 'email']

    company_name = forms.CharField(max_length=100, label='Наименование организации: ')
    company_inn = forms.CharField(max_length=10, label='ИНН: ')
    company_ogrn = forms.CharField(max_length=13, label='ОГРН: ')
    full_company_name = forms.CharField(max_length=100, label='Наименование организации (полное): ')
    fio_manager = forms.CharField(
        max_length=100,
        label='Руководитель организации: ',
    )
    position_manager = forms.CharField(
        max_length=50,
        label='Должность: ',
    )
    full_address = forms.CharField(max_length=100, label='Юридический адрес: ')
    phone = forms.CharField(
        max_length=18,
        label='Телефон организации: ',
        required=False,
        widget=forms.TextInput(attrs={
            'data-mask': '+7 (000) 000-00-00',
            'placeholder': '+7 (000) 000-00-00'
        })
    )
    email = forms.CharField(max_length=50, label='Электронная почта: ', required=False)
    # rate = forms.FloatField(
    #     label='Пени: ',
    #     widget=forms.NumberInput(attrs={
    #             'data-toggle': 'tooltip',
    #             'data-placement': 'right',
    #             'title': 'Данное поле необходимо для корректного расчета задолженности',
    #     })
    # )
    # Реализация выпадающего списка для формы
    # agent_id = forms.ChoiceField(label='Представитель', choices=[])
    # bank_id = forms.ChoiceField(label='Расчетный счет', choices=[])

    # Реализация выпадающего списка для формы
    # def __init__(self, user, *args, **kwargs):
    #     super(MainSettingsForm, self).__init__(*args, **kwargs)
    #     agent_list = []
    #     agent_obj = AgentModel.objects.filter(user_snt=user)
    #     for item in agent_obj:
    #         agent_list.append((item.id, item.fio))
    #
    #     bank_list = []
    #     bank_obj = BankModel.objects.filter(user_snt=user)
    #     for item in bank_obj:
    #         bank_list.append((item.id, item.checking_acc))
    #
    #     self.fields['agent_id'].choices = agent_list
    #     self.fields['bank_id'].choices = bank_list

    helper = FormHelper()
    helper.layout = Layout(
        Div(
            Div('company_inn', css_class='col'),
            HTML('<div class="col mt-sm-auto mb-sm-3"><a href="#" class="url_find_inn" data-toggle="modal" '
                 'data-target="#modal-inn"><span><b>Заполнить по ИНН</b></span></a></div>'),
            css_class='row'
        ),
        Div(
            Div('company_name', css_class='col'),
            Div('company_ogrn', css_class='col'),
            css_class='row'
        ),
        Field('full_company_name'),
        Div(
            Div('fio_manager', css_class='col'),
            Div('position_manager', css_class='col'),
            css_class='row'
        ),
        Field('full_address'),
        # Div(
        #     Div('rate', css_class='col'),
        #     Div('', css_class='col'),
        #     css_class='row'
        # ),
        Div(
            Div('phone', css_class='col'),
            Div('email', css_class='col'),
            css_class='row'
        ),
        # Реализация выпадающего списка для формы
        # Div(
        #     Div('agent_id', css_class='col'),
        #     Div('bank_id', css_class='col'),
        #     css_class='row'
        # ),
        # ButtonHolder(
        #     HTML('<div class="float-right mt-4"><button type="button" name="company_edit" id="submit-id-company_edit"'
        #          ' class="btn btn-primary" data-toggle="modal" data-target="#modal_company">'
        #          '<i class="fas fa-edit"></i>&nbsp;&nbsp;Редактировать</button></div>')
        # )
    )


class BankSettingsForm(forms.ModelForm):
    class Meta:
        model = BankModel
        fields = ['bank_name', 'bik_bank', 'inn_bank', 'kpp', 'correspondent_acc', 'checking_acc']

    bank_name = forms.CharField(max_length=70, label='Наименование банка: ')
    bik_bank = forms.CharField(max_length=9, label='БИК: ')
    inn_bank = forms.CharField(max_length=10, label='ИНН: ')
    kpp = forms.CharField(max_length=9, label='КПП: ')
    correspondent_acc = forms.CharField(max_length=20, label='Корреспондетский счет: ')
    checking_acc = forms.CharField(max_length=20, label='Расчетный счет: ')

    helper = FormHelper()
    helper.layout = Layout(
        Div(
            Div('bank_name', css_class='col'),
            HTML('<div class="col mt-sm-auto mb-sm-3"><a href="#" data-toggle="modal" '
                 'data-target="#modal-bik"><span><b>Заполнить по БИК</b></span></a></div>'),
            css_class='row'
        ),
        Div(
            Div('bik_bank', css_class='col'),
            Div('inn_bank', css_class='col'),
            css_class='row'
        ),
        Div(
            Div('kpp', css_class='col'),
            Div('correspondent_acc', css_class='col'),
            css_class='row'
        ),
        Field('checking_acc')
    )


class AgentForm(forms.ModelForm):
    class Meta:
        model = AgentModel
        fields = ['first_name', 'second_name', 'third_name', 'position', 'phone', 'address',
                  'doc', 'num_doc', 'date_doc', 'file_doc']

    first_name = forms.CharField(max_length=50, label='Имя представителя: ')
    second_name = forms.CharField(max_length=50, label='Фамилия представителя: ')
    third_name = forms.CharField(max_length=50, label='Отчество представителя: ')

    position = forms.CharField(max_length=50, label='Должность: ')
    phone = forms.CharField(
        label='Телефон представителя: ',
        max_length=18,
        required=False,
        widget=forms.TextInput(attrs={'data-mask': '+7 (000) 000-00-00'})
    )
    address = forms.CharField(max_length=70, label='Адрес представителя: ')
    doc = forms.CharField(
        label='Вид документа: ',
        max_length=1,
        widget=forms.Select(choices=AgentModel.CHOICE_DOC))
    num_doc = forms.CharField(max_length=15, label='Номер документа: ')
    date_doc = forms.DateField(
        label='Дата документа: ',
        input_formats=['%d.%m.%Y']
    )

    file_doc = forms.FileField(
        label='Скан документа: ',
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.layout = Layout(
        Div(
            Div('first_name', css_class='col'),
            Div('second_name', css_class='col'),
            css_class='row'
        ),
        Field('third_name'),
        Div(
            Div('position', css_class='col'),
            Div('phone', css_class='col'),
            css_class='row'
        ),
        Field('address'),
        Div(
            Div('doc', css_class='col'),
            Div('date_doc', css_class='col'),
            Div('num_doc', css_class='col'),
            css_class='row'
        ),
        # Field('file_doc'),
        Div(
            HTML('<label for="id_file_doc" class=" requiredField">Скан документа: <span class="asteriskField">*</span> '
                 '</label><div class="custom-file"><input type="file" name="file_doc" class="custom-file-input" '
                 'id="id_file_doc" lang="ru"><label class="custom-file-label" for="id_file_doc"></label></div>')
        )
    )


class ScanCompanyForm(forms.ModelForm):
    class Meta:
        model = ScanCompanyModel
        fields = ['ustav', 'ogrn', 'inn', 'yegryul']

    helper = FormHelper()
    helper.form_method = 'post'
    helper.layout = Layout(
        Div(
            HTML('<label>Устав организации: '
                 '</label><div class="custom-file"><input type="file" name="ustav" class="custom-file-input" '
                 'id="id_ustav" accept="application/pdf" /><label class="custom-file-label" '
                 'for="id_ustav"></label></div>'),
            css_class='form-group'
        ),
        Div(
            HTML('<label>Свидетельство ОГРН: '
                 '</label><div class="custom-file"><input type="file" name="ogrn" class="custom-file-input" '
                 'id="id_ogrn" accept="application/pdf" /><label class="custom-file-label" '
                 'for="id_ogrn"></label></div>'),
            css_class='form-group'
        ),
        Div(
            HTML('<label>Свидетельство ИНН: '
                 '</label><div class="custom-file"><input type="file" name="inn" class="custom-file-input" '
                 'id="id_inn" accept="application/pdf" /><label class="custom-file-label" '
                 'for="id_inn"></label></div>'),
            css_class='form-group'
        ),
        Div(
            HTML('<label>Выписка ЕГРЮЛ: '
                 '</label><div class="custom-file"><input type="file" name="yegryul" class="custom-file-input" '
                 'id="id_yegryul" accept="application/pdf" /><label class="custom-file-label" '
                 'for="id_yegryul"></label></div>'),
            css_class='form-group'
        ),

    )


class PenaltyForm(forms.ModelForm):
    class Meta:
        model = PenaltyModel
        fields = ['date_start', 'description', 'attachment', 'rate']

    date_start = forms.DateField(
        label='Дата документа: ',
        input_formats=['%d.%m.%Y']
    )
    description = forms.CharField(
        label='На основании: ',
        max_length=100
    )
    attachment = forms.FileField(
        label='Приложение: ',
        required=False,
        widget=forms.FileInput(attrs={'accept': 'application/pdf'})
    )
    rate = forms.FloatField(
        label='Размер неустойки: '
    )

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        Field('description'),
        Div(
            Div('date_start', css_class='col'),
            Div('rate', css_class='col'),
            css_class='row'
        ),
        Field('attachment')
    )


class MembersFeeForm(forms.ModelForm):
    """
        Справочник "Членские взносы"
    """

    class Meta:
        model = MembersFeeModel
        fields = ['num_doc', 'date_doc', 'date_start', 'date_finish', 'type_fee', 'payment_period', 'day_accrual',
                  'obj_fee', 'amount_fee', 'attachment', 'comment']

        # fields = '__all__'

    # def clean(self):
    #     cleaned_data = super().clean()
    #
    #     type_fee = cleaned_data.get('type_fee', '')
    #     fee_date_start = cleaned_data.get('date_start', '')
    #     fee_date_finish = cleaned_data.get('date_finish', '')
    #
    #     fee_first = MembersFeeModel.objects.filter(type_fee=type_fee).order_by('id').first()
    #     fee_last = MembersFeeModel.objects.filter(type_fee=type_fee).order_by('-id').first()
    #     start_range = fee_first.date_start
    #     end_range = fee_last.date_finish
    #
    #     if start_range < fee_date_start < end_range:
    #         msg = 'Период пересекается с записями в базе данных!'
    #         raise forms.ValidationError(msg)
    #
    #     if start_range < fee_date_finish < end_range:
    #         msg = 'Период пересекается с записями в базе данных!'
    #         raise forms.ValidationError(msg)
    #
    #     if (fee_date_start < start_range - timedelta(days=1)) and (fee_date_finish != start_range - timedelta(days=1)):
    #         msg = 'Между периодами документов не должно быть "пробелов"!'
    #         raise forms.ValidationError(msg)
    #
    #     # # проверяем условие "после"
    #     if (end_range + timedelta(days=1) < fee_date_finish) and (fee_date_start != end_range + timedelta(days=1)):
    #         msg = 'Между периодами документов не должно быть "пробелов"!'
    #         raise forms.ValidationError(msg)
    #
    #     return cleaned_data

    num_doc = forms.CharField(
        label='Номер протокола: ',
        max_length=50
    )
    date_doc = forms.DateField(
        label='Дата протокола: ',
        input_formats=['%d.%m.%Y']
    )
    date_start = forms.DateField(
        label='C даты: ',
        input_formats=['%d.%m.%Y'],
        required=False,
    )
    date_finish = forms.DateField(
        label='По дату: ',
        input_formats=['%d.%m.%Y'],
        required=False,
    )
    type_fee = forms.CharField(
        label='Тип взноса: ',
        max_length=1,
        required=False,
        widget=forms.Select(choices=MembersFeeModel.CHOICE_TYPE),
        initial='0'
    )
    payment_period = forms.CharField(
        label='Период начисления: ',
        max_length=1,
        required=False,
        widget=forms.Select(choices=MembersFeeModel.CHOICE_PAYMENT),
        initial='0'
    )
    day_accrual = forms.CharField(
        required=False,
        label='Дата начисления: ',
        # input_formats=['%d.%m.%Y'],
    )
    amount_fee = forms.FloatField(
        label='Размер взноса: '
    )
    obj_fee = forms.CharField(
        required=False,
        label='Цель взноса: ',
        max_length=150
    )
    attachment = forms.FileField(
        label='Приложение: ',
        required=False,
        widget=forms.FileInput(attrs={'accept': 'application/pdf'})
    )
    comment = forms.CharField(
        label='Комментарий: ',
        required=False,
        widget=forms.Textarea(attrs={'rows': 5, 'cols': 20})
    )

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        Div(
            Div('num_doc', css_class='col'),
            Div('date_doc', css_class='col'),
            css_class='row'
        ),
        Div(
            Div('type_fee', css_class='col'),
            Div('amount_fee', css_class='col'),
            css_class='row'
        ),
        Div(
            Div(
                Div('date_start', css_class='col'),
                Div('date_finish', css_class='col'),
                css_class='row'
            ),
            Div(
                Div('payment_period', css_class='col'),
                Div('day_accrual', css_class='col'),
                css_class='row'
            ),
            css_class='section_1'
        ),
        Div(
            Div(
                HTML(
                    '<div class="col"><div id="div_id_date_finish_pay" class="form-group">'
                    '<label for="id_date_finish_pay">Дата оплаты: </label>'
                    '<div><input type="text" name="date_finish_pay" class="form-control" id="id_date_finish_pay">'
                    '</div></div></div>'),
                Div('obj_fee', css_class='col'),
                css_class='row'
            ),
            css_class='section_2'
        ),
        Field('attachment'),
        Field('comment'),
    )

# тестовый набросок
# class MessageForm(forms.Form):
#     text_input = forms.CharField(
#         label='Общая сумма задолженности'
#     )
#
#     textarea = forms.CharField(
#         widget = forms.Textarea(),
#     )
#
#     radio_buttons = forms.ChoiceField(
#         choices = (
#             ('option_one', "Option one is this and that be sure to include why it's great"),
#             ('option_two', "Option two can is something else and selecting it will deselect option one")
#         ),
#         widget = forms.RadioSelect,
#         initial = 'option_two',
#     )
#
#     checkboxes = forms.MultipleChoiceField(
#         choices = (
#             ('option_one', "Option one is this and that be sure to include why it's great"),
#             ('option_two', 'Option two can also be checked and included in form results'),
#             ('option_three', 'Option three can yes, you guessed it also be checked and included in form results')
#         ),
#         initial = 'option_one',
#         widget = forms.CheckboxSelectMultiple,
#         help_text = "<strong>Note:</strong> Labels surround all the options for much larger click areas and a
#         more usable form.",
#     )
#
#     appended_text = forms.CharField(
#         help_text = "Here's more help text"
#     )
#
#     prepended_text = forms.CharField()
#
#     prepended_text_two = forms.CharField()
#
#     multicolon_select = forms.MultipleChoiceField(
#         choices = (('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')),
#     )
#
#     # Uni-form
#     helper = FormHelper()
#     # helper.form_class = 'form-horizontal'
#     helper.layout = Layout(
#         Field('text_input', css_class='input-xlarge w-50'),
#         Field('textarea', rows="3", css_class='input-xlarge'),
#         'radio_buttons',
#         Field('checkboxes', style="background: #FAFAFA; padding: 10px;"),
#         AppendedText('appended_text', '.00'),
#         PrependedText('prepended_text', '<input type="checkbox" checked="checked" value="" id="" name="">',
#         active=True),
#         PrependedText('prepended_text_two', '@'),
#         'multicolon_select',
#
#         FormActions(
#             Submit('save_changes', 'Save changes', css_class="btn-primary"),
#             Submit('cancel', 'Cancel'),
#         )
#     )
