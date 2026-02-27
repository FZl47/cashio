from django.utils.translation import gettext_lazy as _
from django.utils.translation import activate as activate_lang
from django.utils import timezone
from django.views.generic import TemplateView, View
from django.shortcuts import redirect
from django.contrib.auth import get_user_model
from django.db.models.functions import TruncMonth, Coalesce
from django.db.models import Sum, Value, DecimalField, Q
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings

from apps.core.auth.permissions import PermissionMixin, SuperUserRequiredMixin
from apps.core.views import UpdateViewMixin, CreateOrUpdateViewMixin

from apps.accounting.models import (PettyCashTransaction, PettyCashFund, Document, DocumentApprovalProcessGroup)

from . import forms, models

User = get_user_model()


class Index(TemplateView):
    template_name = 'public/index.html'

    def get_context_data(self, **kwargs):
        user = self.request.user

        documents = Document.objects.all()
        transactions = PettyCashTransaction.objects.all()
        funds = PettyCashFund.objects.all()

        users = []
        if user.is_superuser:
            users = User.objects.all()
        elif user.is_admin:
            users = User.objects.filter(role='common_user')

        if user.is_common_user:
            documents = documents.filter(Q(uploaded_by=user) | Q(required_approvers__user__in=[user]))
            transactions = transactions.filter(Q(created_by=user) | Q(holder__user__in=[user]))
            funds = funds.filter(holders__user__in=[user])

        context = {
            'funds': funds,
            'users': users,
            'documents': documents,
            'transactions': transactions
        }

        # Expense(Invoice Cost)
        total_expense_week = \
            PettyCashTransaction.objects.this_week().filter(transaction_type='expense').aggregate(total=Sum('amount'))[
                'total'] or 0
        total_expense_month = \
            PettyCashTransaction.objects.this_month().filter(transaction_type='expense').aggregate(total=Sum('amount'))[
                'total'] or 0
        total_expense = PettyCashTransaction.objects.filter(transaction_type='expense').aggregate(total=Sum('amount'))[
                            'total'] or 0

        if total_expense > 0:
            # Weekly
            week_ratio = total_expense_week / total_expense
            expense_week_percentage = week_ratio * 100
            # Monthly
            month_ratio = total_expense_month / total_expense
            expense_month_percentage = month_ratio * 100
        else:
            expense_week_percentage = 0
            expense_month_percentage = 0

        monthly_expenses_qs = PettyCashTransaction.objects.filter(transaction_type='expense',
                                                                  created_at__year=timezone.now().year).annotate(
            month=TruncMonth('date')).values('month').annotate(
            total=Coalesce(Sum('amount'), Value(0, output_field=DecimalField()))).order_by(
            'month').values('month', 'total')

        months_dict = {i: 0 for i in range(1, 13)}

        for item in monthly_expenses_qs:
            months_dict[item['month'].month] = float(item['total'])

        expense_chart_data = [months_dict[i] for i in range(1, 13)]
        context.update({
            'total_expense_week': total_expense_week,
            'total_expense_month': total_expense_month,
            'expense_week_percentage': expense_week_percentage,
            'expense_month_percentage': expense_month_percentage,
            'expense_chart_data': expense_chart_data
        })

        # Income

        total_income_week = PettyCashTransaction.objects.this_week().filter(transaction_type='income').aggregate(
            total=Sum('amount'))['total'] or 0

        total_income_month = PettyCashTransaction.objects.this_month().filter(transaction_type='income').aggregate(
            total=Sum('amount'))['total'] or 0

        total_income = PettyCashTransaction.objects.filter(transaction_type='income').aggregate(
            total=Sum('amount'))['total'] or 0

        if total_income > 0:
            # Weekly
            week_ratio = total_income_week / total_income
            income_week_percentage = week_ratio * 100
            # Monthly
            month_ratio = total_income_month / total_income
            income_month_percentage = month_ratio * 100
        else:
            income_week_percentage = 0
            income_month_percentage = 0

        # Monthly income chart
        monthly_income_qs = PettyCashTransaction.objects.filter(
            transaction_type='income',
            created_at__year=timezone.now().year
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Coalesce(Sum('amount'), Value(0, output_field=DecimalField()))
        ).order_by('month').values('month', 'total')

        months_dict = {i: 0 for i in range(1, 13)}
        for item in monthly_income_qs:
            months_dict[item['month'].month] = float(item['total'])

        income_chart_data = [months_dict[i] for i in range(1, 13)]

        context.update({
            'total_income_week': total_income_week,
            'total_income_month': total_income_month,
            'income_week_percentage': income_week_percentage,
            'income_month_percentage': income_month_percentage,
            'income_chart_data': income_chart_data
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


class Settings(SuperUserRequiredMixin, TemplateView):
    template_name = 'public/settings.html'

    YARMALLI_SDK_ENABLED = None

    def check_yarmalli_sdk_enabled(self):
        if self.YARMALLI_SDK_ENABLED:
            return self.YARMALLI_SDK_ENABLED
        try:
            import yarmalli_sdk
            self.YARMALLI_SDK_ENABLED = True
        except ImportError:
            self.YARMALLI_SDK_ENABLED = False
        return self.YARMALLI_SDK_ENABLED

    def get_context_data(self, **kwargs):
        users = User.objects.filter(is_active=True)
        return {
            'approval_process_groups': DocumentApprovalProcessGroup.objects.all(),
            'users_approval_process_groups': users.filter(documentapprovalprocessgroup__isnull=True),
            'users': users,
            'yarmalli_sdk_has_enabled': self.check_yarmalli_sdk_enabled(),
            'yarmalli_settings': models.YarMalliSettings.objects.first()
        }


class CompanyUpdate(PermissionMixin, UpdateViewMixin, View):
    permissions = ('public.change_company',)
    form = forms.CompanyUpdateForm
    redirect_url = reverse_lazy('public:settings')

    def post(self, request):
        return self.update(request)


class YarMalliSettingsAPIKeyManage(PermissionMixin, CreateOrUpdateViewMixin, View):
    permissions = ('public.change_yarmallisettings',)
    form = forms.YarMalliSettingsAPIKeyManageForm
    redirect_url = reverse_lazy('public:settings')

    def post(self, request):
        if self.get_instance():
            return self.update(request)
        return self.create(request)

    def get_instance(self):
        return models.YarMalliSettings.objects.first()
