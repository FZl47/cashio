from django.utils.translation import gettext_lazy as _
from django.db import transaction
from django import forms

from . import models


class PettyCashTransactionStatusCreateForm(forms.ModelForm):
    class Meta:
        model = models.PettyCashTransactionStatus
        fields = '__all__'


class PettyCashTransactionCreateForm(forms.ModelForm):
    attached_file = forms.FileField(label=_('Attach Files'), required=False)

    class Meta:
        model = models.PettyCashTransaction
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        fund = cleaned_data.get('fund')
        amount = cleaned_data.get('amount')
        transaction_type = cleaned_data.get('transaction_type')

        if fund and transaction_type == 'expense':
            if fund.balance < amount:
                self.add_error('', _("Not enough balance in fund '%(fund)s' (Current balance: %(balance)s).") % {
                    'fund': fund.title, 'balance': fund.balance})

        return cleaned_data

    def save(self, commit=True):
        transaction = super().save(commit=commit)

        files = self.files.getlist('attached_file')
        for file in files:
            models.PettyCashTransactionDocument.objects.create(
                transaction=transaction,
                file=file,
                title=file.name,
                created_by=transaction.created_by
            )

        return transaction


class PettyCashTransactionUpdateForm(forms.ModelForm):
    class Meta:
        model = models.PettyCashTransaction
        exclude = ('amount', 'fund', 'holder')


class PettyCashTransactionAttachDocCreateForm(forms.ModelForm):
    class Meta:
        model = models.PettyCashTransactionDocument
        fields = '__all__'


class DocumentCreateForm(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = '__all__'

    def save(self, commit=True):
        with transaction.atomic():
            document = super().save(commit=commit)
            approvers = self.data.getlist('approvers')
            priorities = self.data.getlist('priority')

            if approvers and priorities:
                for i, approver in enumerate(approvers):
                    models.DocumentApprover.objects.create(
                        document=document,
                        priority=priorities[i],
                        user_id=approver,
                    )

            return document


class DocumentUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = '__all__'


class DocumentStatusCreateForm(forms.ModelForm):
    class Meta:
        model = models.DocumentStatus
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        document = cleaned_data.get('document')
        user = cleaned_data.get('created_by')
        if document and not document.can_create_status(user):
            self.add_error('', _(f"Cannot Create Status"))

        return cleaned_data


class PettyCashFundCreateForm(forms.ModelForm):
    class Meta:
        model = models.PettyCashFund
        fields = '__all__'


class PettyCashFundUpdateForm(forms.ModelForm):
    class Meta:
        model = models.PettyCashFund
        fields = '__all__'
