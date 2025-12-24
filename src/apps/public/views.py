from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate as activate_lang
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings

from apps.core.auth.permissions import PermissionMixin
from apps.core.views import UpdateViewMixin

from apps.accounting.models import (Company, PettyCashTransaction)

from . import forms

User = get_user_model()


class Index(TemplateView):
    template_name = 'public/index.html'

    def get_context_data(self, **kwargs):
        context = {
            'users': User.objects.all(),
            'company': Company.objects.first(),
        }

        # Expense(Invoice Cost)
        total_expense_week = PettyCashTransaction.objects.this_week().filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
        total_expense_month = PettyCashTransaction.objects.this_month().filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0
        total_expense = PettyCashTransaction.objects.filter(transaction_type='expense').aggregate(total=Sum('amount'))['total'] or 0

        if total_expense > 0:
            # Weekly
            week_ratio = total_expense_week / total_expense
            week_percentage = week_ratio * 100
            # Monthly
            month_ratio = total_expense_month / total_expense
            month_percentage = month_ratio * 100
        else:
            week_percentage = 0
            month_percentage = 0

        context.update({
            'total_expense_week':total_expense_week,
            'total_expense_month':total_expense_month,
            'week_percentage': week_percentage,
            'month_percentage':month_percentage
        })

        return context


class SetLang(View):

    def get_referrer_url(self):
        return self.request.META.get('HTTP_REFERER', reverse_lazy('public:settings'))

    def is_language_available(self, lang):
        langs = settings.LANGUAGES
        return any(c == lang for c, n in langs)

    def get(self, request, lang):
        if not self.is_language_available(lang):
            messages.error(request, _('Language code is not available'))
            return redirect(self.get_referrer_url())
        activate_lang(lang)

        request.session[settings.LANGUAGE_COOKIE_NAME] = lang

        response = redirect(self.get_referrer_url())
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang
        )

        return response


class Settings(PermissionMixin, TemplateView):
    permissions = ('public.manage_settings',)
    template_name = 'public/settings.html'

    def get_context_data(self, **kwargs):
        return {
            'company': Company.objects.first(),
            'permissions': Permission.objects.all(),
        }


class CompanyUpdate(PermissionMixin, UpdateViewMixin, View):
    permissions = ('public.change_company',)
    form = forms.CompanyUpdateForm
    redirect_url = reverse_lazy('public:settings')

    def post(self, request):
        return self.update(request)
