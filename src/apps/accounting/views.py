from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView, View
from django.db.models import Q, OuterRef, Subquery
from django.contrib.auth import get_user_model

from apps.core.views import CreateViewMixin, ListViewMixin, DetailViewMixin, UpdateViewMixin
from apps.core.auth.permissions.mixins import PermissionMixin

from . import forms, models

User = get_user_model()


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
                'petty_cash_holders': models.PettyCashHolder.objects.all(),
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


class PettyCashTransactionList(PermissionMixin, ListViewMixin, TemplateView):
    permissions = ('accounting.view_pettycashtransaction',)
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
        qs = self.filter(qs)
        return qs

    def filter(self, qs):
        params = self.request.GET

        sort_by = params.get('sort_by')
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
            'users': User.objects.filter(is_active=True)
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


class DocumentList(PermissionMixin, ListViewMixin, TemplateView):
    permissions = ('accounting.view_document',)
    template_name = 'accounting/document/list.html'
    page_size = 20

    def get_queryset(self):
        qs = models.Document.objects.all()
        user = self.request.user
        if user.is_common_user:
            lookup = Q(uploaded_by=user) | Q(required_approvers__in=[user])
            qs = qs.filter(lookup)
        qs = qs.select_related('uploaded_by').prefetch_related('required_approvers')
        qs = self.filter(qs)
        return qs

    def filter(self, qs):
        params = self.request.GET

        sort_by = params.get('sort_by')
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'users': User.objects.all()
        })
        return context

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
