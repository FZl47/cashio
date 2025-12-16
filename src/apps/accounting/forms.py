from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from . import models

class PettyCashTransactionForm(forms.ModelForm):
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
                raise ValidationError(_(
                    f"Not enough balance in fund '{fund.title}' (Current balance: {fund.balance}). "
                ))

        return cleaned_data