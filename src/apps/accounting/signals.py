from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction

from . import models


@receiver(post_save, sender=models.PettyCashTransaction)
def update_fund_balance(sender, instance, **kwargs):
    with transaction.atomic():
        fund = models.PettyCashFund.objects.select_for_update().get(id=instance.fund.id)

        if instance.transaction_type == 'income':
            fund.balance += instance.amount
        else:
            if fund.balance < instance.amount:
                return None  # Not enough balance in the fund
            fund.balance -= instance.amount

        fund.save()
