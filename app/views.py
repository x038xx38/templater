from templater import settings
from templater.settings import MEDIA_ROOT
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.template.loader import render_to_string
from django.http.response import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils.formats import localize
from django.utils import dateformat
from django.core import serializers

from collections import ChainMap
import mimetypes

from app.models import *
from .forms import *

from django.db.models import Sum, Count

from dadata import Dadata
from docxtpl import DocxTemplate

from crispy_forms.layout import Layout, Div, Submit, Field, HTML
from crispy_forms.bootstrap import FormActions, PrependedText

from django.http import JsonResponse
import requests
import json
from lxml import html
import urllib.parse

import re  # для поиска целых чисел
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

import num2words

import locale
import os

from django.db.models import Q

import pandas as pd
from calendar import monthrange

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
# locale.setlocale(locale.LC_ALL, 'ru')

# TODO: проверить/удалить данную функцию

def index(request):
    template = 'panel.html'
    context = {'body': 'Стартовая страница'}

    return render(request, template, context)


def get_sudrf(request):
    """

    """

    headers_Get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    def get_kladr_code(city):
        s = requests.Session()
        q = city + ' site:kladr-rf.ru'
        q = '+'.join(q.split())
        url = 'https://www.google.com/search?q=' + q
        r = s.get(url, headers=headers_Get)
        tree = html.fromstring(r.content)
        list_link = tree.xpath('//div/div/div/a[contains(@href,"https://kladr-rf.ru/")]/@href')
        items_list_link = list_link[0].split('/')
        kladr_code = items_list_link[4]
        return kladr_code

    def get_sud_address(url):
        r = requests.get(url, headers=headers_Get)
        tree = html.fromstring(r.content)
        sud_adr = tree.xpath('//p[@id="court_address"]/text()')[0]
        return sud_adr

    def get_sudrf(court_subj, ms_city, ms_street):
        s = requests.Session()
        url = "https://sudrf.ru/index.php?id=300&act=go_ms_search&searchtype=ms&var=true&ms_type=ms&" \
              "court_subj=" + court_subj + "&" \
                                           "ms_city=" + urllib.parse.quote_plus(ms_city, safe='?&=',
                                                                                encoding='cp1251') + "&" \
                                                                                                     "ms_street=" + urllib.parse.quote_plus(
            ms_street, safe='?&=', encoding='cp1251')

        print(url)
        # url = "https://sudrf.ru/index.php?id=300&act=go_ms_search&searchtype=ms&var=true&ms_type=ms&" \
        #       "court_subj=38&" \
        #       "ms_city=%C8%F0%EA%F3%F2%F1%EA&" \
        #       "ms_street=%CB%E5%ED%E8%ED%E0"

        r = s.get(url, headers=headers_Get, verify=False)
        tree = html.fromstring(r.content)

        table_rows = tree.xpath('//table[@class="msSearchResultTbl msFullSearchResultTbl"]/tr')

        court_list = {}
        court_list['court'] = []

        for item in table_rows:
            sud_name = item.xpath('./td[1]/a/text()')
            sud_url = item.xpath('./td[1]/div//a/@href')
            sud_terr = item.xpath('./td[3]/text()')
            sud_comment = item.xpath('./td[4]/text()')
            court = {}
            if len(sud_name) > 0:
                court['name'] = sud_name[0]
                court['url'] = sud_url[0]
                court['terr'] = sud_terr[0]
                if len(sud_comment) > 0:
                    court['comment'] = sud_comment[0]
                else:
                    court['comment'] = ''
                court_list['court'].append(court)

        for i in range(len(court_list['court'])):
            address = get_sud_address(court_list['court'][i]['url'])
            court_list['court'][i].update({'address': address})

        return court_list

    if request.POST:
        results = list()
        print(request.POST)

        query = request.POST.get('member_id')
        member_list = query.split(',')
        # тут необходимо делать запросы в БД по member_id, для получения Города, Улицы

        agent = Members.objects.get(id=query)
        print(f'agent street - {agent.street}')
        ms_city = 'Новосибирск'
        ms_street = 'Ленина'

        court_subj = get_kladr_code(ms_city)
        print(f'court_subj - {court_subj}')

        response = get_sudrf(court_subj=court_subj, ms_city=ms_city, ms_street=ms_street)

        print(f'response {response}')
        # response = {'data': 'value'}

    else:
        response = {}

    return HttpResponse(json.dumps(response), content_type="application/json")


def result_multiform(request):
    template = 'result.html'

    if request.POST:
        body = request.POST
    else:
        body = 'POST запроса не было'
    context = {'body': body}

    return render(request, template, context)


#   СВОДКА
def summary(request):
    company = CompanyModel.objects.get(user_snt=request.user)
    debtors = MemberModel.objects.filter(company_id=company.id).values('id').aggregate(count=Count('id'))
    lands = LandModel.objects.filter(company_id=company.id).values('id').aggregate(count=Count('id'))

    pretrial = HistoryTemplate.objects.filter(member_id__company_id__user_snt=request.user).\
        filter(name_template='Претензия').values('id').aggregate(count=Count('id'))

    isk1 = HistoryTemplate.objects.filter(member_id__company_id__user_snt=request.user).\
        filter(name_template='Исковое заявление').values('id').aggregate(count=Count('id'))

    isk2 = HistoryTemplate.objects.filter(member_id__company_id__user_snt=request.user).\
        filter(name_template='Судебный приказ').values('id').aggregate(count=Count('id'))

    dataset = MemberModel.objects.filter(company_id=company.id).filter(lands__debtsmodel__sum__gte=0).\
        values('pk', 'lands__debtsmodel').annotate(Sum('lands__debtsmodel__sum'))

    amount_debt = 0
    for item in dataset:
        response = get_debit_info(item['lands__debtsmodel'], company.id)
        item['lands__debtsmodel__sum__sum'] = response['total_accruals'] + response['total_penalties']
        amount_debt += int(item['lands__debtsmodel__sum__sum'])

    print(f'amount_debt - {amount_debt}')

    context = {
        'debtors': debtors,
        'lands': lands,
        'amount_debt': amount_debt,
        'pretrial': pretrial,
        'isk1': isk1,
        'isk2': isk2,
    }

    return render(request, 'summary.html', context=context)


def get_file(filename):
    fl_path = MEDIA_ROOT + '/' + filename

    fl = open(fl_path, 'rb')
    mime_type, _ = mimetypes.guess_type(fl_path)
    response = HttpResponse(fl, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    # return response
    return redirect('app:result_multiform')


def download_file(request, filename=''):
    if filename != '':
        # fill these variables with real values
        # filename = 'isk_print.docx'
        fl_path = MEDIA_ROOT + '/' + filename

        fl = open(fl_path, 'rb')
        mime_type, _ = mimetypes.guess_type(fl_path)
        response = HttpResponse(fl, content_type=mime_type)
        response['Content-Disposition'] = "attachment; filename=%s" % filename
        return response
    else:
        template = 'file.html'
        return render(request, template)


# это для pretrial_tmp
def debtors_list(request):
    list_members = []
    dataset = dict.fromkeys(['id', 'members', 'lands', 'summa'])

    company = CompanyModel.objects.get(user_snt=request.user)
    members = MemberModel.objects.filter(company_id__user_snt=request.user)

    for item in members:
        dataset['id'] = item.pk
        dataset['members'] = item.second_name + ' ' + item.first_name + ' ' + item.third_name

        land_fields = item.lands.all()
        list = []
        for row in land_fields:
            list.append(row.land_address)
        dataset['lands'] = list

        ids = DebtsModel.objects.filter(land__in=land_fields).values('id')
        dataset['summa'] = 0
        for item in ids:
            if len(item) > 1:
                # print(f'Количество задолженностей больше одной! :: {item}')
                # dataset['summa'] = 0
                for id in item:
                    result = get_debit_info(id['id'], company.id)
                    dataset['summa'] += result['total_accruals'] - result['total_payments'] + result['total_penalties']
            elif len(item) == 1:
                # print(f'Количество задолженностей равно одной! :: {item["id"]}')
                result = get_debit_info(item['id'], company.id)
                dataset['summa'] = result['total_accruals'] - result['total_payments'] + result['total_penalties']
            else:
                # print(f'Нет ни одной задолженности! :: {item}')
                dataset['summa'] = 0

        buff = dataset.copy()
        list_members.append(buff)

    template = 'pretrial_tmp.html'
    context = {
        'header': 'Досудебная претензия',
        'dataset': list_members,
    }
    return render(request, template, context)


# это для isk_tmp_first
def debtors_list_2(request):
    list_members = []
    dataset = dict.fromkeys(['id', 'members', 'lands', 'summa'])

    company = CompanyModel.objects.get(user_snt=request.user)
    members = MemberModel.objects.filter(company_id__user_snt=request.user)

    # land = LandModel.objects.get(pk=item.land_id)
    # dataset['lands'] = land.land_address
    # dataset['members'] = list(land.members.all())
    for item in members:
        dataset['id'] = item.pk
        dataset['members'] = item.second_name + ' ' + item.first_name + ' ' + item.third_name
        land_fields = item.lands.all()
        dataset['lands'] = land_fields.values()
        # debits = DebtsModel.objects.filter(land__in=land_fields).aggregate(Sum('sum')).get('sum__sum', 0.00)
        # dataset['summa'] = DebtsModel.objects.filter(land__in=land_fields).aggregate(Sum('sum'))['sum__sum']

        ids = DebtsModel.objects.filter(land__in=land_fields).values('id')
        dataset['summa'] = 0
        for item in ids:
            if len(item) > 1:
                # print(f'Количество задолженностей больше одной! :: {item}')
                dataset['summa'] = 0
                for id in item:
                    result = get_debit_info(id['id'], company.id)
                    dataset['summa'] += result['total_accruals'] - result['total_payments'] + result['total_penalties']
            elif len(item) == 1:
                # print(f'Количество задолженностей равно одной! :: {item["id"]}')
                result = get_debit_info(item['id'], company.id)
                dataset['summa'] = result['total_accruals'] - result['total_payments'] + result['total_penalties']
                # print(f'result - {result}')
            else:
                # print(f'Нет ни одной задолженности! :: {item}')
                dataset['summa'] = 0

        buff = dataset.copy()
        if dataset['summa'] > 0:
            list_members.append(buff)

    template = 'isk_tmp.html'
    context = {
        'header': 'Судебное взыскание',
        # 'header': 'Исковое заявление',
        'dataset': list_members,
    }
    return render(request, template, context)


def pretrial_tmp(request):
    print(f'Создаем шаблон Претензии. Пришли следующие параметры: {request.POST}')
    if request.POST:
        member_id = request.POST.get('ownership')   # переименовать ownership в member_id
        member = MemberModel.objects.get(pk=member_id)

        if (len(member.series_number_doc) < 14)\
                or (len(member.issued) < 10 or 'удалось' in member.issued)\
                or (len(member.division_code) < 7)\
                or (member.date_of_issue is None):
            member_doc = ''
        else:
            member_doc = 'Паспорт: ' + member.series_number_doc + '. Выдан - ' + member.issued + '. Код подразделения - ' \
                     + member.division_code + '. Дата выдачи: ' + member.date_of_issue.strftime('%d-%m-%Y')

        if (member.date_of_birth is None) or (len(member.place_of_birth) < 1):
            member_birth = ''
        else:
            member_birth = 'Дата и место рождения: ' + member.date_of_birth.strftime('%d-%m-%Y') + ', ' + \
                       member.place_of_birth

        note = 'Иными сведениями заявитель не располагает.'

        # Участки
        land = member.lands.values().all()

        # Задолженности
        debit = DebtsModel.objects.filter(land__in=member.lands.all()).values('start_debt', 'end_debt', 'sum',
                                                                              'land__land_address',
                                                                              'land__kadastr_number', 'land__number')
        total = 0
        for item in debit:
            total = total + float(item['sum'])
        total_text = num2words.num2words(total, lang='ru', to='currency', currency='RUB')

        # Делаем корректировку на конечную дату
        if debit[len(debit)-1]['end_debt'] is None:
            end_debit = datetime.now().date()
        else:
            end_debit = debit[len(debit)-1]['end_debt']

        debit_for_template = {
            'start_debt': debit[0]['start_debt'],
            'end_debt': end_debit,
            'amount_debt': total,
            'amount_debt_text': total_text,
        }

        penalty = PenaltyCalculationModel.objects.filter(debt__land__members=member)
        total_penalty = 0
        for item in penalty:
            # print(f'- {item.pk} :: {item.rate} :: {item.sum} :: {item.sum_edit} :: {item.debt}')
            total_penalty += item.sum
            penalty_end_day = item.debt
        total_penalty_text = num2words.num2words(total_penalty, lang='ru', to='currency', currency='RUB')
        buff = str(penalty_end_day).split(' - ')
        penalty_start_day = datetime.strptime(buff[0], '%Y-%m-%d').date()
        if buff[1] == 'None':
            penalty_end_day = datetime.now().date()
        else:
            penalty_end_day = datetime.strptime(buff[1], '%Y-%m-%d').date()

        protocol = MembersFeeModel.objects.filter(company_id__user_snt=request.user).values()
        for item in protocol:
            # print(f'item - {item}')
            item['amount_fee_text'] = num2words.num2words(item['amount_fee'], lang='ru', to='currency', currency='RUB')

        company = CompanyModel.objects.get(user_snt=request.user)
        bank = BankModel.objects.get(company_id=company.id)

        # место где находятся шаблоны
        base_url = MEDIA_ROOT + '/template/'

        if member.status == '0':
            assert_url = base_url + 'PretrialTemplateMemberFalse.docx'  # Шаблон Претензия (для НЕ члена товарищества)
        else:
            assert_url = base_url + 'PretrialTemplateMemberTrue.docx'  # Шаблон Претензия (для члена товарищества)
        tpl = DocxTemplate(assert_url)

        fio = member.second_name + ' ' + member.first_name + ' ' + member.third_name
        data = {
            'member_name': fio,
            'member_address': member.address,
            'member_doc': member_doc,
            'member_birth': member_birth,
            'note': note,

            'land': land,
            'company_name': company.company_name,
            'protocol': protocol,
            'debit': debit_for_template,

            'penalties': total_penalty,
            'penalties_text': total_penalty_text,
            'penalties_date': penalty_end_day,


            'bank_name': bank.bank_name,
            'bank_bik': bank.bik_bank,
            'bank_inn': bank.inn_bank,
            'bank_kpp': bank.kpp,
            'bank_ogrn': 'его нет в форме ((',
            'bank_correspondent_acc': bank.correspondent_acc,
            'bank_payment_acc': bank.checking_acc,

            'company_contact': company.phone,
            'fio_manager': company.fio_manager,
        }

        tpl.render(data)

        line = fio.split(' ')

        c = HistoryTemplate.objects.filter(member_id__company_id__user_snt=request.user).filter(member_id=member.id)\
            .filter(name_template='Претензия').values('id').aggregate(count=Count('id'))
        v = int(c['count']) + 1
        # Иванов И.И.(Претензия)
        filename = line[0] + ' ' + line[1][0] + '. ' + line[2][0] + '. ' + '(Претензия)_v' + str(v) + '.docx'

        directory = str(company.id)
        path = os.path.join(settings.MEDIA_ROOT, directory)
        if not os.path.exists(path):
            os.mkdir(path)

        directory = str(company.id) + '/' + str(member.id)
        path = os.path.join(settings.MEDIA_ROOT, directory)
        if not os.path.exists(path):
            os.mkdir(path)

        path_template = str(company.id) + '/' + str(member.id) + '/' + filename
        # path_template = os.path.join(str(member.id), filename)
        print(f'path_template - {path_template}')
        tpl.save(MEDIA_ROOT + '/' + path_template)

        HistoryTemplate.objects.create(
            date_template=datetime.now(),
            name_template='Претензия',
            file_template=path_template,
            member_id=member
        )

    # Если ничего не выбрано в "Досудебной претензии" переходим на Историю документов
    # По идеи надо сделать сообщение об ошибке
    return render(request, 'history_tmp.html')


def get_land_for_member(request):
    print(f'POST request - {request.POST}')
    dataset = LandModel.objects.filter(member_id=request.POST.get('member_id')).values()
    print(f'dataset response land - {dataset}')
    return JsonResponse({'data': list(dataset)}, content_type="application/json")


# Исковое заявления
def isk_tmp_first(request):
    print(f'Исковое заявление.')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    if request.POST:
        if request.POST.get('process') == '1':
            print(f'Обрабатываем субъкт Москва - суды общей юрисдикции')
            # print(f'request - {request.POST}')
            tribunal_name = request.POST.get('court_name')
            tribunal_address = request.POST.get('court_address')
        elif request.POST.get('process') == '2':
            print(f'Обрабатываем обл Московская - суды общей юрисдикции')
            tribunal_name = request.POST.get('court_name')
            tribunal_address = request.POST.get('court_address')
        elif request.POST.get('process') == '3':
            print(f'Обрабатываем субъект Москва - мировые судьи')
            print(f'request - {request.POST}')
            # court = CourtMoscow.objects.get(id_court=request.POST.get('court_id'))
            tribunal_name = request.POST.get('court_name')
            tribunal_address = request.POST.get('court_address')
        elif request.POST.get('process') == '4':
            print(f'Обрабатываем обл Московская - мировые судьи')
            # print(f'request - {request.POST}')
            # url = request.POST.get('court_url')
            # ss = requests.Session()
            # rsp = ss.get(url, headers=headers)
            # tree = html.fromstring(rsp.content)
            # address = tree.xpath('//p[@id="court_address"]/text()')[0]
            tribunal_name = request.POST.get('court_name')
            tribunal_address = request.POST.get('court_address')
        else:
            print(f'request.POST.get process - пришло что-то непонятное')
            print(request.POST)
            tribunal_name = ''
            tribunal_address = ''

        member_id = request.POST.get('member_id')
        member = MemberModel.objects.get(pk=member_id)

        if (len(member.series_number_doc) < 14)\
                or (len(member.issued) < 10 or 'удалось' in member.issued)\
                or (len(member.division_code) < 7)\
                or (member.date_of_issue is None):
            member_doc = ''
        else:
            member_doc = 'Паспорт: ' + member.series_number_doc + '. Выдан - ' + member.issued + '. Код подразделения - ' \
                     + member.division_code + '. Дата выдачи: ' + member.date_of_issue.strftime('%d-%m-%Y')

        if (member.date_of_birth is None) or (len(member.place_of_birth) < 1):
            member_birth = ''
        else:
            member_birth = 'Дата и место рождения: ' + member.date_of_birth.strftime('%d-%m-%Y') + ', ' + \
                       member.place_of_birth

        note = 'Иными сведениями заявитель не располагает.'

        company = CompanyModel.objects.get(id=member.company_id_id)
        agent = AgentModel.objects.get(company_id=company.pk)

        land = member.lands.all().values()

        debit = DebtsModel.objects.filter(land__in=member.lands.all()).values('start_debt', 'end_debt', 'sum',
                                                                              'land__land_address',
                                                                              'land__kadastr_number', 'land__number')

        # print(f'debit - {list(debit)}')
        total_debit = 0
        for item in debit:
            # Делаем корректировку на конечную дату
            if item['end_debt'] is None:
                item['end_debt'] = datetime.now().date()

            item['sum_text'] = num2words.num2words(item['sum'], lang='ru', to='currency', currency='RUB')
            total_debit = total_debit + float(item['sum'])
        total_debit_text = num2words.num2words(total_debit, lang='ru', to='currency', currency='RUB')
        # print(f'debit new - {list(debit)}')
        # print(f'total - {total_debit}')
        # total_text = num2words.num2words(total, lang='ru', to='currency', currency='RUB')

        penalty = PenaltyCalculationModel.objects.filter(debt__land__members=member)
        total_penalty = 0
        for item in penalty:
            print(f'- {item.pk} :: {item.rate} :: {item.sum} :: {item.sum_edit} :: {item.debt}')
            total_penalty += item.sum
            penalty_end_day = item.debt

        total_penalty_text = num2words.num2words(total_penalty, lang='ru', to='currency', currency='RUB')
        buff = str(penalty_end_day).split(' - ')
        penalty_start_day = datetime.strptime(buff[0], '%Y-%m-%d').date()
        if buff[1] == 'None':
            penalty_end_day = datetime.now().date()
        else:
            penalty_end_day = datetime.strptime(buff[1], '%Y-%m-%d').date()

        all_price = float(total_penalty) + float(total_debit)

        duty = state_duty(all_price)
        duty_text = num2words.num2words(duty, lang='ru', to='currency', currency='RUB')

        protocol = MembersFeeModel.objects.filter(company_id__user_snt=request.user).values()

        for item in protocol:
            print(f'item - {item}')
            item['amount_fee_text'] = num2words.num2words(item['amount_fee'], lang='ru', to='currency', currency='RUB')

        base_url = MEDIA_ROOT + '/template/'

        if member.status == '0':
            assert_url = base_url + 'JudicialTemplateMemberFalse.docx'
        else:
            assert_url = base_url + 'JudicialTemplateMemberTrue.docx'

        tpl = DocxTemplate(assert_url)

        agent_fio = agent.second_name + ' ' + agent.first_name + ' ' + agent.third_name
        member_fio = member.second_name + ' ' + member.first_name + ' ' + member.third_name
        text = {
            'tribunal_name': tribunal_name,
            'tribunal_address': tribunal_address,

            'company_name': company.company_name,
            'company_inn': company.company_inn,
            'company_ogrn': company.company_ogrn,
            'company_address': company.full_address,

            'protocol': protocol,

            'company_agent_name': agent_fio,
            'company_agent_address': agent.address,
            'company_agent_phone': agent.phone,

            'member_name': member_fio,
            'member_address': member.address,
            'member_doc': member_doc,
            'member_birth': member_birth,
            'note': note,
            
            'land': land,
            'debit': debit,
            'total_debit': total_debit,
            'total_debit_text': total_debit_text,

            'penalties': total_penalty,
            'penalties_text': total_penalty_text,
            'penalty_start_day': penalty_start_day,
            'penalty_end_day': penalty_end_day,

            # 'amount_debt': summa,
            # 'amount_debt_text': num2words.num2words(summa, lang='ru', to='currency', currency='RUB'),
            # 'start_debt': debit.start_debt.strftime('%-d %B %Y') + ' года',
            # 'end_debt': debit.end_debt.strftime('%-d %B %Y') + ' года',

            'cost': float(total_debit) + float(total_penalty),

            'duty': duty,
            'duty_text': duty_text,
        }

        tpl.render(text)
        line = member_fio.split(' ')

        c = HistoryTemplate.objects.filter(member_id__company_id__user_snt=request.user).filter(member_id=member.id)\
            .filter(name_template='Исковое заявление').values('id').aggregate(count=Count('id'))
        v = int(c['count']) + 1

        # Иванов И.И.(Исковое заявление)
        filename = line[0] + ' ' + line[1][0] + '. ' + line[2][0] + '. ' + '(Исковое заявление)_v' + str(v) + '.docx'

        directory = str(company.id) + '/' + str(member.id)
        path = os.path.join(settings.MEDIA_ROOT, directory)
        if not os.path.exists(path):
            os.mkdir(path)

        path_template = str(company.id) + '/' + str(member.id) + '/' + filename
        tpl.save(MEDIA_ROOT + '/' + path_template)

        HistoryTemplate.objects.create(
            date_template=datetime.now(),
            name_template='Исковое заявление',
            file_template=path_template,
            member_id=member
        )
        return redirect('app:history_tmp')

    return redirect('app:history_tmp')


def state_duty(credit_sum):
    """
    до 20 000 рублей - 4 процента цены иска, но не менее 400 рублей;
    от 20 001 рубля до 100 000 рублей - 800 рублей плюс 3 процента суммы;
    от 100 001 рубля до 200 000 рублей - 3 200 рублей плюс 2 процента суммы;
    от 200 001 рубля до 1 000 000 рублей - 5 200 рублей плюс 1 процент суммы;
    свыше 1 000 000 рублей - 13 200 рублей плюс 0,5 процента суммы, но не более 60 000 рублей;
    :param credit_sum:
    :return: величина госпошлины
    """
    if not credit_sum > 20000:
        duty = credit_sum * 4 / 100
        if not duty > 400:
            duty = 400
    elif credit_sum > 20000 and not credit_sum > 100000:
        duty = 800 + (credit_sum - 20000) * 3 / 100
    elif credit_sum > 100000 and not credit_sum > 200000:
        duty = 3200 + (credit_sum - 100000) * 2 / 100
    elif credit_sum > 200000 and not credit_sum > 1000000:
        duty = 5200 + (credit_sum - 200000) * 1 / 100
    else:
        duty = 13200 + (credit_sum - 1000000) * 0.5 / 100
        if duty > 60000:
            duty = 60000
    return round(duty, 2)


def state_penalty(rate, credit):
    duration = credit.date_finish - credit.date_start
    days = duration.days

    if rate == 0:
        list_rate = []
        penalty_rate = KeyRate.objects.filter(date__range=(credit.date_start, credit.date_finish)) \
            .values('date', 'rate')
        # определяем первый элемент
        if credit.date_start == penalty_rate[0]['date']:
            list_rate.append({
                'date': penalty_rate[0]['date'],
                'rate': penalty_rate[0]['rate']
            })
            n = penalty_rate[0]['rate']
        else:
            prev_rate = KeyRate.objects.filter(date__lt=penalty_rate[0]['date']).order_by('-date')[0]
            list_rate.append({
                'date': credit.date_start,
                'rate': prev_rate.rate
            })
            n = prev_rate.rate

        # определяем середину
        for item in penalty_rate:
            if item['rate'] != n:
                list_rate.append({
                    'date': item['date'],
                    'rate': item['rate']
                })
                n = item['rate']

        i = len(penalty_rate)
        list_rate.append({
            'date': credit.date_finish,
            'rate': penalty_rate[i - 1]['rate']
        })

        finish_rate = []
        for i in range(1, len(list_rate)):
            duration = list_rate[i]['date'] - list_rate[i - 1]['date']
            print(f'count days - {duration.days}')
            finish_rate.append({
                'date': list_rate[i - 1]['date'],
                'rate': list_rate[i - 1]['rate'],
                'duraction': duration.days,
                'sum': round(credit.summa * (float(list_rate[i - 1]['rate']) / 100) * duration.days / 365, 2)
            })

        finish_rate.append({
            'date': list_rate[-1]['date'],
            'rate': list_rate[-1]['rate'],
            'duraction': 1,
            'sum': round(credit.summa * (float(list_rate[-1]['rate']) / 100) * 1 / 365, 2)
        })

        penalty = 0
        for item in finish_rate:
            penalty = penalty + item['sum']
    else:
        penalty = round(credit.summa * (rate / 100) * days, 2)

    return penalty


# Шаблон заявления на судебный приказ
def isk_tmp_second(request):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    header_html = 'Заявление на судебный приказ'

    if request.POST:
        if request.POST.get('process') == '3':
            print(f'Обрабатываем субъект Москва - мировые судьи')
            print(f'request - {request.POST}')
            court = CourtMoscow.objects.get(id_court=request.POST.get('court_id'))
            tribunal_name = court.short_name
            tribunal_address = court.address
        elif request.POST.get('process') == '4':
            print(f'Обрабатываем обл Московская - мировые судьи')
            # url = request.POST.get('court_url')
            # ss = requests.Session()
            # rsp = ss.get(url, headers=headers)
            # tree = html.fromstring(rsp.content)
            # address = tree.xpath('//p[@id="court_address"]/text()')[0]
            tribunal_name = request.POST.get('court_name')
            tribunal_address = request.POST.get('court_address')
        else:
            print(f'request.POST.get process - пришло что-то непонятное')
            print(request.POST)
            tribunal_name = request.POST.get('court_name')
            tribunal_address = request.POST.get('court_address')

        member_id = request.POST.get('member_id')
        member = MemberModel.objects.get(pk=member_id)

        if (len(member.series_number_doc) < 14)\
                or (len(member.issued) < 10 or 'удалось' in member.issued)\
                or (len(member.division_code) < 7)\
                or (member.date_of_issue is None):
            member_doc = ''
        else:
            member_doc = 'Паспорт: ' + member.series_number_doc + '. Выдан - ' + member.issued + '. Код подразделения - ' \
                     + member.division_code + '. Дата выдачи: ' + member.date_of_issue.strftime('%d-%m-%Y')

        if (member.date_of_birth is None) or (len(member.place_of_birth) < 1):
            member_birth = ''
        else:
            member_birth = 'Дата и место рождения: ' + member.date_of_birth.strftime('%d-%m-%Y') + ', ' + \
                       member.place_of_birth

        note = 'Иными сведениями заявитель не располагает.'

        company = CompanyModel.objects.get(id=member.company_id_id)
        agent = AgentModel.objects.get(company_id=company.pk)

        land = member.lands.all().values()

        debit = DebtsModel.objects.filter(land__in=member.lands.all()).values('start_debt', 'end_debt', 'sum',
                                                                              'land__land_address',
                                                                              'land__kadastr_number', 'land__number')

        print(f'debit - {list(debit)}')
        total_debit = 0
        for item in debit:
            # Делаем корректировку на конечную дату
            if item['end_debt'] is None:
                item['end_debt'] = datetime.now().date()

            item['sum_text'] = num2words.num2words(item['sum'], lang='ru', to='currency', currency='RUB')
            total_debit = total_debit + float(item['sum'])
        total_debit_text = num2words.num2words(total_debit, lang='ru', to='currency', currency='RUB')
        print(f'debit new - {list(debit)}')
        print(f'total - {total_debit}')
        # total_text = num2words.num2words(total, lang='ru', to='currency', currency='RUB')

        penalty = PenaltyCalculationModel.objects.filter(debt__land__members=member)
        total_penalty = 0
        for item in penalty:
            # print(f'- {item.pk} :: {item.rate} :: {item.sum} :: {item.sum_edit} :: {item.debt}')
            total_penalty += item.sum
            penalty_end_day = item.debt
        total_penalty_text = num2words.num2words(total_penalty, lang='ru', to='currency', currency='RUB')
        buff = str(penalty_end_day).split(' - ')
        penalty_start_day = datetime.strptime(buff[0], '%Y-%m-%d').date()

        if buff[1] == 'None':
            penalty_end_day = datetime.now().date()
        else:
            penalty_end_day = datetime.strptime(buff[1], '%Y-%m-%d').date()

        all_price = (float(total_penalty) + float(total_debit))*0.5

        duty = state_duty(all_price)
        duty_text = num2words.num2words(duty, lang='ru', to='currency', currency='RUB')

        protocol = MembersFeeModel.objects.filter(company_id__user_snt=request.user).values()

        for item in protocol:
            print(f'item - {item}')
            item['amount_fee_text'] = num2words.num2words(item['amount_fee'], lang='ru', to='currency', currency='RUB')

        base_url = MEDIA_ROOT + '/template/'
        if member.status == '0':
            assert_url = base_url + 'CourtOrderTemplateMemberFalse.docx'
        else:
            assert_url = base_url + 'CourtOrderTemplateMemberTrue.docx'

        tpl = DocxTemplate(assert_url)

        agent_fio = agent.second_name + ' ' + agent.first_name + ' ' + agent.third_name
        member_fio = member.second_name + ' ' + member.first_name + ' ' + member.third_name
        text = {
            'tribunal_name': tribunal_name,
            'tribunal_address': tribunal_address,

            'company_name': company.company_name,
            'company_inn': company.company_inn,
            'company_ogrn': company.company_ogrn,
            'company_address': company.full_address,

            'protocol': protocol,

            'company_agent_name': agent_fio,
            'company_agent_address': agent.address,
            'company_agent_phone': agent.phone,

            'member_name': member_fio,
            'member_address': member.address,
            'member_doc': member_doc,
            'member_birth': member_birth,
            'note': note,

            'land': land,
            'debit': debit,
            'total_debit': total_debit,
            'total_debit_text': total_debit_text,

            'penalties': total_penalty,
            'penalties_text': total_penalty_text,
            'penalty_start_day': penalty_start_day,
            'penalty_end_day': penalty_end_day,

            # 'amount_debt': summa,
            # 'amount_debt_text': num2words.num2words(summa, lang='ru', to='currency', currency='RUB'),
            # 'start_debt': debit.start_debt.strftime('%-d %B %Y') + ' года',
            # 'end_debt': debit.end_debt.strftime('%-d %B %Y') + ' года',

            'cost': float(total_debit) + float(total_penalty),

            'duty': duty,
            'duty_text': duty_text,
        }

        tpl.render(text)

        line = member_fio.split(' ')
        c = HistoryTemplate.objects.filter(member_id__company_id__user_snt=request.user).filter(member_id=member.id)\
            .filter(name_template='Судебный приказ').values('id').aggregate(count=Count('id'))
        v = int(c['count']) + 1

        # Иванов И.И.(Заявление о выдаче судебного приказа)
        filename = line[0] + ' ' + line[1][0] + '. ' + line[2][0] + '. ' + '(Заявление на судебный приказ)_v' + str(v) + '.docx'
        directory = str(company.id) + '/' + str(member.id)
        path = os.path.join(settings.MEDIA_ROOT, directory)
        if not os.path.exists(path):
            os.mkdir(path)

        path_template = str(company.id) + '/' + str(member.id) + '/' + filename
        # path_template = os.path.join(str(member.id), filename)
        # print(f'path_template - {path_template}')
        tpl.save(MEDIA_ROOT + '/' + path_template)

        HistoryTemplate.objects.create(
            date_template=datetime.now(),
            name_template='Судебный приказ',
            file_template=path_template,
            member_id=member
        )

        return redirect('app:history_tmp')

    return redirect('app:history_tmp')

    # else:
    #     company = CompanyModel.objects.get(user_snt=request.user)
    #     dataset = MemberModel.objects.filter(company_id=company.id, credits__isnull=False).values(
    #         'id', 'fio', 'phone', 'address', 'credits__summa')
    #
    #     context = {
    #         'members': dataset,
    #         'header': header_html,
    #     }
    #     return render(request, 'isk_tmp.html', context)


def history_tmp(request):
    history = HistoryTemplate.objects.filter(member_id__company_id__user_snt=request.user).\
        values('member_id', 'member_id__first_name', 'member_id__second_name', 'member_id__third_name').distinct()
    for item in history:
        file_template = HistoryTemplate.objects.filter(member_id=item['member_id']).values('date_template', 'file_template', 'name_template')

        for elem in file_template:
            filename = str(elem['file_template']).split('/')[-1]
            elem['filename'] = filename

        item['file_template'] = list(file_template)

    ustav = dict()
    ogrn = dict()
    inn = dict()
    yegryul = dict()

    scans = ScanCompanyModel.objects.filter(company_id__user_snt=request.user)
    if scans.exists():

        scans = ScanCompanyModel.objects.get(company_id__user_snt=request.user)

        if scans.ustav != '':
            ustav['path'] = scans.ustav
            ustav['filename'] = str(scans.ustav).split('/')[-1]
        if scans.ogrn != '':
            ogrn['path'] = scans.ogrn
            ogrn['filename'] = str(scans.ogrn).split('/')[-1]
        if scans.inn != '':
            inn['path'] = scans.inn
            inn['filename'] = str(scans.inn).split('/')[-1]
        if scans.yegryul != '':
            yegryul['path'] = scans.yegryul
            yegryul['filename'] = str(scans.yegryul).split('/')[-1]

    attachments = MembersFeeModel.objects.filter(company_id__user_snt=request.user).values('attachment')
    print(f'attachments - {attachments}')

    fee_doc = []
    for item in attachments:
        if item['attachment'] != '':
            f = dict()
            f['path'] = item['attachment']
            f['filename'] = str(item['attachment']).split('/')[-1]
            fee_doc.append(f)


    context = {
        'history': history,
        'ustav': ustav,
        'ogrn': ogrn,
        'inn': inn,
        'yegryul': yegryul,
        'fee_doc': fee_doc
    }

    return render(request, 'history_tmp.html', context=context)


def main_tab(request):
    from crispy_forms.layout import Submit
    from crispy_forms.bootstrap import FormActions

    def get_dadata(inn):
        token = '8e395d15a1206b762e59b997136d82763480a33e'
        dadata = Dadata(token)
        result = dadata.find_by_id('party', inn)
        result = dict(ChainMap(*result))
        return result

    form_main = form_inn = None

    try:
        main_settings = CompanyModel.objects.get(user_snt=request.user)
    except CompanyModel.DoesNotExist:
        main_settings = None

    if main_settings is None:
        # События `fill_inn` и `save_main`, когда в БД нет информации о Компании.
        if 'fill_inn' in request.POST:
            form_inn = InputInnForm(request.POST)
            if form_inn.is_valid():
                result_inn = get_dadata(form_inn.cleaned_data['inn'])
                initial_dict = {
                    'fio_manager': result_inn['data']['management']['name'],
                    'company_name': result_inn['value'],
                    'company_inn': result_inn['data']['inn'],
                    'company_ogrn': result_inn['data']['ogrn'],
                    'full_company_name': result_inn['data']['name']['full_with_opf'],
                    'position_manager': result_inn['data']['management']['post'],
                    'full_address': result_inn['data']['address']['unrestricted_value']
                }
                form_main = MainSettingsForm(None, initial=initial_dict)

        elif 'save_main' in request.POST:
            form = MainSettingsForm(request.POST)
            if form.is_valid():
                data = form.save(commit=False)
                data.user_snt = request.user
                data.save()
                return HttpResponseRedirect(reverse('app:main_settings'))

        else:
            form_inn = InputInnForm()
            form_main = None
    else:
        # События `fill_inn` и `save_main`, когда в БД есть информация о Компании.
        if 'save_main' in request.POST:
            form = MainSettingsForm(request.POST, instance=request.user.companysettings)
            if form.is_valid():
                form.save(commit=False)
                form.save()
                return HttpResponseRedirect(reverse('app:main_settings'))

        elif 'edit_main' in request.POST:
            print('edit main')
            form_inn = InputInnForm()
            initial_dict = {
                'company_name': main_settings.company_name,
                'company_inn': main_settings.company_inn,
                'company_ogrn': main_settings.company_ogrn,
                'full_company_name': main_settings.full_company_name,
                'position_manager': main_settings.position_manager,
                'fio_manager': main_settings.fio_manager,
                'full_address': main_settings.full_address,
            }
            form_main = MainSettingsForm(None, initial=initial_dict)
            form_main.helper.layout[5] = FormActions(
                Submit('save_main', 'Сохранить', css_class="btn-primary pull-right"),
            )

        elif 'fill_inn' in request.POST:
            form_inn = InputInnForm(request.POST)
            if form_inn.is_valid():
                result_inn = get_dadata(form_inn.cleaned_data['inn'])
                initial_dict = {
                    'fio_manager': result_inn['data']['management']['name'],
                    'company_name': result_inn['value'],
                    'company_inn': result_inn['data']['inn'],
                    'company_ogrn': result_inn['data']['ogrn'],
                    'full_company_name': result_inn['data']['name']['full_with_opf'],
                    'position_manager': result_inn['data']['management']['post'],
                    'full_address': result_inn['data']['address']['unrestricted_value']
                }
                form_main = MainSettingsForm(None, initial=initial_dict)
                form_main.helper.layout[5] = FormActions(
                    Submit('save_main', 'Сохранить', css_class="btn-primary pull-right"),
                )
        else:
            form_inn = None
            initial_dict = {
                'company_name': main_settings.company_name,
                'company_inn': main_settings.company_inn,
                'company_ogrn': main_settings.company_ogrn,
                'full_company_name': main_settings.full_company_name,
                'position_manager': main_settings.position_manager,
                'fio_manager': main_settings.fio_manager,
                'full_address': main_settings.full_address,
            }
            form_main = MainSettingsForm(None, initial=initial_dict)
            form_main.fields['company_name'].disabled = True
            form_main.fields['company_inn'].disabled = True
            form_main.fields['company_ogrn'].disabled = True
            form_main.fields['full_company_name'].disabled = True
            form_main.fields['position_manager'].disabled = True
            form_main.fields['fio_manager'].disabled = True
            form_main.fields['full_address'].disabled = True
            form_main.helper.layout[5] = FormActions(
                Submit('edit_main', 'Редактировать', css_class="btn-primary pull-right"),
            )

    context = {
        'form_inn': form_inn,
        'form_main_settings': form_main,
    }

    return render(request, 'settings/main.html', context=context)


def bank_tab(request):
    from crispy_forms.layout import Submit
    from crispy_forms.bootstrap import FormActions

    form_bank = form_bik = None

    try:
        main_settings = CompanyModel.objects.get(user_snt=request.user)
        bank_settings = BankModel.objects.get(company_id=main_settings.id)
    except CompanyModel.DoesNotExist:
        bank_settings = None
    except BankModel.DoesNotExist:
        bank_settings = None

    if bank_settings is None:
        if 'fill_bik' in request.POST:
            form_bik = InputBikForm(request.POST)
            if form_bik.is_valid():
                bik = form_bik.cleaned_data['bik']
                token = '8e395d15a1206b762e59b997136d82763480a33e'
                dadata = Dadata(token)
                result_bik = dadata.find_by_id('bank', bik)
                # print(f'result bik - {result_bik}')
                result_bik = dict(ChainMap(*result_bik))

                initial_dict = {
                    'bank_name': result_bik['value'],
                    'bik': result_bik['data']['bic'],
                    'inn': result_bik['data']['inn'],
                    'kpp': result_bik['data']['kpp'],
                    'correspondent_acc': result_bik['data']['correspondent_account'],
                }
                form_bank = BankSettingsForm(initial=initial_dict)

        if 'save_bank' in request.POST:
            main_settings = CompanyModel.objects.get(user_snt=request.user)
            form = BankSettingsForm(request.POST)
            form.instance.company_id = main_settings
            if form.is_valid():
                data = form.save(commit=False)
                data.save()
                return HttpResponseRedirect(reverse('app:bank_settings'))

        else:
            form_bik = InputBikForm()
    else:
        print(f'data bank is ')
        if 'edit_bank' in request.POST:
            return HttpResponseRedirect(reverse('app:bank_settings'))
        else:
            form_bik = None
            initial_dict = {
                'bank_name': bank_settings.bank_name,
                'bik': bank_settings.bik,
                'inn': bank_settings.inn,
                'kpp': bank_settings.kpp,
                'correspondent_acc': bank_settings.correspondent_acc,
                'checking_acc': bank_settings.checking_acc,
            }
            form_bank = BankSettingsForm(initial=initial_dict)
            form_bank.fields['bank_name'].disabled = True
            form_bank.fields['bik'].disabled = True
            form_bank.fields['inn'].disabled = True
            form_bank.fields['kpp'].disabled = True
            form_bank.fields['correspondent_acc'].disabled = True
            form_bank.fields['checking_acc'].disabled = True

            form_bank.helper.layout[3] = FormActions(
                Submit('edit_bank', 'Редактировать', css_class="btn-primary pull-right"),
            )

    context = {
        'form_bik': form_bik,
        'form_bank_settings': form_bank,
    }

    return render(request, 'settings/bank.html', context=context)


def agent(request):
    try:
        main_settings = CompanyModel.objects.get(user_snt=request.user)
        agents = AgentModel.objects.filter(company_id=main_settings.id)
    except AgentModel.DoesNotExist:
        agents = None

    if agents is None:
        form_agent = AgentForm()

        if 'save_agent' in request.POST:
            main_settings = CompanyModel.objects.filter(user_snt=request.user)
            form = AgentForm(request.POST)
            form.instance.company_id = main_settings
            if form.is_valid():
                data = form.save(commit=False)
                data.save()
                return HttpResponseRedirect(reverse('app:agent_settings'))
    else:
        form_agent = None

    context = {
        'form_agent': form_agent,
        'agents': agents,
    }
    return render(request, 'settings/agent.html', context=context)


def issued(request):
    print(f'views issued - {request.POST}')
    dc = request.POST.get('division_code')

    token = '8e395d15a1206b762e59b997136d82763480a33e'
    dadata = Dadata(token)
    result = dadata.suggest('fms_unit', dc)
    result = dict(ChainMap(*result))

    if 'value' in result.keys():
        data = result['value']
        print(f"result - {result['value']}")
    else:
        data = 'Не удалось автоматически определить наименование подразделения.'

    return JsonResponse({'data': data}, status=200)

# ---------------------------

def land_create(request, id):
    member = get_object_or_404(MemberModel, id=id)
    form = LandsForm(request.POST or None)
    if form.is_valid():
        form.save(commit=False)
        form.instance.member_id = member
        form.save()
        return HttpResponseRedirect(reverse('app:member_detail', args=(id,)))

    context = {
        'form': form,
    }
    return render(request, 'land.html', context)


def land_update(request, id):
    land = get_object_or_404(LandModel, id=id)

    form = LandsForm(request.POST or None, instance=land)
    form.helper.layout[2] = FormActions(
        Submit('land_save', 'Сохранить', css_class="btn-primary pull-right"),
        Submit('land_del', 'Удалить', css_class="btn-primary pull-right mr-2"),
    )

    if 'land_save' in request.POST:
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('app:member_detail', args=(id,)))

    if 'land_del' in request.POST:
        land.delete()
        return HttpResponseRedirect(reverse('app:member_detail', args=(id,)))

    context = {
        'form': form,
    }
    return render(request, 'land.html', context)


def get_court(request):
    import json
    from app.models import CourtMoscow
    from django.contrib.gis.geos import GEOSGeometry

    headers_get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    url = 'https://mos-sud.ru/api/courts'
    # ss = requests.Session()
    # rsp = ss.get(url, headers=headers_get)
    rsp = requests.get(url, headers=headers_get, verify=False)
    courts = rsp.json()

    for item in courts:
        try:
            list_polygon = json.loads(item['polygonData'])
        except KeyError:
            print(f'У участка {item.get("fullName")} нет данных в поле - PolygonData \n'
                  f'В базу данная запись не попадет')
            continue

        if len(list_polygon) > 1:
            coordinates = '['
            for i in range(len(list_polygon)):
                coordinates += '[' + str(list_polygon[i]) + '],'
            coordinates = coordinates[:-1]
            coordinates += ']'
        else:
            coordinates = '[' + item['polygonData'] + ']'

        try:
            poly_data = GEOSGeometry('{ "type": "MultiPolygon", '
                                     '"coordinates": ' + coordinates + ' }', srid=4326)
        except Exception:
            print(f'Участок - {item.get("fullName")} без координат. Необходимо проверить данные полигона.')
            continue

        CourtMoscow.objects.create(
            id_court=item.get('id'),
            code=item.get('code'),
            number=item.get('number'),
            full_name=item.get('fullName'),
            polygon_data=poly_data,
            short_name=item.get('shortName'),
            address=item.get('address'),
            phones=item.get('phones'),
            phone_info=item.get('phoneInfo'),
            territorial_info=item.get('territorialInfo'),
            judge_fio=item.get('judgeFIO'),
            dinner_time=item.get('dinnerTime'),
            week_ends=item.get('weekEnds'),
            counsulting_hours=item.get('consultingHours'),
            business_hours=item.get('businessHours'),
            email=item.get('email'),
            court_latitude=item.get('latitude'),
            court_longitude=item.get('longitude')
        )

    return render(request, 'test/get_court.html', {'courts': courts})


def get_courts_moscow_region(request):
    headers_get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    url = 'https://sudrf.ru/index.php?id=300&act=podsud_search&searchtype=podsud&court_subj=50&fs_city=&fs_street='
    r = requests.get(url, headers=headers_get, verify=False)
    tree = html.fromstring(r.text)
    courts = tree.xpath('//div[@class="sud_info"]')

    for item in courts:
        sud_name = item.xpath('./div[@class="sud_name"]/text()')[0]
        sud_ter_name = item.xpath('./div[@class="sud_ter_name"]/text()')[0]
        code = item.xpath('./text()')[2]
        address = item.xpath('./text()')[3]
        phone = item.xpath('./text()')[4]
        email = item.xpath('./a/text()')[0]
        url = item.xpath('./div/a/text()')[0]
        print(f'{sud_name} : {sud_ter_name} : {code} : {address} : {phone} : {email} : {url}')

        CourtMoscowRegion.objects.create(
            short_name=sud_name,
            region_name=sud_ter_name,
            code=code,
            address=address,
            phones=phone,
            email=email,
            url=url
        )

    return render(request, 'test/get_court.html', {'courts': courts})


def find_court_for_first_tmp(request):
    import requests
    import json
    from lxml import html

    headers_get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    court_list = {
        'court': [],
    }

    def get_sud_address(url):
        r = requests.get(url, headers=headers_get)
        tree = html.fromstring(r.content)
        sud_adr = tree.xpath('//p[@id="court_address"]/text()')[0]
        return sud_adr

    if request.POST:
        print(f'find_court_for_first_tmp {request.POST}')
        member_id = request.POST.get('member_id')
        summa = request.POST.get('summa')
        summa = summa.replace(',', '.')

        member_data = MemberModel.objects.get(pk=member_id)
        print(f"Член товарищества --> {member_data.first_name} :: {member_data.second_name} :: {member_data.address}")
        # land_data = LandModel.objects.get(ownershipmodel=ownership_data)
        # print(f'Земельный участок --> {land_data.land_address}')

        # agent_id = request.POST.get('member_id')
        # agent = MemberModel.objects.get(id=agent_id)
        # land_id = request.POST.get('land_id')
        # credit = Credits.objects.get(id=land_id)
        address = member_data.address

        address_str = address.split(',')
        # address_str[0] - субъект РФ
        # address_str[1] - город РФ
        print(f'address str split - {address_str}')
        address_str = address_str[:-1]
        print(f'address_find - {str(address_str)}')
        address_find = ' '.join(address_str)

        if float(summa) > 50000:
            # суды общей юрисдикции
            if address_str[0].strip() == 'г Москва':
                print(f'мы обрабатываем субъект г Москва')
                print(f'agent address - {address.replace(",", "")}')
                search_address = address.replace(",", "")
                print(urllib.parse.quote_plus(search_address))
                # url = 'https://mos-gorsud.ru/territorial/getStreets?q='+search_address+'+&tid='
                city = address_str[0].lstrip().split(' ')
                street = address_str[1].lstrip().split(' ')
                num_house = address_str[2].lstrip().split(' ')
                print(f'city - street - num_house - {city, street, num_house}')
                search_address = city[1] + ' ' + street[1] + ' ' + num_house[1] # old version
                # search_address = address_str[1]
                print(f'search_address - {search_address}')
                print(f'address_find - {address_find}')
                print(urllib.parse.quote_plus(search_address))
                url = 'http://mos-gorsud.ru/territorial/getStreets?q=' + urllib.parse.quote_plus(search_address) + '+&tid='
                print(f'url contact - {url}')
                ss = requests.Session()
                rsp = ss.get(url, headers=headers_get, verify=True)
                print(f'rsp - {rsp.json()}')
                court = rsp.json()
                print(f'result - {court["result"][0]["court"]}')
                rsp = ss.post('https://mos-gorsud.ru/territorial/search',
                              data={'court': court["result"][0]["court"]},
                              headers=headers_get, verify=False)
                print(f'final fsp - {rsp.json()}')
                data = rsp.json()
                print(f'court address - {data["address"]}')

                court_list = {
                    'court': [],
                }

                court = {
                    'id_court': data['code'],
                    'short_name': data['fullName'],
                    'judge_fio': '',
                    'address': data['address'],
                    'phones': data['phones'],
                    'process': 1,
                }

                court_list['court'].append(court)

                # return HttpResponse(json.dumps(court_list), content_type="application/json")
                html = render_to_string("tmp_table/result_table_2.html", context={'courts': court_list})
                return HttpResponse(html)

            elif address_str[0].strip() == 'обл Московская':
                print(f'address - {address_str[1]}')
                adrs = address_str[1].split(' ')
                print(f'чистое название города - {adrs[2]}')

                queryset = CourtMoscowRegion.objects.filter(address__contains=adrs[2])
                court_list = {
                    'court': [],
                }

                for item in queryset:
                    court = {
                        'id_court': item.id,
                        'short_name': item.short_name,
                        'judge_fio': ' ',
                        'address': item.address,
                        'phones': item.phones,
                        'process': 2,
                    }

                    court_list['court'].append(court)

                # return HttpResponse(json.dumps(court_list), content_type="application/json")
                html = render_to_string("tmp_table/result_table_2.html", context={'courts': court_list})
                return HttpResponse(html)
            else:
                print(f'мы не сможем больше ничего обратать')

        else:
            if address_str[0].strip() == 'г Москва':
                print(f'Задолженность меньше 50000. г. Москва')
                apikey = '5a29bfa5-d882-4180-b6ab-3d50ebe1920b'
                url = 'https://geocode-maps.yandex.ru/1.x/?apikey=' + apikey + '&geocode=' + address

                ss = requests.Session()
                rsp = ss.get(url, headers=headers_get)

                tree = html.fromstring(rsp.content)
                pos = tree.xpath('//pos/text()')
                point = pos[0].split(' ')
                queryset = CourtMoscow.objects.filter(polygon_data__contains='POINT(' + point[1] + ' ' + point[0] + ')')

                court_list = {
                    'court': [],
                }

                for item in queryset:
                    court = {
                        'id_court': item.id_court,
                        'short_name': item.short_name,
                        'judge_fio': item.judge_fio,
                        'address': item.address,
                        'phones': item.phones,
                        'process': 3,
                    }

                    print(f'court - {court}')

                    court_list['court'].append(court)

                # return HttpResponse(json.dumps(court_list), content_type="application/json")
                html = render_to_string("tmp_table/result_table_2.html", context={'courts': court_list})
                return HttpResponse(html)

            elif address_str[0].strip() == 'обл Московская':
                print(f'Задолженность меньше 50000\n, Московская область\n, Мы ищем судебные участки мировых судей ... ')
                print(f'Адрес - {address_str}')

                ss = requests.Session()
                # url = 'https://sudrf.ru/'
                # rsp = ss.get(url, headers=headers_get, verify=False)
                # print(f'Ответ от sudrf.ru - {rsp.status_code}')
                city_str = ''
                if len(address_str[1]) > 0:
                    city = address_str[1].strip()
                    city_str = '&ms_city=' + urllib.parse.quote_plus(city, encoding='cp1251')

                street_str = ''
                if len(address_str[2]) > 0:
                    street = address_str[2].strip()
                    street_str = '&ms_street=' + urllib.parse.quote_plus(street, encoding='cp1251')

                url = 'https://sudrf.ru/index.php?id=300&act=go_ms_search&searchtype=ms&var=true&ms_type=ms' \
                      '&court_subj=50' + city_str + street_str

                print(f'url - {url}')
                rsp = ss.get(url, headers=headers_get, verify=False)
                print(f'Ответ от sudrf.ru - {rsp.status_code}')
                tree = html.fromstring(rsp.content)

                table_rows = tree.xpath('//table[@class="msSearchResultTbl msFullSearchResultTbl"]/tr')

                court_list = {'court': []}

                for item in table_rows:
                    sud_name = item.xpath('./td[1]/a/text()')
                    sud_url = item.xpath('./td[1]/div//a/@href')
                    sud_terr = item.xpath('./td[2]/text()')
                    sud_comment = item.xpath('./td[4]/text()')

                    print(f'sud_name - {sud_name}')
                    print(f'sud_url - {sud_url}')
                    print(f'sud_terr - {sud_terr}')
                    print(f'sud_comment - {sud_comment}')

                    court = {}
                    if len(sud_name) > 0:
                        court['short_name'] = sud_name[0]
                        court['url'] = sud_url[0]
                        # court['phone'] = ''
                        court['terr'] = sud_terr[0]
                        if len(sud_comment) > 0:
                            court['comment'] = sud_comment[0]
                        else:
                            court['comment'] = ''
                        court_list['court'].append(court)

                for i in range(len(court_list['court'])):
                    address = get_sud_address(court_list['court'][i]['url'])
                    court_list['court'][i].update({'address': address})
                    court_list['court'][i].update({'process': 4})

                print(f'court_list - {court_list}')


                # return HttpResponse(json.dumps(court_list), content_type="application/json")
                html = render_to_string("tmp_table/result_table_2.html", context={'courts': court_list})
                return HttpResponse(html)

            else:
                print(f'мы не сможем больше ничего обратать')


# скорее всего это копия верхней функции, но для чего она была сделана пока несовсем понятно
def find_court_for_second_tmp(request):
    headers_get = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    court_list = {
        'court': [],
    }

    def get_sud_address(url):
        r = requests.get(url, headers=headers_get)
        tree = html.fromstring(r.content)
        sud_adr = tree.xpath('//p[@id="court_address"]/text()')[0]
        return sud_adr

    if request.method == 'POST':
        print(f'find_court_for_second_tmp {request.POST}')
        # agent_id = request.POST.get('member_id')
        # agent = MemberModel.objects.get(id=agent_id)
        # land_id = request.POST.get('land_id')
        # credit = Credits.objects.get(id=land_id)

        address = 'г Москва, г Щербинка, ул 1-я Центральная, дом 1'

        address_str = address.split(',')
        # address_str[0] - субъект РФ
        # address_str[1] - город РФ
        print(f'address str split - {address_str[0]}')

        address_str = address.split(',')

        if address_str[0].strip() == 'г Москва':
            print(f'Мы ищем судебные участки мировых судей :: г Москва :: Заявление на судебное взыскание')
            apikey = '5a29bfa5-d882-4180-b6ab-3d50ebe1920b'

            ss = requests.Session()
            url = 'https://geocode-maps.yandex.ru/1.x/?apikey=' + apikey + '&geocode=' + address
            rsp = ss.get(url, headers=headers_get)
            tree = html.fromstring(rsp.content)
            pos = tree.xpath('//pos/text()')
            point = pos[0].split(' ')
            queryset = CourtMoscow.objects.filter(polygon_data__contains='POINT(' + point[1] + ' ' + point[0] + ')')

            court_list = {
                'court': [],
            }

            for item in queryset:
                court = {
                    'id_court': item.id_court,
                    'short_name': item.short_name,
                    'judge_fio': item.judge_fio,
                    'address': item.address,
                    'phones': item.phones,
                    'process': 3,
                }

                court_list['court'].append(court)

            return HttpResponse(json.dumps(court_list), content_type="application/json")

        elif address_str[0].strip() == 'обл Московская':
            print(f'Мы ищем судебные участки мировых судей :: Московская область :: Заявление на судебное взыскание')
            ss = requests.Session()

            buff = address_str[2].strip().split(' ')
            print(f'buff first - {buff}')
            if buff[0].strip() == 'д':
                print(f'buff - {buff}')
                print(f'buff[0] - {buff[0]}')
                print(f'buff[1] - {buff[1]}')
                city = buff[1].strip()
                # street = address_str[3].strip()
                street = ''
            else:
                city = address_str[1].strip()
                street = address_str[2].strip()

            url = 'https://sudrf.ru/index.php?id=300&act=go_ms_search&searchtype=ms&var=true&ms_type=ms' \
                  '&court_subj=50' \
                  '&ms_city=' + urllib.parse.quote_plus(city, encoding='cp1251') + \
                  '&ms_street=' + urllib.parse.quote_plus(street, encoding='cp1251')
            print(f'url - {url}')
            rsp = ss.get(url, headers=headers_get, verify=False)
            # print(f'response - {rsp.content}')
            tree = html.fromstring(rsp.text)

            table_rows = tree.xpath('//table[@class="msSearchResultTbl msFullSearchResultTbl"]/tr')

            court_list = {'court': []}

            for item in table_rows:
                sud_name = item.xpath('./td[1]/a/text()')
                sud_url = item.xpath('./td[1]/div//a/@href')
                # sud_terr = item.xpath('./td[3]/text()')
                sud_comment = item.xpath('./td[4]/text()')
                court = {}
                if len(sud_name) > 0:
                    court['short_name'] = sud_name[0]
                    court['url'] = sud_url[0]
                    court['terr'] = ''  # sud_terr[0]
                    if len(sud_comment) > 0:
                        court['comment'] = sud_comment[0]
                    else:
                        court['comment'] = ''
                    court_list['court'].append(court)

            for i in range(len(court_list['court'])):
                address = get_sud_address(court_list['court'][i]['url'])
                court_list['court'][i].update({'address': address})
                court_list['court'][i].update({'process': 4})

            print(f'court list - {court_list}')

            return HttpResponse(json.dumps(court_list), content_type="application/json")
        else:
            print(f'мы не сможем больше ничего обратать')


def protocol_create(request):
    err_msg = company = None
    try:
        company = CompanyModel.objects.get(user_snt=request.user)
    except CompanyModel.DoesNotExist:
        err_msg = 'Первым делом необходимо выполнить настройки Организации.'

    form = ProtocolForm(request.POST or None)
    form.instance.company_id = company
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('app:protocol_list'))
    context = {
        'form': form,
        'err_msg': err_msg,
    }
    return render(request, 'settings/protocol.html', context)


def protocol_update(request, id):
    obj = get_object_or_404(ProtocolModel, id=id)
    initial_dict = {
        'date_start': obj.date_start.strftime("%d.%m.%Y"),
        'date_finish': obj.date_finish.strftime("%d.%m.%Y"),
    }
    form = ProtocolForm(request.POST or None, instance=obj, initial=initial_dict)
    form.helper.layout[2] = FormActions(
        Submit('protocol_save', 'Сохранить', css_class="btn-primary pull-right"),
        Submit('protocol_del', 'Удалить', css_class="btn-primary pull-right mr-2"),
    )

    if 'protocol_del' in request.POST:
        obj.delete()
        return HttpResponseRedirect(reverse('app:protocol_list'))

    if 'protocol_save' in request.POST:
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('app:protocol_list'))

    context = {
        'form': form,
    }
    return render(request, 'settings/protocol.html', context)


def protocol_list(request):
    err_msg = None
    try:
        company = CompanyModel.objects.get(user_snt=request.user)
        dataset = ProtocolModel.objects.filter(company_id=company.id)
    except CompanyModel.DoesNotExist:
        dataset = None
        err_msg = 'Первым делом необходимо выполнить настройки Организации.'

    context = {
        'dataset': dataset,
        'err_msg': err_msg,
    }
    return render(request, 'settings/protocol.html', context)


def member_create(request):
    err_msg = company = None
    try:
        company = CompanyModel.objects.get(user_snt=request.user)
    except CompanyModel.DoesNotExist:
        err_msg = 'Первым делом необходимо выполнить настройки Организации.'

    form = MemberForm(request.POST or None)
    form.instance.company_id = company
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('app:member_list'))
    context = {
        'form': form,
        'err_msg': err_msg,
    }
    return render(request, 'settings/member.html', context)


# new function for (ajax method)
def member_add(request):
    company = CompanyModel.objects.get(user_snt=request.user)

    print(f'function member_add - {request.POST}')

    # TODO: Попробовать реализовать с помощью QueryDict
    #       https://docs.djangoproject.com/en/dev/ref/request-response/#django.http.QueryDict.getlist
    data_land = request.POST.getlist('lands[]')
    print(f'data_land - {data_land}')

    # post = request.POST.copy()
    # if 'status' in post:
    #     post['status'] = '1'
    # else:
    #     post['status'] = '0'
    # request.POST = post

    # если в запросе id_member - то это редактирование
    if request.POST.get('id_member'):
        print(f'Выполняем редактироввание члена товарищества')
        id = request.POST.get('id_member')
        member = MemberModel.objects.get(pk=id)


        form_member = MemberForm(request.POST, instance=member)
        form_member.instance.company_id_id = company.id
        if form_member.is_valid():
            form_member.status = int(request.POST.get('status'))
            form_member.save()
            for id in data_land:
                land = LandModel.objects.get(pk=id)
                land.members.add(member.pk)
                land.save()
        else:
            print(f'member edit form.errors {form_member.errors}')

        return HttpResponse(json.dumps({'response': 'ok'}), content_type="application/json")

    # TODO: пересмотреть написание функции
    #       добавление данных в связку ManyToMany
    form_member = MemberForm(request.POST)
    form_member.instance.company_id_id = company.id
    if form_member.is_valid():
        form_member.save()
        # таким образом сохраняем Членов товарищества без участка!
        if 'Нет участков в собственности' not in data_land:
            obj = MemberModel.objects.latest('id')
            for id in data_land:
                land = LandModel.objects.get(pk=id)
                land.members.add(obj.pk)
                land.save()
    # else:
    #     print(f'member add form.errors {form_member.errors}')
    return HttpResponseRedirect(reverse('app:member_list'))
    # return HttpResponse(json.dumps({'response': 'ok'}), content_type="application/json")


def member_detail(request, id):
    member = get_object_or_404(MemberModel, id=id)

    try:
        lands = LandModel.objects.filter(member_id=member.id)
        # lands = get_object_or_404(Lands, id=member)
    except LandModel.DoesNotExist:
        lands = None

    print(f'lands - {lands.values()}')

    try:
        credits = Credits.objects.filter(land_id__in=lands)
    except Credits.DoesNotExist:
        credits = None

    print(f'credits - {credits.values()}')

    context = {
        'member_detail': member,
        'lands': lands,
        'credits': credits,
    }

    # return render(request, 'settings/member_view.html', context=context)
    return render(request, 'settings/member.html', context)


def member_update(request, id):
    member = get_object_or_404(MemberModel, id=id)
    form = MemberForm(request.POST or None, instance=member)
    form.helper.layout[2] = FormActions(
        Submit('member_save', 'Сохранить', css_class="btn-primary pull-right"),
        Submit('member_del', 'Удалить', css_class="btn-primary pull-right mr-2"),
    )

    if 'member_del' in request.POST:
        member.delete()
        return HttpResponseRedirect(reverse('app:member_list'))

    if 'member_save' in request.POST:
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('app:member_list'))

    context = {
        'form': form,
    }
    return render(request, 'settings/member.html', context)


def member_list(request):
    try:
        company = CompanyModel.objects.get(user_snt=request.user)
        members = MemberModel.objects.filter(company_id=company.id)
        list_members = []
        dataset = dict.fromkeys(['id', 'members', 'lands'])

        for item in members:
            dataset['id'] = item.id
            dataset['members'] = item.second_name + ' ' + item.first_name + ' ' + item.third_name
            dataset['lands'] = list(item.lands.all())
            buff = dataset.copy()
            list_members.append(buff)

    except CompanyModel.DoesNotExist:
        list_members = None

    form_member = MemberForm(None)
    form_land = LandsForm(None)

    context = {
        'header': 'Физические лица',
        'dataset': list_members,
        'form_member': form_member,
        'form_land': form_land
    }
    return render(request, 'settings/member.html', context)


def member_del(request, id):
    MemberModel.objects.filter(pk=id).delete()
    return JsonResponse({'data': 'Member deleted'}, status=200)


def credit_create(request, id):
    member = get_object_or_404(MemberModel, id=id)
    land = LandModel.objects.filter(member_id=member.id)
    protocol = ProtocolModel.objects.all()

    # form.helper.layout[2] = FormActions(
    #     Submit('protocol_save', 'Сохранить', css_class="btn-primary pull-right"),
    #     Submit('protocol_del', 'Удалить', css_class="btn-primary pull-right mr-2"),
    # )
    #
    # if 'protocol_del' in request.POST:
    #     obj.delete()
    #     return HttpResponseRedirect(reverse('app:protocol_list'))
    #
    # if 'protocol_save' in request.POST:
    #     if form.is_valid():
    #         form.save()
    #         return HttpResponseRedirect(reverse('app:protocol_list'))

    form = CreditForm(request.POST or None)
    # form.helper.layout[0] = FormActions(
    #     Submit('protocol_save', 'Сохранить', css_class="btn-primary pull-right"),
    # )

    if form.is_valid():
        form.save(commit=False)
        form.instance.member_id = member
        form.save()
        return HttpResponseRedirect(reverse('app:member_detail', args=(id,)))

    context = {
        'form': form,
        'protocol': protocol,
        'land': land,
    }

    return render(request, 'settings/credit.html', context)


def credit_update(request, id):
    credit = get_object_or_404(Credits, id=id)
    land = LandModel.objects.filter(id=credit.land_id_id)
    member_id = land.values('member_id')
    protocol = ProtocolModel.objects.filter(id=credit.meeting_id_id)

    initial_dict = {
        'date_start': credit.date_start.strftime("%d.%m.%Y"),
        'date_finish': credit.date_finish.strftime("%d.%m.%Y"),
    }

    # form.helper.layout[2] = FormActions(
    #     Submit('protocol_save', 'Сохранить', css_class="btn-primary pull-right"),
    #     Submit('protocol_del', 'Удалить', css_class="btn-primary pull-right mr-2"),
    # )
    #
    # if 'protocol_del' in request.POST:
    #     obj.delete()
    #     return HttpResponseRedirect(reverse('app:protocol_list'))
    #
    # if 'protocol_save' in request.POST:
    #     if form.is_valid():
    #         form.save()
    #         return HttpResponseRedirect(reverse('app:protocol_list'))

    form = CreditForm(request.POST or None, instance=credit, initial=initial_dict)
    if 'credit_save' in request.POST:
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('app:member_detail', args=(int(member_id[0]['member_id']),)))

    context = {
        'form': form,
        'protocol': protocol,
        'land': land,
    }

    return render(request, 'settings/credit.html', context)


def credit_list(request):
    err_msg = None
    try:
        company = CompanyModel.objects.get(user_snt=request.user)
        members = MemberModel.objects.filter(company_id=company.id)
        credit_list = Credits.objects.filter(member_id_id__in=members)
        print(credit_list.values())
    except CompanyModel.DoesNotExist:
        credit_list = None
        err_msg = 'Первым делом необходимо выполнить настройки Организации.'

    context = {
        'dataset': credit_list,
        'err_msg': err_msg,
    }
    return render(request, 'settings/credit.html', context)


def get_dadata(inn):
    token = '8e395d15a1206b762e59b997136d82763480a33e'
    dadata = Dadata(token)
    result = dadata.find_by_id('party', inn)
    result = dict(ChainMap(*result))
    return result


def sizeof_fmt(num, suffix='б'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return f'{num:3.1f} {unit}{suffix}'
        num /= 1024.0
    return f'{num:.1f} Yi{suffix}'


def company_detail(request):
    # company = get_object_or_404(CompanyModel, user_snt=request.user)
    # bank = get_object_or_404(BankModel, id=company.bank_id)
    scan_list = []

    try:
        company = CompanyModel.objects.get(user_snt=request.user)
        bank = BankModel.objects.get(company_id=company.id)
        agent = AgentModel.objects.filter(company_id=company.id)
        attachment = ScanCompanyModel.objects.get(company_id=company.id)

        dataset = dict.fromkeys(['key', 'filename', 'size'])

        dataset['key'] = 'ustav'
        if attachment.ustav != '':
            dataset['filename'] = str(attachment.ustav).split('/')[1]
            size = os.path.getsize(MEDIA_ROOT + '/' + str(attachment.ustav))
            dataset['size'] = sizeof_fmt(int(size))
        else:
            dataset['filename'] = ''
            dataset['size'] = ''
        buff = dataset.copy()
        scan_list.append(buff)

        dataset['key'] = 'inn'
        if attachment.inn != '':
            dataset['filename'] = str(attachment.inn).split('/')[1]
            size = os.path.getsize(MEDIA_ROOT + '/' + str(attachment.inn))
            dataset['size'] = sizeof_fmt(int(size))
        else:
            dataset['filename'] = ''
            dataset['size'] = ''
        buff = dataset.copy()
        scan_list.append(buff)

        dataset['key'] = 'ogrn'
        if attachment.ogrn != '':
            dataset['filename'] = str(attachment.ogrn).split('/')[1]
            size = os.path.getsize(MEDIA_ROOT + '/' + str(attachment.ogrn))
            dataset['size'] = sizeof_fmt(int(size))
        else:
            dataset['filename'] = ''
            dataset['size'] = ''
        buff = dataset.copy()
        scan_list.append(buff)

        dataset['key'] = 'yegryul'
        if attachment.yegryul != '':
            dataset['filename'] = str(attachment.yegryul).split('/')[1]
            size = os.path.getsize(MEDIA_ROOT + '/' + str(attachment.yegryul))
            dataset['size'] = sizeof_fmt(int(size))
        else:
            dataset['filename'] = ''
            dataset['size'] = ''
        buff = dataset.copy()
        scan_list.append(buff)
    except (CompanyModel.DoesNotExist, AgentModel.DoesNotExist):
        company = None
        bank = None
        agent = None
        scan = None
    except BankModel.DoesNotExist:
        company = CompanyModel.objects.get(user_snt=request.user)
        agent = AgentModel.objects.filter(company_id=company.id)
        bank = None
        scan = None
    except ScanCompanyModel.DoesNotExist:
        company = CompanyModel.objects.get(user_snt=request.user)
        bank = BankModel.objects.get(company_id=company.id)
        agent = AgentModel.objects.filter(company_id=company.id)
        scan = None

    form_inn = InputInnForm(None)
    form_bik = InputBikForm(None)
    form_bank = BankSettingsForm(None)
    form_company = MainSettingsForm(None)
    form_agent = AgentForm(None)
    form_scan = ScanCompanyForm(None)
    # if company is None:
    #     form_company.fields["fio_manager"].widget.attrs['readonly'] = True
    print(request.POST)

    if 'save_company' in request.POST:
        print(f'request POST save company - {request.POST}')
        form_company = MainSettingsForm(request.POST or None, instance=company)
        form_company.instance.user_snt = request.user
        # if company is None:
        #     first_penalty = PenaltyModel.objects.create(
        #         description='По умолчанию',
        #         rate=0.0,
        #         user_snt=request.user
        #     )
        #     first_penalty.save()
        #     form_company.instance.penalty_id = first_penalty
        # else:
        #     penalty = PenaltyModel.objects.latest('id')
        #     form_company.instance.penalty_id = penalty

        if form_company.is_valid():
            form_company.save()
            if company is None:
                save_company = CompanyModel.objects.get(user_snt=request.user)
                fio = form_company.cleaned_data.get('fio_manager')
                data = fio.split()
                print('fio - ' + fio)
                print('data[1] - ' + data[1])
                first_agent = AgentModel.objects.create(
                    first_name=data[1],
                    second_name=data[0],
                    third_name=data[2],
                    position=form_company.cleaned_data.get('position_manager'),
                    active=True,
                    company_id_id=save_company.id,
                )
                first_agent.save()

            return HttpResponseRedirect(reverse('app:company_detail'))
        else:
            print(f'save company valid form error - {form_company.errors}')

    if 'save_bank' in request.POST:
        form_bank = BankSettingsForm(request.POST or None, instance=bank)
        form_bank.instance.company_id_id = company.id
        if form_bank.is_valid():
            form_bank.save()
            return HttpResponseRedirect(reverse('app:company_bank'))

    if 'save_agent' in request.POST:
        if request.POST.get('id_edit'):
            id = request.POST.get('id_edit')
            agent = AgentModel.objects.get(pk=id)
            agent.first_name = request.POST.get('first_name')
            agent.second_name = request.POST.get('second_name')
            agent.third_name = request.POST.get('third_name')
            agent.position = request.POST.get('position')
            agent.phone = request.POST.get('phone')
            agent.address = request.POST.get('address')
            agent.doc = request.POST.get('doc')
            agent.num_doc = request.POST.get('num_doc')
            agent.file_doc = request.FILES.get('file_doc')
            agent.save()
            return HttpResponseRedirect(reverse('app:company_agent'))
        else:
            form_agent = AgentForm(request.POST, request.FILES)
            form_agent.instance.company_id_id = company.id
            if form_agent.is_valid():
                form_agent.save()
                return HttpResponseRedirect(reverse('app:company_agent'))

    if 'save_scan' in request.POST:
        if request.POST.get('id_edit'):
            id = request.POST.get('id_edit')
            scan = ScanCompanyModel.objects.get(pk=id)
            if request.FILES.get('inn') is not None:
                scan.inn = request.FILES.get('inn')
            if request.FILES.get('ogrn') is not None:
                scan.ogrn = request.FILES.get('ogrn')
            if request.FILES.get('ustav') is not None:
                scan.ustav = request.FILES.get('ustav')
            if request.FILES.get('yegryul') is not None:
                scan.yegryul = request.FILES.get('yegryul')
            scan.save()
            return HttpResponseRedirect(reverse('app:company_scan'))
        else:
            form_scan = ScanCompanyForm(request.POST, request.FILES)
            form_scan.instance.company_id_id = company.id
            if form_scan.is_valid():
                form_scan.save()
                return HttpResponseRedirect(reverse('app:company_scan'))

    if request.POST.get('action') == 'company_edit':
        obj = PenaltyModel.objects.latest('id')

        response_data = {
            'company_name': company.company_name,
            'company_inn': company.company_inn,
            'company_ogrn': company.company_ogrn,
            'full_company_name': company.full_company_name,
            'full_address': company.full_address,
            'rate': obj.rate,
            'phone': company.phone,
            'email': company.email,
            'fio_manager': company.fio_manager,
            'position_manager': company.position_manager,
        }
        return JsonResponse(response_data)
        # TODO: return JsonResponse({"data": "Data goes here"}, status=200)
    if request.POST.get('action') == 'bank_edit':
        response_data = {
            'bank_name': bank.bank_name,
            'inn_bank': bank.inn_bank,
            'bik_bank': bank.bik_bank,
            'kpp': bank.kpp,
            'correspondent_acc': bank.correspondent_acc,
            'checking_acc': bank.checking_acc,
        }
        return JsonResponse(response_data)
    if request.POST.get('action') == 'agent_edit':
        id = request.POST.get('id')
        response_data = AgentModel.objects.filter(id=id).values()[0]
        return JsonResponse(response_data)
    if request.POST.get('action') == 'agent_delete':
        id = request.POST.get('id')
        AgentModel.objects.filter(id=id).delete()
        return HttpResponseRedirect(reverse('app:company_agent'))
    if request.POST.get('action') == 'agent_update_active':
        print(f'request update active - {request.POST}')
        AgentModel.objects.filter(company_id_id=company.id).update(active=False)
        id = request.POST.get('id')
        AgentModel.objects.filter(id=id).update(active=True)

        return JsonResponse({'response': 'ok'})
    if request.POST.get('action') == 'scan_edit':
        response_data = ScanCompanyModel.objects.filter(company_id=company.id).values()[0]
        return JsonResponse(response_data)
    if request.POST.get('action') == 'scan_delete':
        company = CompanyModel.objects.get(user_snt=request.user)
        scan = ScanCompanyModel.objects.get(company_id=company.id)
        if request.POST.get('field') == 'inn':
            scan.inn = ''
        if request.POST.get('field') == 'ogrn':
            scan.ogrn = ''
        if request.POST.get('field') == 'ustav':
            scan.ustav = ''
        if request.POST.get('field') == 'yegryul':
            print('92834769098')
            scan.yegryul = ''
        scan.save()

        return HttpResponseRedirect(reverse('app:company_scan'))

    context = {
        'company': company,
        # 'rate': PenaltyModel.objects.latest('id').rate,
        'bank': bank,
        'agent': agent,
        'scan': scan_list,
        'form_inn': form_inn,
        'form_bik': form_bik,
        'form_company': form_company,
        'form_bank': form_bank,
        'form_agent': form_agent,
        'form_scan': form_scan,
    }

    return render(request, 'settings/main.html', context=context)


def company_create(request):
    pass


def company_update(request):
    try:
        company = CompanyModel.objects.get(user_snt=request.user)
    except CompanyModel.DoesNotExist:
        company = None

    print(f'request user - {request.user}')
    print(f'request POST company_update - {request.POST}')
    initial_dict = {
        'company_name': request.POST.get('company_name_edit'),
        'company_inn': request.POST.get('company_inn_edit'),
        'company_ogrn': request.POST.get('company_ogrn_edit'),
        'full_company_name': request.POST.get('full_company_name_edit'),
        'fio_manager': request.POST.get('fio_manager_edit'),
        'position_manager': request.POST.get('position_manager_edit'),
        'full_address': request.POST.get('full_address_edit'),
        'phone': request.POST.get('phone_edit'),
        'email': request.POST.get('email_edit'),
        'rate': 0.0,
        'agent_id': '',
        'user_snt': request.user,
    }
    form_cmp = MainSettingsForm(user=request.user, initial=initial_dict)

    if 'save_company' in request.POST:
        print(f'press button company save')
        # form_cmp.instance.agent_id = AgentModel.objects.get(id=int(request.POST.get('agent_id')))
        # form_cmp.instance.bank_id = BankModel.objects.get(id=int(request.POST.get('bank_id')))
        form_cmp.save()
        return HttpResponseRedirect(reverse('app:company_detail'))

    context = {
        'form_cmp': form_cmp,
    }

    return render(request, 'settings/main.html', context=context)


def bank_detail(request):
    err_msg = None
    # try:
    #     company = CompanyModel.objects.get(user_snt=request.user)
    #     bank = BankModel.objects.filter(company_id=company.id)
    # except CompanyModel.DoesNotExist:
    #     bank = None
    #     err_msg = 'Первым делом необходимо выполнить настройки Организации.'
    bank = BankModel.objects.all()
    context = {
        'dataset': bank,
        'err_msg': err_msg,
    }
    return render(request, 'settings/bank.html', context)


def bank_create(request):
    err_msg = bank = None
    # try:
    #     company = CompanyModel.objects.get(user_snt=request.user)
    # except CompanyModel.DoesNotExist:
    #     err_msg = 'Первым делом необходимо выполнить настройки Организации.'

    if 'save_bank' in request.POST:
        form_bik = InputBikForm(None)
        form_bank = BankSettingsForm(request.POST or None)
        form_bank.instance.user_snt = request.user
        if form_bank.is_valid():
            form_bank.save()
            return HttpResponseRedirect(reverse('app:bank_detail'))

    elif 'fill_bik' in request.POST:
        print(f'press button fiil bik')
        form_bik = InputBikForm(request.POST)
        if form_bik.is_valid():
            bik = form_bik.cleaned_data['bik']
            token = '8e395d15a1206b762e59b997136d82763480a33e'
            dadata = Dadata(token)
            result_bik = dadata.find_by_id('bank', bik)
            result_bik = dict(ChainMap(*result_bik))

            initial_dict = {
                'bank_name': result_bik['value'],
                'bik': result_bik['data']['bic'],
                'inn': result_bik['data']['inn'],
                'kpp': result_bik['data']['kpp'],
                'correspondent_acc': result_bik['data']['correspondent_account'],
            }
            form_bank = BankSettingsForm(None, initial=initial_dict)
    else:
        form_bik = InputBikForm(None)
        form_bank = BankSettingsForm(request.POST or None)

    context = {
        'form_bank': form_bank,
        'form_bik': form_bik,
        'dataset': bank,
        'err_msg': err_msg,
    }
    return render(request, 'settings/bank.html', context)


def bank_update(request, id):
    bank = get_object_or_404(BankModel, id=id)
    form_bik = InputBikForm(None)
    form_bank = BankSettingsForm(request.POST or None, instance=bank)

    if 'save_bank' in request.POST:
        if form_bank.is_valid():
            form_bank.save()
            return HttpResponseRedirect(reverse('app:bank_detail'))

    context = {
        'form_bank': form_bank,
        'form_bik': form_bik,
        'dataset': bank,
        # 'err_msg': err_msg,
    }
    return render(request, 'settings/bank.html', context)


def agent_list(request):
    err_msg = None
    # try:
    #     company = CompanyModel.objects.get(user_snt=request.user)
    #     agent = AgentModel.objects.filter(company_id=company.id)
    # except CompanyModel.DoesNotExist:
    #     agent = None
    #     err_msg = 'Первым делом необходимо выполнить настройки Организации.'
    agent = AgentModel.objects.all()
    context = {
        'dataset': agent,
        'err_msg': err_msg,
    }
    return render(request, 'settings/agent.html', context)


def agent_create(request):
    form_agent = AgentForm(request.POST or None)
    form_agent.instance.user_snt = request.user
    if form_agent.is_valid():
        form_agent.save()
        return HttpResponseRedirect(reverse('app:agent_list'))

    context = {
        'form_agent': form_agent,
    }
    return render(request, 'settings/agent.html', context)


def agent_update(request, id):
    agent = get_object_or_404(AgentModel, id=id)
    form_agent = AgentForm(request.POST or None, instance=agent)
    if form_agent.is_valid():
        form_agent.save()
        return HttpResponseRedirect(reverse('app:agent_list'))

    context = {
        'form_agent': form_agent,
    }
    return render(request, 'settings/agent.html', context)


def get_key_rate(request):

    s = requests.Session()
    s.headers ={
        # 'cookie': '__ddg1_ = TTt7P9ixzbbHYsa5vtEr',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    # headers_get = {
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    #     'Accept-Language': 'en-US,en;q=0.5',
    #     'Accept-Encoding': 'gzip, deflate',
    #     'DNT': '1',
    #     'Connection': 'keep-alive',
    #     'Upgrade-Insecure-Requests': '1'
    # }

    url = 'https://www.cbr.ru/hd_base/KeyRate/'
    response = s.get(url)
    tree = html.fromstring(response.text)

    scripts = tree.xpath('//div[@class="container-fluid"]//script/text()')
    categories = re.findall('"categories":.*?]', scripts[3])

    data = re.findall('"data":.*?]', scripts[3])
    categories.append(data[0])

    buff = '{' + categories[0].replace('"', '\'') + ',' + categories[1].replace('"', '\'') + '}'
    print(f'buff key rate - {buff}')
    result = eval(buff)

    key_rate_list = []
    all_date = pd.date_range(result['categories'][0], result['categories'][-1], freq='D').strftime('%d.%m.%Y')
    for i in range(0, len(all_date)):
        item = [all_date[i], 0]
        for j in range(0, len(result['categories'])):
            if all_date[i] == result['categories'][j]:
                item[1] = result['data'][j]
        key_rate_list.append(item)

    for i in range(1, len(key_rate_list)):
        if key_rate_list[i][1] == 0:
            key_rate_list[i][1] = key_rate_list[i - 1][1]
        # print(key_rate_list[i])

    KeyRate.objects.all().delete()
    print(f'Все записи из таблицы KeyRate - удалены!')

    for i in range(0, len(key_rate_list)):
        date_time_obj = datetime.strptime(key_rate_list[i][0], '%d.%m.%Y')
        # print(f'date_time_obj - {date_time_obj}')
        if date_time_obj.date() > date(2016, 1, 1):
            KeyRate.objects.create(date=date_time_obj.date(), rate=key_rate_list[i][1])

    context = {

    }
    return render(request, 'summary.html', context=context)


# TODO: изменить название данной функции
def lands(request):
    err_msg = None
    try:
        company = CompanyModel.objects.get(user_snt=request.user)
        lands = LandModel.objects.filter(company_id=company.id)

        list_lands = []
        dataset = dict.fromkeys(['id', 'number', 'kadastr_number', 'land_address', 'members'])

        for item in lands:
            dataset['id'] = item.id
            dataset['number'] = item.number
            dataset['kadastr_number'] = item.kadastr_number
            dataset['land_address'] = item.land_address
            fio = item.members.all()

            # dataset['members'] = list(item.members.values('first_name'))
            dataset['members'] = list(item.members.all())

            buff = dataset.copy()
            list_lands.append(buff)
        # print(list_members)
        # print(f' members - {members.id}')
        # all = LandModel.objects.all()
        # print(f' all - {all.values()}')
        # dataset = LandModel.objects.filter(member_id_id__in=members.values('id'))

    except CompanyModel.DoesNotExist:
        list_lands = None
        err_msg = 'Первым делом необходимо выполнить настройки Организации.'

    form_member = MemberForm(None)
    form_land = LandsForm(None)
    form_ownership = OwnershipForm(None)

    template = 'lands.html'
    context = {
        'header': 'Земельные участки',
        'dataset': list_lands,
        'form_land': form_land,
        'form_member': form_member,
        'form_ownership': form_ownership,
        'err_msg': err_msg,
    }
    return render(request, template, context)


def penalties(request):
    company = CompanyModel.objects.get(user_snt=request.user)
    penalty = PenaltyModel.objects.filter(company_id=company.id)

    print(request.POST)

    if 'save-penalty' in request.POST:
        if request.POST.get('id_penalty'):
            id = request.POST.get('id_penalty')
            penalty = PenaltyModel.objects.get(pk=id)
            form_penalty = PenaltyForm(request.POST, request.FILES, instance=penalty)
            if form_penalty.is_valid():
                form_penalty.save()
                return HttpResponseRedirect(reverse('app:penalties'))

        form_penalty = PenaltyForm(request.POST, request.FILES)
        form_penalty.instance.company_id_id = company.id
        if form_penalty.is_valid():
            form_penalty.save()
            return HttpResponseRedirect(reverse('app:penalties'))
        else:
            print(form_penalty.errors)

    # if request.POST.get('action') == 'penalty_delete':
    #     id = request.POST.get('id')
    #     PenaltyModel.objects.filter(id=id).delete()
    #     return HttpResponseRedirect(reverse('app:penalties'))

    # if request.POST.get('action') == 'penalty_edit':
    #     id = request.POST.get('id')
    #     response_data = PenaltyModel.objects.filter(id=id).values()[0]
    #     return JsonResponse(response_data)

    form_penalty = PenaltyForm(None)

    key_rate = KeyRate.objects.filter(date__year__gte='2017').order_by('-date').values('date', 'rate')
    list = []
    line = {
        'st_date': key_rate[0]['date'].strftime('%d %B %Y'),
        'fn_date': date.today().strftime('%d %B %Y'),
        'rate': key_rate[0]['rate'],
    }
    list.append(line)

    for i in range(1, len(key_rate)):
        if key_rate[i]['rate'] == key_rate[i - 1]['rate']:
            list[-1]['st_date'] = key_rate[i]['date'].strftime('%d %B %Y')
        else:
            start = key_rate[i]['date']
            finish = datetime.strptime(list[-1]['st_date'], '%d %B %Y') - timedelta(days=1)
            line = {
                'st_date': start.strftime('%d %B %Y'),
                'fn_date': finish.strftime('%d %B %Y'),
                'rate': key_rate[i]['rate'],
            }
            list.append(line)

    template = 'penalties.html'
    context = {
        'header': 'Размер неустойки',
        'penalty': penalty,
        'bank_rate': list,
        'form_penalty': form_penalty,
    }
    return render(request, template, context)


def get_penalty(request, id):
    response = PenaltyModel.objects.filter(pk=id).values()[0]
    return JsonResponse(response)


def del_penalty(request, id):
    PenaltyModel.objects.filter(pk=id).delete()
    response = {'message': 'ok'}
    return JsonResponse(response)


# Справочик - Членские взносы :: Старт
def members_fee(request):
    company = CompanyModel.objects.get(user_snt=request.user)
    print(f'Загружаем список Членские взносы')

    # print(f'Создаем новую запись Членские взносы')
    # print(f'request POST - {request.POST}')

    # проверяем нажата ли кнопка submit
    # if 'btn-create-fee-save' in request.POST:
    #     # если присутствует идентификатор - то это режим редактирования
    #     if request.POST.get('id_fee'):
    #         print(f'Это режим редактирования')
    #         id = request.POST.get('id_fee')
    #         members_fee = MembersFeeModel.objects.get(pk=id)
    #         fee_form = MembersFeeForm(request.POST, request.FILES, instance=members_fee)
    #         fee_form.instance.company_id_id = company.id
    #         if fee_form.is_valid():
    #             fee_form.save()
    #             return HttpResponseRedirect(reverse('app:members_fee'))
    #
    #     # если идентификатора нет, то создаем новую запись
    #     # формируя также таблицу с начислениями
    #     fee_form = MembersFeeForm(request.POST, request.FILES)
    #     fee_form.instance.company_id_id = company.id
    #     if fee_form.is_valid():
    #         fee_form.save()
    #         type_fee = fee_form.cleaned_data['type_fee']
    #
    #         # условие для членского типа взноса
    #         if type_fee == '0':
    #             shift = int(fee_form.cleaned_data['day_accrual']) - 1
    #             result = pd.date_range(
    #                 fee_form.cleaned_data['date_start'],
    #                 fee_form.cleaned_data['date_finish'],
    #                 freq='MS'
    #             ).shift(shift, freq='D')
    #
    #             for i in range(0, len(result)):
    #                 DebtCharges.objects.create(date_payment=result[i], id_member_fee=fee_form.instance)
    #
    #         # условие для целевого типа взноса
    #         if type_fee == '1':
    #             DebtCharges.objects.create(
    #                 date_payment=fee_form.cleaned_data['date_finish'],
    #                 id_member_fee=fee_form.instance
    #             )
    #
    #         return HttpResponseRedirect(reverse('app:members_fee'))

    fee_form = MembersFeeForm(None)
    fee = MembersFeeModel.objects.filter(company_id=company.id)
    template = 'members_fee.html'
    context = {
        'header': 'Членские взносы',
        'fee': fee,
        'fee_form': fee_form,
    }
    return render(request, template, context)


def members_fee_create(request):
    print(f'members_fee_create')
    print(f'request POST - {request.POST}')
    company = CompanyModel.objects.get(user_snt=request.user)

    # если присутствует идентификатор - то это режим редактирования
    if request.POST.get('id_fee'):
        print(f'Процесс редактирования')

        id = request.POST.get('id_fee')
        members_fee = MembersFeeModel.objects.get(pk=id)

        changed_data = request.POST.copy()
        changed_data.update({'date_start': members_fee.date_start})
        changed_data.update({'date_finish': members_fee.date_finish})

        fee_form = MembersFeeForm(changed_data, request.FILES, instance=members_fee)
        fee_form.instance.company_id_id = company.id
        if fee_form.is_valid():
            fee_form.save()
            return HttpResponseRedirect(reverse('app:members_fee'))
        else:
            print(f'Ошибка при редактирование записи Членских взносов!')

    fee = MembersFeeModel.objects.filter(company_id=company.id).exists()
    # первым делом определим какой "тип взноса" пришёл
    type_fee = request.POST.get('type_fee')
    # ежемесячная плата :: Проверка период - они не должны пересекаться!
    if fee and int(type_fee) == 0:
        fee_first = MembersFeeModel.objects.filter(company_id=company.id).filter(type_fee=type_fee).order_by('id').first()
        fee_last = MembersFeeModel.objects.filter(company_id=company.id).filter(type_fee=type_fee).order_by('-id').first()
        # print(f'Первая запись в "Членских взносах" - {fee_first.id}')
        # print(f'Последняя запись в "Членских взносах" - {fee_last.id}')
        dsp = datetime.strptime(str(fee_first.date_start), '%Y-%m-%d')
        dfp = datetime.strptime(str(fee_last.date_finish), '%Y-%m-%d')
        # print(f'Весь диапазон периода в "Членских взносах" - {dsp} - {dfp}')

        ds = datetime.strptime(request.POST.get('date_start'), '%d.%m.%Y')
        df = datetime.strptime(request.POST.get('date_finish'), '%d.%m.%Y')

        # print(f'Дата начала интервала периода :: {dsp.date()}')
        # print(f'Дата окончания интервала периода :: {dfp.date()}')
        # print(f'ввод дат - {ds.date()} :: {df.date()}')
        # dsp - дата начала интервала периода
        # dfp - дата конца интервала периода

        # # проверяем условие "в"
        # print(f'dsp < ds < dfp - {dsp <= ds <= dfp}')
        # print(f'dsp < df < dfp - {dsp <= df <= dfp}')
        if dsp < ds < dfp:
            row = MembersFeeModel.objects.filter(company_id=company.id). \
                filter(date_start__lte=ds, date_finish__gte=ds).first()
            data = dict(error='Период пересекается с записями в базе данных!', body=row.num_doc)
            return JsonResponse(data, status=400)

        if dsp < df < dfp:
            row = MembersFeeModel.objects.filter(company_id=company.id). \
                filter(date_start__lte=df, date_finish__gte=df).first()
            data = dict(error='Период пересекается с записями в базе данных!', body=row.num_doc)
            return JsonResponse(data, status=400)

        # проверяем условие "до"
        # print(f'ds < dsp - {ds < dsp - timedelta(days=1)}')
        # print(f'df < dsp - {df == dsp - timedelta(days=1)}')
        # print(f'dsp - 1 :: {dsp - timedelta(days=1)}')
        if (ds < dsp - timedelta(days=1)) and (df != dsp - timedelta(days=1)):
            data = dict(error='Между периодами документов не должно быть "пробелов"!', body=fee_first.num_doc)
            return JsonResponse(data, status=400)

        # # проверяем условие "после"
        if (dfp + timedelta(days=1) < df) and (ds != dfp + timedelta(days=1)):
            data = dict(error='Между периодами документов не должно быть "пробелов"!', body=fee_last.num_doc)
            return JsonResponse(data, status=400)
        # if (ds - dfp).days != 1 or 0 < (df - dfp).days < 2:
        #     print(f'(ds - dfp).days != 1 --- {(ds - dfp).days}')
        #     print(f'(df - dfp).days < 2 --- {(df - dfp).days}')
        #     data = {'error': 'Между периодами не должно быть пробелов! Проверка "после"'}
        #     return JsonResponse(data, status=400)
    # ежеквартальная плата
    # ...
    # ежегодная плата
    # ...

    fee_form = MembersFeeForm(request.POST, request.FILES)
    fee_form.instance.company_id_id = company.id
    date_finish_pay = request.POST.get('date_finish_pay')
    if fee_form.is_valid():
        directory = str(company.id)
        path = os.path.join(settings.MEDIA_ROOT, directory)
        if not os.path.exists(path):
            os.mkdir(path)
        # fee_form.save()

        opp_detail = fee_form.save(commit=False)  # gives you the instance without saving it
        if date_finish_pay:
            dt_object1 = datetime.strptime(date_finish_pay, '%d.%m.%Y')
            opp_detail.date_finish = dt_object1
        opp_detail.save()  # now save

        type_fee = fee_form.cleaned_data['type_fee']
        # расчет таблицы начислений
        # условие для членского типа взноса
        if type_fee == '0':
            shift = int(fee_form.cleaned_data['day_accrual']) - 1
            result = pd.date_range(
                fee_form.cleaned_data['date_start'],
                fee_form.cleaned_data['date_finish'],
                freq='MS'
            ).shift(shift, freq='D')

            for i in range(0, len(result)):
                DebtCharges.objects.create(date_payment=result[i], id_member_fee=fee_form.instance)
        # условие для целевого типа взноса
        if type_fee == '1':
            dt_object1 = datetime.strptime(date_finish_pay, '%d.%m.%Y')
            DebtCharges.objects.create(
                date_payment=dt_object1,
                id_member_fee=fee_form.instance
            )
    else:
        print(f'Ошибка добавления записи в справочник Членские взносы!')

    response = {
        'data': 'данные успешно добавлены!'
    }
    return JsonResponse(response, status=200)


def get_members_fee(request, id):
    obj_data = MembersFeeModel.objects.get(pk=id)
    response_data = MembersFeeModel.objects.filter(pk=id).values()[0]
    response_data['type_fee_value'] = obj_data.get_type_fee_display()
    response_data['payment_period_value'] = obj_data.get_payment_period_display()

    print(f'response_data - {response_data}')

    return JsonResponse(response_data)


def del_members_fee(request, id):
    MembersFeeModel.objects.filter(pk=id).delete()
    response = {'message': 'ok'}
    return JsonResponse(response)
# Справочник - Членские взносы :: Конец


def about(request):
    template = 'about.html'
    context = {
        'data': 'О cистеме',
    }
    return render(request, template, context)


def doc_penalty(request):
    template = 'doc-penalty.html'
    context = {
        'data': 'Справка по расчету пеней',
    }
    return render(request, template, context)


def test_member(request):
    from app.models import TestMemberModel
    print(f'ManyToMany для Физических лиц')
    # company = CompanyModel.objects.get(user_snt=request.user)
    members = TestMemberModel.objects.all()

    print(f'members all():')
    for item in members:
        print(f'{item.id} :: {item.address} :: {item.fio} :: {item.phone}')

    template = 'test.html'
    context = {
        'data': 'О cистеме',
    }
    return render(request, template, context)


def test_land(request):
    print(f'ManyToMany для дачных участков')
    from app.models import TestLandModel, TestMemberModel
    # lands = TestLandModel.objects.all()
    # print(f'lands all():')
    # for item in lands:
    #     print(f'{item.id} :: {item.address} :: {item.members.values()}')
    members = TestMemberModel.objects.filter(id=3)
    lands = TestLandModel.objects.filter(members__in=members)
    for item in lands:
        print(f'{item.id} :: {item.address} :: {item.members.values()}')

    template = 'test.html'
    context = {
        'data': 'О cистеме',
    }
    return render(request, template, context)


def land_new(request):
    err_msg = company = None
    try:
        company = CompanyModel.objects.get(user_snt=request.user)
    except CompanyModel.DoesNotExist:
        err_msg = 'Первым делом необходимо выполнить настройки Организации.'

    form = LandsForm(request.POST or None)
    form.instance.company_id = company
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('app:lands'))
    context = {
        'form': form,
        'err_msg': err_msg,
    }
    return render(request, 'land.html', context)


# TODO: функций ajax - должная возвращть только ответ json
#       подобная реализация есть в функции company_detail

# TODO: посмотреть реализацию - как определить текущий шаблоны
#       или спользовать шаблоны в параметрах функции

#     if request.POST.get('action') == 'company_edit':
#         obj = PenaltyModel.objects.latest('id')
#
#         response_data = {
#             'company_name': company.company_name,
#             'company_inn': company.company_inn,
#             'company_ogrn': company.company_ogrn,
#             'full_company_name': company.full_company_name,
#             'full_address': company.full_address,
#             'rate': obj.rate,
#             'phone': company.phone,
#             'email': company.email,
#             'fio_manager': company.fio_manager,
#             'position_manager': company.position_manager,
#         }
#         return JsonResponse(response_data)

def land_add(request):
    print(f'land add --> {request.POST}')
    #
    # i = Item.objects.create(name="Water Bottle", price=100)
    # c = Customer.objects.create(name="Abhishek", age=21)
    # p = Purchase(item=i, customer=c,
    #              date_purchased=date(2019, 7, 7),
    #              quantity_purchased=3)
    #
    # p.save()

    if len(request.POST.get('id_land')) == 0:
        # Company нам необходимо для добавления Land
        company = CompanyModel.objects.get(user_snt=request.user)
        # две формы Lands и Ownership
        form_land = LandsForm(request.POST)
        if form_land.is_valid():
            obj_land = LandModel.objects.create(
                number=form_land.cleaned_data['number'],
                kadastr_number=form_land.cleaned_data['kadastr_number'],
                land_address=form_land.cleaned_data['land_address'],
                comment=form_land.cleaned_data['comment'],  # эта запись не происходит
                attachment=form_land.cleaned_data['attachment'],  # эта запись не происходит
                company_id=company
            )

            data = {
                'id': obj_land.id,
                'number': obj_land.number,
                'kadastr_number': obj_land.kadastr_number,
                'land_address': obj_land.land_address
            }
            # print(f'data for response - {obj_land.serializable_value("land_address")}')
            return JsonResponse(data, status=200)
            # return JsonResponse(list(obj_land.objects.values()), safe=False, status=200)
            # return JsonResponse({'data': 'Error save object Land'}, status=200)
        else:
            return JsonResponse({'data': 'Error save object Land'}, status=200)
    else:
        print(f'редактирование')
        obj_land = LandModel.objects.get(pk=request.POST.get('id_land'))

    print(f'Прошли условия!')

    member_list = request.POST.getlist('members')
    obj_land.members.clear()
    if len(member_list) > 1:
        start_hold_list = request.POST.getlist('start_hold')
        end_hold_list = request.POST.getlist('end_hold')
        comment_list = request.POST.getlist('comment')
        attachment_list = request.POST.getlist('attachment')
        for i in range(1, len(member_list)):
            obj_member = MemberModel.objects.get(pk=member_list[i])
            if len(start_hold_list[i]) == 0:
                start_hold = None
            else:
                start_hold = datetime.strptime(start_hold_list[i], '%d.%m.%Y')

            if len(end_hold_list[i]) == 0:
                end_hold = None
            else:
                end_hold = datetime.strptime(end_hold_list[i], '%d.%m.%Y')

            obj_ownership = OwnershipModel.objects.filter(member=obj_member.pk).filter(land=obj_land.pk)
            print(f'объект ownersip - {obj_ownership}')
            if not obj_ownership:
                print(f'создаем ownership')
                OwnershipModel.objects.create(
                    member=obj_member,
                    land=obj_land,
                    start_hold=start_hold,
                    end_hold=end_hold,
                    comment=comment_list[i],
                    attachment=attachment_list[i]
                )
            else:
                print(f'пересохраняем ownership')
                for obj in obj_ownership:
                    obj.start_hold = start_hold
                    obj.end_hold = end_hold
                    obj.comment = comment_list[i]
                    obj.attachment = attachment_list[i]
                    obj.save()

    return JsonResponse({'data': 'Land append'}, status=200)


def land_delete(request, id):
    LandModel.objects.filter(id=id).delete()
    return JsonResponse({'data': 'ok'}, status=200)


def get_lands(request):
    company = CompanyModel.objects.get(user_snt=request.user)
    lands = LandModel.objects.filter(company_id=company.id)

    data_lands = {'lands': []}
    for item in lands:
        land = {
            'id': item.id,
            'number': item.number,
            'kadastr_number': item.kadastr_number,
            'address': item.land_address
        }
        data_lands['lands'].append(land)

    return HttpResponse(json.dumps(data_lands), content_type='application/json')


def get_land(request, id):
    # obj_data = MemberModel.objects.get(pk=id)
    # response = MemberModel.objects.filter(pk=id).values()[0]
    # response['status_value'] = obj_data.get_status_display()
    # list = obj_data.lands.all()
    # serialized_list = serializers.serialize('json', list)
    # response['land_list'] = serialized_list
    #
    # ownership = OwnershipModel.objects.filter(land__ownershipmodel__member_id=obj_data.pk)
    # serialized_list = serializers.serialize('json', ownership)
    # response['ownership'] = serialized_list
    #
    # return JsonResponse(response, status=200)

    obj_data = LandModel.objects.get(pk=id)
    response = LandModel.objects.filter(pk=id).values()[0]
    list = obj_data.members.all()
    serialized_list = serializers.serialize('json', list)
    response['member_list'] = serialized_list

    ownership = OwnershipModel.objects.filter(member__ownershipmodel__land_id=obj_data.pk)
    serialized_list = serializers.serialize('json', ownership)
    response['ownership'] = serialized_list

    print(response)

    return JsonResponse(response, status=200)

    # company = CompanyModel.objects.get(user_snt=request.user)
    # lands = LandModel.objects.filter(company_id=company.id).filter(id=id)
    #
    # data_lands = {'lands': []}
    # for item in lands:
    #     land = {
    #         'id': item.id,
    #         'number': item.number,
    #         'kadastr_number': item.kadastr_number,
    #         'address': item.land_address
    #     }
    #     data_lands['lands'].append(land);
    #
    # return HttpResponse(json.dumps(data_lands), content_type='application/json')


def get_debit_land(request, member_id):
    member = MemberModel.objects.get(pk=member_id)
    member_lands = DebtsModel.objects.filter(land__in=member.lands.all()).values('land_id', 'land__land_address', 'sum')

    html = render_to_string("tmp_table/multiform_step_3.html", context={'lands': member_lands})
    return HttpResponse(html)


def members_get(request):
    company = CompanyModel.objects.get(user_snt=request.user)
    members = MemberModel.objects.filter(company_id=company.id)
    print(members.values()[0])

    data_members = {'members': []}
    for item in members:
        member = {
            'id': item.id,
            'fio': item.second_name + ' ' + item.second_name + ' ' + item.third_name,
            'status': item.status,
            'address': item.address,
            'phone': item.phone,
            'email': item.email,
            'series_number_doc': item.series_number_doc,
            'division_code': item.division_code,
            'date_of_issue': item.date_of_issue,
            'issued': item.issued,
            'date_of_birth': item.date_of_birth,
            'place_of_birth': item.place_of_birth,


        # $('#modal-add-member input[name="series_number_doc"]').val(edit_data.series_number_doc);
        # $('#modal-add-member input[name="division_code"]').val(edit_data.division_code);
        # $('#modal-add-member input[name="date_of_issue"]').val(edit_data.date_of_issue);
        # $('#modal-add-member input[name="date_of_birth"]').val(edit_data.date_of_birth);
        # $('#modal-add-member input[name="place_of_birth"]').val(edit_data.place_of_birth);

        }
        data_members['members'].append(member)

    return HttpResponse(json.dumps(data_members), content_type='application/json')


def member_get(request, id):
    from django.core import serializers

    obj_data = MemberModel.objects.get(pk=id)
    response = MemberModel.objects.filter(pk=id).values()[0]
    response['status_value'] = obj_data.get_status_display()
    list = obj_data.lands.all()
    serialized_list = serializers.serialize('json', list)
    response['land_list'] = serialized_list

    ownership = OwnershipModel.objects.filter(land__ownershipmodel__member_id=obj_data.pk)
    serialized_list = serializers.serialize('json', ownership)
    response['ownership'] = serialized_list

    print(f'respone member_get - {response}')

    return JsonResponse(response, status=200)


def test_index(request):
    template = 'test/index.html'
    context = {
        'data': 'Тестовая страница',
    }
    return render(request, template, context)


# del
# def change_land(request, instruction, pk):
#     land = LandModel.objects.get(pk=pk)
#     if instruction == 'add_land':
#         LandModel.add_land(request, land)
#     elif instruction == 'del_land':
#         LandModel.del_land(request, land)


def find_inn(request):
    token = '8e395d15a1206b762e59b997136d82763480a33e'
    dadata = Dadata(token)
    result = dadata.find_by_id('party', request.POST.get('inn'))
    result = dict(ChainMap(*result))

    if not result:
        data = {'error': 'Not find inn'}
        response = HttpResponse(json.dumps(data), content_type='application/json')
        response.status_code = 403
        return response
    else:
        data = {
            'fio_manager': result['data']['management']['name'],
            'company_name': result['value'],
            'company_inn': result['data']['inn'],
            'company_ogrn': result['data']['ogrn'],
            'full_company_name': result['data']['name']['full_with_opf'],
            'position_manager': result['data']['management']['post'],
            'full_address': result['data']['address']['unrestricted_value']
        }
        return HttpResponse(json.dumps(data), content_type='application/json')


def find_bik(request):
    print(f'find bik - {request.POST.get("bik")}')
    token = '8e395d15a1206b762e59b997136d82763480a33e'
    dadata = Dadata(token)
    result = dadata.find_by_id('bank', request.POST.get('bik'))
    result = dict(ChainMap(*result))

    if not result:
        data = {'error': 'Not find bik'}
        response = HttpResponse(json.dumps(data), content_type='application/json')
        response.status_code = 403
        return response
    else:
        data = {
            'bank_name': result['value'],
            'bik': result['data']['bic'],
            'inn': result['data']['inn'],
            'kpp': result['data']['kpp'],
            'correspondent_acc': result['data']['correspondent_account'],
        }
        return HttpResponse(json.dumps(data), content_type='application/json')


def debit_list(request):
    company = CompanyModel.objects.get(user_snt=request.user)
    dataset = MemberModel.objects.filter(company_id__user_snt=request.user).filter(lands__debtsmodel__sum__gte=0).\
        values('pk', 'first_name', 'second_name', 'third_name', 'lands__debtsmodel').annotate(Sum('lands__debtsmodel__sum'))

    for item in dataset:
        response = get_debit_info(item['lands__debtsmodel'], company.id)
        item['lands__debtsmodel__sum__sum'] = response['total_accruals'] + response['total_penalties']

    debit_form = DebitForm(None, user=request.user)
    template = 'debits.html'
    context = {
        'header': 'Задолженность',
        'dataset': dataset,
        'debit_form': debit_form,
    }
    return render(request, template, context)


def debit_detail(request, member_id):
    debt = DebtsModel.objects.filter(land__members=member_id).values('id', 'land__land_address', 'start_debt', 'end_debt',
                                                                      'type_accuals', 'sum')
    data = {'data': list(debt)}
    return JsonResponse(data, status=200)


def debit_add(request):
    form_start_date = datetime.strptime(request.POST.get('start_debt'), '%d.%m.%Y').date()
    form_end_date = date.today()
    if request.POST.get('end_debt'):
        form_end_date = datetime.strptime(request.POST.get('end_debt'), '%d.%m.%Y').date()

    print(f'\n\n\nДобавление задолженности:')
    print(f'request.POST - {request.POST}')
    print(f'Содержимое - form_start_date - {form_start_date}')
    print(f'Содержимое - form end date - {form_end_date}')

    # членский взнос
    if request.POST.get('type_doc') == '0':
        list_debits = DebtsModel.objects.filter(land_id=request.POST.get('land')).filter(type_doc=0)
        print(f'list_debits - {list_debits}')
        for item in list_debits:
            if item.end_debt is not None:
                print(f'Номер записи - {item.id}')
                if item.start_debt <= form_start_date <= item.end_debt or item.start_debt <= form_end_date <= item.end_debt:
                    print(f'item.start_debt < form_start_date < item.end_debt\n'
                          f'{item.start_debt} :: {form_start_date} :: {item.end_debt}')
                    print(f'item.start_debt < form_end_date < item.end_debt\n'
                          f'{item.start_debt} :: {form_end_date} :: {item.end_debt}')
                    print(f'Есть совпадение периодов! Номер записи - {item.id}')
                    data = dict(error='Период пересекается с записями в базе данных!', body=item.id)
                    return JsonResponse(data, status=400)

            else:
                print(f'Номер последней записи - {item.id}')
                item.end_debt = date.today()
                if item.start_debt <= form_start_date <= item.end_debt or item.start_debt <= form_end_date <= item.end_debt:
                    print(f'item.start_debt < form_start_date < item.end_debt\n'
                          f'{item.start_debt} :: {form_start_date} :: {item.end_debt}')
                    print(f'item.start_debt < form_end_date < item.end_debt\n'
                          f'{item.start_debt} :: {form_end_date} :: {item.end_debt}')
                    print(f'Есть совпадение периодов! Номер записи - {item.id}')
                    data = dict(error='Период пересекается с записями в базе данных!', body=item.id)
                    return JsonResponse(data, status=400)

    # целевой взнос
    if request.POST.get('type_doc') == '1':
        print(f'Здесь делаем что-то такое с целевым взносом')

    company = CompanyModel.objects.get(user_snt=request.user)
    land = LandModel.objects.get(pk=request.POST.get('land'))
    form_debit = DebitForm(request.POST, user=request.user)
    form_debit.instance.land = land

    if form_debit.is_valid():
        new_debt_obj = form_debit.save()

        # Если Членский взнос, то:
        if request.POST.get('type_doc') == '0':
            # Та самая сложная функция, которая требует внимания и детального разбора!
            result = get_debit_info(new_debt_obj.id, company.id)

            # Обновляем поле Суммы у задолженности (все это после работы функции get_debit_info())
            debt = DebtsModel.objects.get(pk=new_debt_obj.id)
            debt.sum = result["total_accruals"]
            debt.save()

            # Сохраняем калькуляцию Начислений
            print(f'list_accruals - {result["list_accruals"]}')
            for item in result['list_accruals']:
                obj_accruals = AccrualsCalculationModel(debt_id=new_debt_obj.id, **item)
                obj_accruals.save()

            # Сохраняем калькуляцию Пени
            for item in result['list_penalties']:
                obj_penalty = PenaltyCalculationModel(debt_id=new_debt_obj.id, **item)
                obj_penalty.save()

            # ext = form_debit.save(commit=False)
            # ext.sum = 1000
            # ext.save()
    else:
        print(form_debit.errors)

    return HttpResponseRedirect(reverse('app:debit_list'))


# расчет ставки вынесен в отдельную функцию потому что
# - необходим расчет общего результата в списке задолженностей
# - необходим расчет для индивидуальной задолженности
def get_debit_info(debit_id, company_id):
    # Берем queryset необходимой Задолженности по id
    debit = DebtsModel.objects.get(pk=debit_id)

    print(f'debit - {debit}')

    t = debit.type_doc  # Этот параметр необходимо для расчет Типа членского взноса
    l = debit.land.id

    # Определяем конечную дату
    start_date = debit.start_debt
    if debit.end_debt is None:
        end_date = date.today()
    else:
        end_date = debit.end_debt
    print(f'Результат по определению периода: {debit_id} ::: {start_date} ::: {end_date}')

    # Начисления. Добавляем еще один месяц
    # print(f'Период текущей задолженности - {start_date} :: {end_date}')
    # end_date = end_date + relativedelta(months=1)
    # print(f'Период текущей задолженности(отредактированный) - {start_date} :: {end_date}')

    # -----------------------------------------------------------------------------------------------------------------

    # Новый запрос
    accruals = DebtCharges.objects.filter(
        date_payment__gte=start_date, date_payment__lte=end_date,
        id_member_fee__company_id__landmodel=l, id_member_fee__type_fee=0)\
        .values('date_payment', 'id_member_fee__amount_fee', 'id_member_fee', 'id_member_fee__type_fee'
                ).order_by('date_payment')
    # Исключаем в это выборке тип начислений Целевой взнос
    print('Выборка начислений - accruals :', *accruals, sep='\n')

    # Проверить что за список !!!
    test_list_type_0 = DebtCharges.objects.filter(
        date_payment__gte=start_date, date_payment__lte=end_date,
        id_member_fee__type_fee=0, id_member_fee__company_id__landmodel=l)\
        .values('date_payment', 'id_member_fee__amount_fee', 'id_member_fee', 'id_member_fee__type_fee'
                ).order_by('date_payment')

    # Список целевых взносов
    test_list_type_1 = DebtCharges.objects.filter(
        date_payment__gte=start_date, date_payment__lte=end_date,
        id_member_fee__type_fee=1, id_member_fee__company_id__landmodel=l)\
        .values('date_payment', 'id_member_fee__amount_fee', 'id_member_fee', 'id_member_fee__type_fee'
                ).order_by('date_payment')

    test_list_accruals = []
    dolg = 0
    for i in range(0, len(accruals)-1):
        data = dict(
            date_start=accruals[i]['date_payment'],
            date_finish=accruals[i+1]['date_payment'],
        )
        test_list_accruals.append(data)

    # Добавляем последнюю запись
    data = dict(
        date_start=accruals[len(accruals)-1]['date_payment'],
        date_finish=end_date,
    )
    test_list_accruals.append(data)

    test_list_accruals.sort(key=lambda x: x.get('date_start'))
    print('Выборка начислений - accruals (с обработанным периодом) :', *test_list_accruals, sep='\n')

    # Пропускаем список через выборку Целевых взносов. Задача врезать дату Целевого взноса в период начислений.
    # Это необходимо для корректного расчета Пени
    print(f'Выборка целевых взносов - {test_list_type_1}')
    buff = list(test_list_type_1)
    pos = 1
    for j in range(0, len(buff)):
        for i in range(0, len(test_list_accruals)):
            if test_list_accruals[i]['date_start'] < buff[j]['date_payment'] < test_list_accruals[i]['date_finish']:
                data = dict(
                    date_start=buff[j]['date_payment'],
                    date_finish=test_list_accruals[i]['date_finish'],
                )
                test_list_accruals[i]['date_finish'] = buff[j]['date_payment']
                test_list_accruals.insert(pos, data)

                pos += 1
                continue
            pos += 1
    print('Выборка начислений - accruals (после обработки "Целевого взноса") :', *test_list_accruals, sep='\n')

    # ------------------------------------------------------------------------------------------------------------------

    # Платежи
    # Берем платежи по Участку :: list_payments
    list_payments = []
    payments = PaymentsModel.objects.filter(land_id=l).order_by('date_payment')
    for item in payments:
        data = dict(date=item.date_payment, type=item.get_type_payment_display(), sum=float(item.sum_payment))
        list_payments.append(data)
    print('Список платежей:', *list_payments, sep='\n')

    # пропускаем список через выборку платежей
    pos = 1
    for j in range(0, len(list_payments)):
        for i in range(0, len(test_list_accruals)):
            if test_list_accruals[i]['date_start'] < list_payments[j]['date'] < test_list_accruals[i]['date_finish']:
                data = dict(
                    date_start=list_payments[j]['date'],
                    date_finish=test_list_accruals[i]['date_finish'],
                )
                test_list_accruals[i]['date_finish'] = list_payments[j]['date']
                test_list_accruals.insert(pos, data)

                pos += 1
                continue
            pos += 1
    test_list_accruals.sort(key=lambda x: x.get('date_start'))
    # print('Выборка начислений - accruals (после обработки платежей) :', *test_list_accruals, sep='\n')

    # ------------------------------------------------------------------------------------------------------------------

    penal = []
    if PenaltyModel.objects.filter(company_id=company_id).exists():
        penalty = PenaltyModel.objects.filter(company_id=company_id).values('date_start').order_by('date_start')
        penal = list(penalty)
        pos = 1
        for j in range(0, len(penal)):
            for i in range(0, len(test_list_accruals)):
                if test_list_accruals[i]['date_start'] < penal[j]['date_start'] < test_list_accruals[i]['date_finish']:
                    data = dict(
                        date_start=penal[j]['date_start']-timedelta(days=1),
                        date_finish=test_list_accruals[i]['date_finish'],
                    )
                    test_list_accruals[i]['date_finish'] = penal[j]['date_start']-timedelta(days=1)
                    test_list_accruals.insert(pos, data)

                    pos += 1
                    continue
                pos += 1

        test_list_accruals.sort(key=lambda x: x.get('date_start'))
        # есть случаи когда договор ставки начинает действовать раньше, чем день начисления
        print('Выборка начислений - accruals (после обработки "Ставки по договору") :', *test_list_accruals, sep='\n')

    # ------------------------------------------------------------------------------------------------------------------

    # Расчет накопленной задолженности
    accruals = DebtCharges.objects.filter(
        date_payment__gte=start_date, date_payment__lte=end_date,
        id_member_fee__company_id__landmodel=l)\
        .values('date_payment', 'id_member_fee__amount_fee', 'id_member_fee', 'id_member_fee__type_fee'
                ).order_by('date_payment')

    for i in range(0, len(test_list_accruals)):
        for j in range(0, len(accruals)):
            if test_list_accruals[i]['date_start'] == accruals[j]['date_payment']:
                type = MembersFeeModel.objects.get(pk=accruals[j]['id_member_fee'])
                dolg += accruals[j]['id_member_fee__amount_fee']
                type_display = type.get_type_fee_display()
                type_num = type.type_fee
                sum = float(accruals[j]['id_member_fee__amount_fee'])
                sum_edit = float(dolg)
                continue

        test_list_accruals[i]['type'] = type_display
        test_list_accruals[i]['type_num'] = type_num
        test_list_accruals[i]['sum'] = sum
        test_list_accruals[i]['sum_edit'] = sum_edit

    # print(f'end_date - {end_date}')

    test_list_accruals[-1]['date_finish'] = end_date
    # test_list_accruals[-1]['sum_edit'] = float(dolg) + sum
    test_list_accruals[-1]['sum_edit'] = float(dolg)

    list_accruals = []
    for item in test_list_accruals:
        # type = MembersFeeModel.objects.get(pk=item['id_member_fee'])
        data = dict(
            date_start=item['date_start'],
            date_finish=item['date_finish'],
            type=item['type'],
            type_num=item['type_num'],
            sum=float(item['sum']),
            sum_edit=float(item['sum_edit'])
        )
        list_accruals.append(data)
    list_accruals.sort(key=lambda x: x.get('date_start'))
    print('list_accruals:', *list_accruals, sep='\n')

    print('Результат выборки начислений test_list_accruals (до обработки платежей и пени) :', *test_list_accruals, sep='\n')

    dolg = 0
    for i in range(0, len(test_list_accruals)):
        dolg += float(test_list_accruals[i]['sum'])
        for j in range(0, len(list_payments)):
            # print(f"{test_list_accruals[i]['date_start']} :: {list_payments[j]['date']} :: {test_list_accruals[i]['date_finish']}")
            if test_list_accruals[i]['date_start'] <= list_payments[j]['date'] < test_list_accruals[i]['date_finish']:

                # print(f'{i} - if payments - {dolg}')
                dolg -= float(test_list_accruals[i]['sum'])
                dolg -= float(list_payments[j]['sum'])
                # test_list_accruals[i]['sum_edit'] = float(dolg)

        for j in range(0, len(penal)):
            # print(f"{test_list_accruals[i]['date_finish']} :: {penal[j]['date_start']}")
            if test_list_accruals[i]['date_start'] < penal[j]['date_start'] <= test_list_accruals[i]['date_finish']:
                # print(f'{i} - if penal - {dolg}')
                dolg -= float(test_list_accruals[i]['sum'])
                # test_list_accruals[i]['sum_edit'] = float(dolg)

        # for j in range(0, len(accruals)-1):
        #     if test_list_accruals[i]['date_finish'] == accruals[j]['date_payment']:
        #         dolg -= float(test_list_accruals[i]['sum'])

        test_list_accruals[i]['sum_edit'] = float(dolg)
        # print(f'dolf - {dolg} \n')

    # удалить скорее всего
    # test_list_accruals[-1]['sum_edit'] = float(dolg) + sum

    print('Результат выборки начислений test_list_accruals (после обработки платежей и пени) :', *test_list_accruals, sep='\n')

    # print(f'\n\n*****************************')
    # обходим членские взносы
    for i in range(0, len(test_list_type_0)-1):
        test_list_type_0[i]['date_finish'] = test_list_type_0[i+1]['date_payment']

    # обходим целевые взносы
    for i in range(0, len(test_list_type_1)):
        test_list_type_1[i]['date_finish'] = test_list_type_1[i]['date_payment']

    test_list_type_all = [*test_list_type_0, *test_list_type_1]
    test_list_type_all.sort(key=lambda x: x.get('date_payment'))

    dolg = 0
    for i in range(0, len(test_list_type_all)):
        test_list_type_all[i]['dolg'] = dolg
    test_list_type_all.pop()
    print('test_list_type_all:', *test_list_type_all, sep='\n')

    # list_accruals = []
    # for item in test_list_type_all:
    #     type = MembersFeeModel.objects.get(pk=item['id_member_fee'])
    #     data = dict(
    #         date_start=item['date_payment'],
    #         date_finish=item['date_finish'],
    #         type=type.get_type_fee_display(),
    #         type_num=type.type_fee,
    #         sum=float(item['id_member_fee__amount_fee']),
    #         sum_edit=float(item['dolg'])
    #     )
    #     list_accruals.append(data)
    # list_accruals.sort(key=lambda x: x.get('date_start'))
    # print('list_accruals:', *list_accruals, sep='\n')

    # print('Результат выборки начислений test_list_accruals(платежи): ', *test_list_accruals, sep='\n')

    # ------------------------------------------------------------------------------------------------------------------

    # Начисление пени. Необходим список test_list_accruals
    list_penalties = []
    # проверка наличия ставки в уставе
    if PenaltyModel.objects.filter(company_id=company_id).exists():
        penalty = PenaltyModel.objects.filter(company_id=company_id).values('date_start', 'rate').order_by('date_start')
        # print(f'Выборка даты и ставки из Базы данных: {list(penalty)}')
        new_penalty = list(penalty)
        new_penalty.append(dict(date_start=date.today(), rate=0.1))
        # print('Список членских взносов', *new_penalty, sep='\n')
        # print(f'Преобразованная дата и ставка (закрываем открытую дату): {new_penalty}')
        for j in range(1, len(new_penalty)):
            # расчет Пени по ставке из договора
            for i in range(0, len(test_list_accruals)):
                if new_penalty[j - 1]['date_start'] <= (test_list_accruals[i]['date_start']+timedelta(days=1)) < new_penalty[j]['date_start']:
                    # print(f"========{new_penalty[j - 1]['date_start']} :: {test_list_accruals[i]['date_start']} :: {new_penalty[j]['date_start']}")
                    type = test_list_accruals[i]['type']
                    rate = float(new_penalty[j-1]['rate'])
                    delta = (test_list_accruals[i]['date_finish'] - test_list_accruals[i]['date_start']).days
                    sum = test_list_accruals[i]['sum_edit'] * rate * delta / 100

                    ds = datetime.strptime(str(test_list_accruals[i]['date_start'] + timedelta(days=1)), '%Y-%m-%d').strftime('%d.%m.%Y')
                    de = datetime.strptime(str(test_list_accruals[i]['date_finish']), '%Y-%m-%d').strftime('%d.%m.%Y')

                    data = dict(
                        date=ds + ' - ' + de,
                        date_start=test_list_accruals[i]['date_start'],
                        date_finish=test_list_accruals[i]['date_finish'],
                        type=type,
                        days=delta,
                        rate=float(rate),
                        sum=float(sum),
                        sum_edit=float(test_list_accruals[i]['sum_edit'])
                    )
                    list_penalties.append(data)
    else:
        # print('test_list_accruals ____ before:', *test_list_accruals, sep='\n')
        # расчет Пени по ключевой ставке
        for i in range(0, len(test_list_accruals)):
            # print(f"Период с {list_accruals[i]['date_start']} по {list_accruals[i]['date_finish']}")
            check_first_day = KeyRate.objects.filter(date=test_list_accruals[i]['date_start']).exists()
            if check_first_day:
                key_rate = KeyRate.objects.filter(date__gte=test_list_accruals[i]['date_start'],
                                                  date__lte=test_list_accruals[i]['date_finish'])
            else:
                dt = test_list_accruals[i]['date_start'] - timedelta(days=2)
                key_rate = KeyRate.objects.filter(date__gte=dt, date__lte=test_list_accruals[i]['date_finish'])

            end_display = test_list_accruals[i]['date_finish']
            type = test_list_accruals[i]['type']
            start_display = key_rate.values('date')[0]['date']
            current_rate = key_rate.values('rate')[0]['rate']
            sum = test_list_accruals[i]['sum_edit']

            for item in key_rate:
                if item.rate != current_rate:
                    sd = start_display
                    ed = item.date
                    delta = (item.date - start_display - timedelta(days=1)).days
                    accurals = float(current_rate) * delta * float(sum) / 365 / 100

                    test_dict = dict(
                        date=(sd + timedelta(days=1)).strftime('%d.%m.%Y') + ' - ' + ((ed - timedelta(days=1)).strftime('%d.%m.%Y')),
                        date_start=test_list_accruals[i]['date_start'],
                        date_finish=test_list_accruals[i]['date_finish'],
                        rate=current_rate,
                        type=type,
                        days=delta,
                        sum=round(accurals, 2),
                        sum_edit=sum)
                    list_penalties.append(test_dict)

                    current_rate = item.rate
                    start_display = item.date - timedelta(days=1)

                elif item.rate == current_rate and item.date == end_display:
                    sd = start_display
                    ed = item.date
                    delta = (item.date - start_display).days
                    accurals = float(current_rate) * delta * float(sum) / 365 / 100

                    test_dict = dict(
                        date=(sd + timedelta(days=1)).strftime('%d.%m.%Y') + ' - ' + (ed.strftime('%d.%m.%Y')),
                        date_start=test_list_accruals[i]['date_start'],
                        date_finish=test_list_accruals[i]['date_finish'],
                        rate=current_rate,
                        type=type,
                        days=delta,
                        sum=round(accurals, 2),
                        sum_edit=sum)
                    list_penalties.append(test_dict)

    print('Список Пени:', *list_penalties, sep='\n')

    total_acc = 0
    for i in range(0, len(list_accruals)):
        total_acc += float(list_accruals[i]['sum'])
    print(f'Общая сумма начислений - {total_acc}')

    total_pay = 0
    for item in list_payments:
        total_pay += float(item['sum'])
    # print(f'Общая сумма платежей - {total_pay}')

    total_penal = 0
    for item in list_penalties:
        total_penal += float(item['sum'])

    response = {
        'land_name': debit.land.land_address,
        'total_accruals': total_acc,
        'total_payments': total_pay,
        'total_penalties': total_penal,
        'list_accruals': list_accruals,
        'list_payments': list_payments,
        'list_penalties': list_penalties,
    }

    return response


def debit_get(request, id):
    company_id = DebtsModel.objects.filter(pk=id).values('land__company_id')[0]
    response = get_debit_info(id, company_id['land__company_id'])
    print(f'result response - {response}')
    return JsonResponse(response, content_type='application/json', status=200)


def debit_get_list(request, id):
    company = CompanyModel.objects.get(user_snt=request.user)
    debts = DebtsModel.objects.filter(land__members=id).values('id')

    data = []
    for item in debts:
        data.append(get_debit_info(item['id'], company.id))

    response = {'data': data}
    return JsonResponse(response, status=200)


def debit_edit(request, id):
    pass


def debit_del(request, id):
    DebtsModel.objects.filter(id=id).delete()
    return JsonResponse({'data': 'Debit deleted'}, status=200)


def debitgroup_del(request, member_id):
    DebtsModel.objects.filter(land__members=member_id).delete()
    return JsonResponse({'data': 'Debitgroup deleted'}, status=200)


def payment_list(request):
    payments = PaymentsModel.objects.filter(land__company_id__user_snt=request.user).values(
        'land__land_address', 'land_id').annotate(total_sum=Sum('sum_payment'))

    form_payment = PaymentForm(None, user=request.user)

    template = 'payments.html'
    context = {
        'header': 'Платежи',
        'dataset': payments,
        'form_payment': form_payment,
    }
    return render(request, template, context)


def payment_add(request):
    print(f'request payment add - {request.POST}')

    # если есть payment_id - редактируем данные
    if 'id_payment' in request.POST:
        payment = PaymentsModel.objects.get(id=request.POST.get('id_payment'))
        land = LandModel.objects.get(pk=request.POST.get('land'))
        form_payment = PaymentForm(request.POST, instance=payment, user=request.user)
        # form_payment.instance.land = land
        if form_payment.is_valid():
            form_payment.save()
        else:
            print(f'ошибка в данных редактирование - {form_payment.errors}')
        return HttpResponseRedirect(reverse('app:payment_list'))

    land = LandModel.objects.get(pk=request.POST.get('land'))
    form_payment = PaymentForm(None or request.POST, user=request.user)
    form_payment.instance.land = land
    if form_payment.is_valid():
        form_payment.save()
    else:
        print(form_payment.errors)

    return HttpResponseRedirect(reverse('app:payment_list'))


def payment_get(request, id):
    payment = PaymentsModel.objects.filter(pk=id)
    serialized_list = serializers.serialize('json', payment)
    response = {'data': serialized_list}
    print(response)
    # return HttpResponse(json.dumps(response), content_type="application/json")
    return JsonResponse(response, status=200)


def payment_del(request, id):
    PaymentsModel.objects.filter(id=id).delete()
    return JsonResponse({'data': 'Payment deleted'}, status=200)


def get_payment_for_land(request, id_land):
    payments = PaymentsModel.objects.filter(land_id=id_land)
    print(f'payments - {payments}')
    r = dict(data=[])

    # проходим по списку и переписываем тип на текстовое значение
    for item in payments:
        r['data'].append(dict(
            pk=item.pk,
            fio=item.fio,
            date_payment=item.date_payment,
            type_payment=item.get_type_payment_display(),
            sum_payment=item.sum_payment
        ))
    print(f'r - {r}')

    # serialized_list = serializers.serialize('json', payments)
    # response = dict(data=serialized_list)
    # print(f'response - {response}')
    return JsonResponse(r, status=200)


def del_payment_for_land(request, id_land):
    PaymentsModel.objects.filter(land_id=id_land).delete()
    return JsonResponse({'data': 'Payments deleted'}, status=200)


def get_ownership(request, id):
    ownership = OwnershipModel.objects.filter(pk=id)
    serialized_list = serializers.serialize('json', ownership)
    response = {'ownership': serialized_list}

    print(response)

    return JsonResponse(response, status=200)


def edit_ownership(request, id):
    if id is not None:
        print(request.POST)
        ownership = OwnershipModel.objects.get(pk=id)
        form = OwnershipForm(request.POST)
        if form.is_valid():
            ownership.start_hold = form.cleaned_data['start_hold']
            ownership.save()

            print(form.cleaned_data)

        response = {'data': 'ok'}
        return JsonResponse(response, status=200)
    else:
        pass


def del_ownership(request, id):
    OwnershipModel.objects.filter(id=id).delete()
    return JsonResponse({'data': 'ok'}, status=200)
