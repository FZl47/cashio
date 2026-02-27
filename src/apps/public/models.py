from django.db import models

from apps.core.models import BaseModel


class YarMalliSettings(BaseModel):
    api_key = models.CharField(max_length=128)

    """
      linked to Yarmalli users
      value like => <full_name>-<id>
    """
    journal_author = models.CharField(max_length=256)

    """
        linked to Yarmalli accounts
        value like => <title>-<id>
    """
    acc_debit_transaction = models.CharField(max_length=256)
    acc_credit_transaction = models.CharField(max_length=256)

    def get_journal_author_name(self):
        return self.journal_author.rsplit('-', 1)[0]

    def get_journal_author_id(self):
        return self.journal_author.rsplit('-', 1)[-1]

    def acc_debit_transaction_name(self):
        return self.acc_debit_transaction.rsplit('-', 1)[0]

    def acc_debit_transaction_id(self):
        return self.acc_debit_transaction.rsplit('-', 1)[-1]

    def acc_credit_transaction_name(self):
        return self.acc_credit_transaction.rsplit('-', 1)[0]

    def acc_credit_transaction_id(self):
        return self.acc_credit_transaction.rsplit('-', 1)[-1]
