from app import views
from django.conf.urls import url
from django.urls import path

# from django.conf import settings
# from django.conf.urls.static import static

app_name = 'app'

urlpatterns = [
    url(r'^$', views.summary, name='index'),
    url('^summary/$', views.summary, name="summary"),

    url('^settings/main$', views.main_tab, name="main_settings"),
    url('^settings/bank$', views.bank_tab, name="bank_settings"),
    url('^settings/agent$', views.agent, name="agent_settings"),

    url(r'^download/$', views.download_file, name='download_file'),

    url('^result/$', views.isk_tmp_first, name="result_multiform"),
    url('^getsud/$', views.get_sudrf),

    # url('^findcourt/$', views.find_court_for_first_tmp),
    url('^updatecourt/$', views.get_court),
    url('^updcourtmoscowregion/$', views.get_courts_moscow_region),

    #####
    path('isk_tmp/1', views.isk_tmp_first, name='isk_tmp'),
    path('isk_tmp/2', views.isk_tmp_second, name='isk_tmp_2'),
    path('debtors_list', views.debtors_list, name='debtors_list'),
    path('debtors_list_2', views.debtors_list_2, name='debtors_list_2'),
    path('preisk_tmp', views.pretrial_tmp, name='pretrial_tmp'),
    path('history_tmp', views.history_tmp, name='history_tmp'),

    path('get-debit-land/<member_id>', views.get_debit_land),
    path('findcourt', views.find_court_for_first_tmp),
    path('findcourtmir', views.find_court_for_second_tmp),
    path('issued', views.issued),


    path('protocol', views.protocol_list, name='protocol_list'),
    path('protocol/add', views.protocol_create, name='protocol_add'),
    path('protocol/<id>/edit', views.protocol_update, name='protocol_edit'),

    path('member', views.member_list, name='member_list'),
    # path('member/add', views.member_create, name='member_add'),
    path('member/add', views.member_add, name='member_add'),
    path('member/get', views.members_get),
    path('member/<id>/edit', views.member_update, name='member_edit'),
    # path('member/<id>/detail', views.member_detail, name='member_detail'),
    path('member/<id>', views.member_detail, name='member_detail'),
    path('member/land', views.get_land_for_member, name='member_land'),
    path('member/<id>/get', views.member_get),
    path('member/<id>/del', views.member_del),

    path('debt', views.debit_list, name='debit_list'),
    path('debt/<member_id>', views.debit_detail, name='debit_detail'),
    path('debit/add', views.debit_add, name='debit_add'),
    path('debit/<id>/del', views.debit_del, name='debit_del'),
    path('debitgroup/<member_id>/del', views.debitgroup_del, name='debitgroup_del'),
    path('debit/<id>/get', views.debit_get, name='debit_get'),
    path('debit/<id>/edit', views.debit_edit, name='debit_edit'),
    path('debit/<id>/list', views.debit_get_list, name='debit_get_list'),

    # path('debit/detail', views.debit_list, name='debit_list'),          # Подробная информация по списку

    path('payment', views.payment_list, name='payment_list'),
    path('payment/add', views.payment_add, name='payment_add'),
    path('payment/<id>/get', views.payment_get, name='payment_get'),
    path('payment/<id>/del', views.payment_del, name='payment_del'),
    path('payment-group/<id_land>/get', views.get_payment_for_land),
    path('payment-group/<id_land>/del', views.del_payment_for_land),


    # path('land/<id>/add', views.land_create, name='land_add'),
    path('land/<id>/edit', views.land_update, name='land_edit'),
    path('land/add', views.land_add, name='land_add'),
    path('land/get', views.get_lands),
    path('land/<id>/get', views.get_land),
    # path('land/<instruction>/<pk>', views.change_land, name='change_land'),
    path('land/<id>/del', views.land_delete),

    path('ownership/<id>/get', views.get_ownership),
    path('ownership/<id>/edit', views.edit_ownership),
    path('ownership/<id>/del', views.del_ownership),

    path('inn', views.find_inn),
    path('bik', views.find_bik),
    path('company', views.company_detail, name='company_detail'),
    path('bank', views.company_detail, name='company_bank'),
    path('agent', views.company_detail, name='company_agent'),
    path('scan', views.company_detail, name='company_scan'),
    path('company/add', views.company_create, name='company_add'),
    path('company/edit', views.company_update, name='company_edit'),

    # path('bank', views.bank_detail, name='bank_detail'),
    path('bank/add', views.bank_create, name='bank_add'),
    path('bank/<id>/edit', views.bank_update, name='bank_edit'),

    # path('agent', views.agent_list, name='agent_list'),
    path('agent/add', views.agent_create, name='agent_add'),
    path('agent/<id>/edit', views.agent_update, name='agent_edit'),

    path('getkeyrate', views.get_key_rate, name='get_key_rate'),

    path('lands', views.lands, name='lands'),
    path('penalties', views.penalties, name='penalties'),
    path('penalties/<id>/get', views.get_penalty),
    path('penalties/<id>/del', views.del_penalty),

    path('fee', views.members_fee, name='members_fee'),
    path('fee/add', views.members_fee_create, name='members_fee_create'),
    path('fee/<id>/get', views.get_members_fee),
    path('fee/<id>/del', views.del_members_fee),

    path('about', views.about, name='about'),
    path('doc-penalty', views.doc_penalty, name='doc_penalty'),

    path('testmember', views.test_member, name='test_member'),
    path('testlands', views.test_land, name='test_land'),

    path('test', views.test_index, name='test_index'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)