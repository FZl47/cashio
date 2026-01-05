from django.utils.translation import gettext_lazy as _
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.db.models import Q, OuterRef, Subquery, Sum
from django.db.models.functions import ExtractMonth
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from apps.core.views import CreateViewMixin, ListViewMixin, DetailViewMixin, UpdateViewMixin
from apps.core.auth.permissions.mixins import PermissionMixin

from . import forms, models

User = get_user_model()


class PettyCashFundCreate(PermissionMixin, CreateViewMixin, TemplateView):
    permissions = ('accounting.add_pettycashfund',)
    template_name = 'accounting/petty_cash_fund/create.html'
    form = forms.PettyCashFundCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['holders'] = models.PettyCashHolder.objects.filter(user__is_active=True).select_related('user')
        return context

    def post(self, request):
        return self.create(request)


class PettyCashFundUpdate(PermissionMixin, UpdateViewMixin, View):
    permissions = ('accounting.change_pettycashfund',)
    form = forms.PettyCashFundUpdateForm

    def get_instance(self):
        return get_object_or_404(models.PettyCashFund, id=self.kwargs['pk'])

    def post(self, request, *args, **kwargs):
        return self.update(request)


class PettyCashFundList(LoginRequiredMixin, ListViewMixin, TemplateView):
    template_name = 'accounting/petty_cash_fund/list.html'
    page_size = 8

    def get_queryset(self):
        qs = models.PettyCashFund.objects.all()

        user = self.request.user
        if user.is_common_user:
            qs = qs.filter(holders__user=user)

        qs = self.filter(qs).prefetch_related('holders__user').distinct()
        return qs

    def filter(self, qs):
        params = self.request.GET

        sort_by = params.get('sort_by', 'latest')
        if sort_by == 'latest':
            qs = qs.order_by('-id')
        else:
            qs = qs.order_by('id')

        status = params.get('status', 'all')
        if status == 'active':
            qs = qs.filter(is_active=True)
        elif status == 'inactive':
            qs = qs.filter(is_active=False)

        search = params.get('search')
        if search:
            qs = qs.filter(title__icontains=search)

        return qs

    def get(self, request, *args, **kwargs):
        return self.list(request)


class PettyCashFundDetail(PermissionMixin, DetailViewMixin, TemplateView):
    permissions = ('accounting.view_pettycashfund',)
    template_name = 'accounting/petty_cash_fund/detail.html'

    def additional_context(self):
        fund = self.obj
        transactions = fund.get_transactions()

        context = {
            'all_holders': models.PettyCashHolder.objects.filter(user__is_active=True).select_related('user'),
            'total_income': transactions.filter(transaction_type='income').aggregate(total=Sum('amount'))['total'] or 0,
            'total_expense': transactions.filter(transaction_type='expense').aggregate(total=Sum('amount'))[
                                 'total'] or 0,
        }

        # Expense(Invoice Cost)
        total_expense_week = \
            transactions.this_week().filter(transaction_type='expense').aggregate(total=Sum('amount'))[
                'total'] or 0
        total_expense_month = \
            transactions.this_month().filter(transaction_type='expense').aggregate(total=Sum('amount'))[
                'total'] or 0
        total_expense = transactions.filter(transaction_type='expense').aggregate(total=Sum('amount'))[
                            'total'] or 0

        if total_expense > 0:
            # Weekly
            week_ratio = total_expense_week / total_expense
            week_expense_percentage = week_ratio * 100
            # Monthly
            month_ratio = total_expense_month / total_expense
            month_expense_percentage = month_ratio * 100
        else:
            week_expense_percentage = 0
            month_expense_percentage = 0

        context.update({
            'total_expense_week': total_expense_week,
            'total_expense_month': total_expense_month,
            'week_expense_percentage': week_expense_percentage,
            'month_expense_percentage': month_expense_percentage
        })

        # Income
        total_income_week = transactions.this_week().filter(
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_income_month = transactions.this_month().filter(
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0

        total_income = transactions.filter(
            transaction_type='income'
        ).aggregate(total=Sum('amount'))['total'] or 0

        if total_income > 0:
            # Weekly
            week_ratio = total_income_week / total_income
            week_income_percentage = week_ratio * 100

            # Monthly
            month_ratio = total_income_month / total_income
            month_income_percentage = month_ratio * 100
        else:
            week_income_percentage = 0
            month_income_percentage = 0

        context.update({
            'total_income_week': total_income_week,
            'total_income_month': total_income_month,
            'week_income_percentage': week_income_percentage,
            'month_income_percentage': month_income_percentage,
        })

        # Income Chart
        monthly_income_qs = (
            transactions.filter(transaction_type='income')
            .annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
        )

        monthly_income_map = {
            item['month']: float(item['total']) for item in monthly_income_qs
        }

        monthly_income = []
        for m in range(1, 13):
            monthly_income.append(monthly_income_map.get(m, 0) or 0)

        context.update({
            'monthly_income': monthly_income,
        })

        # Expense Chart
        monthly_expense_qs = (
            transactions
            .filter(transaction_type='expense')
            .annotate(month=ExtractMonth('date'))
            .values('month')
            .annotate(total=Sum('amount'))
        )

        monthly_expense_map = {
            item['month']: float(item['total']) for item in monthly_expense_qs
        }

        monthly_expense = []
        for m in range(1, 13):
            monthly_expense.append(monthly_expense_map.get(m, 0) or 0)

        context.update({
            'monthly_expense': monthly_expense,
        })

        return context

    def get_instance(self):
        user = self.request.user
        if user.is_common_user:
            return get_object_or_404(models.PettyCashFund.objects.prefetch_related('holders__user'),
                                     id=self.kwargs['pk'], holders__user__in=[user])

        return get_object_or_404(models.PettyCashFund.objects.prefetch_related('holders__user'), id=self.kwargs['pk'])


class PettyCashTransactionAttachDocCreate(PermissionMixin, CreateViewMixin, TemplateView):
    permissions = ('accounting.add_pettycashtransactiondocument',)
    form = forms.PettyCashTransactionAttachDocCreateForm

    def additional_data(self):
        return {
            'created_by': self.request.user
        }

    def post(self, request):
        return self.create(request)


class PettyCashTransactionStatusCreate(PermissionMixin, CreateViewMixin, TemplateView):
    permissions = ('accounting.add_pettycashtransactionstatus',)
    form = forms.PettyCashTransactionStatusCreateForm

    def additional_data(self):
        return {
            'created_by': self.request.user
        }

    def post(self, request):
        return self.create(request)


class PettyCashTransactionUpdate(PermissionMixin, UpdateViewMixin, View):
    permissions = ('accounting.change_pettycashtransaction',)
    form = forms.PettyCashTransactionUpdateForm

    def post(self, request, *args, **kwargs):
        return self.update(request)

    def additional_data(self):
        return {
            'created_by': self.request.user
        }

    def get_instance(self):
        obj = get_object_or_404(models.PettyCashTransaction, id=self.kwargs['pk'])
        if obj.is_approved:
            raise PermissionDenied
        return obj


class PettyCashTransactionCreate(PermissionMixin, CreateViewMixin, TemplateView):
    permissions = ('accounting.add_pettycashtransaction',)
    template_name = 'accounting/petty_cash_transaction/create.html'
    form = forms.PettyCashTransactionCreateForm

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)

        if user.is_admin:
            context.update({
                'petty_cash_holders': models.PettyCashHolder.objects.filter(user__is_active=True).select_related(
                    'user'),
                'petty_cash_funds': models.PettyCashFund.objects.filter(is_active=True)
            })
        else:
            context.update({
                'holder': user.holder,
                'petty_cash_funds': user.holder.funds
            })
        return context

    def additional_data(self):
        return {
            'created_by': self.request.user
        }

    def post(self, request):
        return self.create(request)


class PettyCashTransactionList(LoginRequiredMixin, ListViewMixin, TemplateView):
    template_name = 'accounting/petty_cash_transaction/list.html'
    page_size = 20

    def additional_context(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_admin:
            context.update({
                'petty_cash_funds': models.PettyCashFund.objects.filter(is_active=True)
            })
        else:
            context.update({
                'petty_cash_funds': user.holder.funds
            })

        return context

    def get_queryset(self):
        qs = models.PettyCashTransaction.objects.all()
        user = self.request.user

        if user.is_common_user:
            qs = qs.filter(holder__user=user)
        qs = qs.select_related('fund', 'holder__user')
        qs = self.filter(qs).distinct()
        return qs

    def filter(self, qs):
        params = self.request.GET

        sort_by = params.get('sort_by', 'latest')
        if sort_by == 'latest':
            qs = qs.order_by('-id')
        else:
            qs = qs.order_by('id')

        fund = params.get('fund', 'all')
        if not fund == 'all' and fund.isdigit():
            qs = qs.filter(fund__id=fund)

        search = params.get('search')
        if search:
            lookup = Q(reference_number__icontains=search) | Q(date__icontains=search)
            qs = qs.filter(lookup)

        return qs

    def get(self, request, *args, **kwargs):
        return self.list(request)


class PettyCashTransactionDetail(PermissionMixin, DetailViewMixin, TemplateView):
    permissions = ('accounting.view_pettycashtransaction',)
    template_name = 'accounting/petty_cash_transaction/detail.html'

    def get_instance(self):
        return get_object_or_404(models.PettyCashTransaction, id=self.kwargs['pk'])


class DocumentCreate(PermissionMixin, CreateViewMixin, TemplateView):
    permissions = ('accounting.add_document',)
    template_name = 'accounting/document/create.html'
    form = forms.DocumentCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'users': User.objects.filter(is_active=True).exclude(id=self.request.user.id)
        })
        return context

    def additional_data(self):
        return {
            'uploaded_by': self.request.user
        }

    def post(self, request):
        return self.create(request)


class DocumentUpdate(PermissionMixin, UpdateViewMixin, View):
    permissions = ('accounting.change_document',)
    form = forms.DocumentUpdateForm

    def additional_data(self):
        return {
            'uploaded_by': self.request.user
        }

    def post(self, request, *args, **kwargs):
        return self.update(request)

    def get_instance(self):
        obj = get_object_or_404(models.Document, id=self.kwargs['pk'])
        if obj.is_fully_approved:
            raise PermissionDenied
        return obj


class DocumentList(LoginRequiredMixin, ListViewMixin, TemplateView):
    template_name = 'accounting/document/list.html'
    page_size = 20

    def get_queryset(self):
        qs = models.Document.objects.all()
        user = self.request.user
        if user.is_common_user:
            lookup = Q(uploaded_by=user) | Q(required_approvers__in=[user])
            qs = qs.filter(lookup)
        qs = qs.select_related('uploaded_by').prefetch_related('required_approvers')
        qs = self.filter(qs).distinct()
        return qs

    def filter(self, qs):
        params = self.request.GET

        sort_by = params.get('sort_by', 'latest')
        if sort_by == 'latest':
            qs = qs.order_by('-id')
        else:
            qs = qs.order_by('id')

        status = params.get('status', 'all')
        if not status == 'all':
            latest_status_subquery = models.DocumentStatus.objects.filter(document=OuterRef('pk')).order_by(
                '-created_at').values('status')[:1]
            qs = qs.annotate(
                latest_status=Subquery(latest_status_subquery)
            ).filter(latest_status=status)

        search = params.get('search')
        if search:
            lookup = Q(title__icontains=search)
            qs = qs.filter(lookup)

        return qs

    def get(self, request, *args, **kwargs):
        return self.list(request)


class DocumentDetail(PermissionMixin, DetailViewMixin, TemplateView):
    permissions = ('accounting.view_document',)
    template_name = 'accounting/document/detail.html'

    def additional_context(self, **kwargs):
        return {
            'users': User.objects.all(),
            'can_create_status': self.obj.can_create_status(self.request.user)
        }

    def get_instance(self):
        return get_object_or_404(models.Document, id=self.kwargs['pk'])


class DocumentStatusCreate(PermissionMixin, CreateViewMixin, View):
    permissions = ('accounting.add_documentstatus',)
    form = forms.DocumentStatusCreateForm

    def additional_data(self):
        return {
            'created_by': self.request.user
        }

    def post(self, request):
        return self.create(request)
