from django.contrib import admin
from django.apps import apps
from app.models import CourtMoscow


class CourtMoscowAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'judge_fio', 'address', 'phones')


class ListAdminMixin(object):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(ListAdminMixin, self).__init__(model, admin_site)


models = apps.get_models()
for model in models:
    admin_class = type('AdminClass', (ListAdminMixin, admin.ModelAdmin), {})
    try:
        if model == CourtMoscow:
            admin.site.register(CourtMoscow, CourtMoscowAdmin)
        else:
            admin.site.register(model, admin_class)
    except admin.sites.AlreadyRegistered:
        pass

