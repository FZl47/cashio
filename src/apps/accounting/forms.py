from django import forms
from django.utils.translation import gettext_lazy as _

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

        if transaction_type == 'expense':
            if fund.balance < amount:
                self.add_error('Amount',
                               f"Not enough balance in fund '{fund.title}' (Current balance: {fund.balance}).")

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

class DocumentUpdateForm(forms.ModelForm):
    class Meta:
        model = models.Document
        fields = '__all__'


class DocumentStatusCreateForm(forms.ModelForm):
    class Meta:
        model = models.DocumentStatus
        fields = '__all__'
