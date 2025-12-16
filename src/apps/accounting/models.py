from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone

from datetime import timedelta

from apps.core.models import BaseModel


class Company(BaseModel):
    SCALE_TYPES = (
        ('small', _('Small')),
        ('medium', _('Medium')),
        ('large', _('Large')),
    )

    name = models.CharField(max_length=256)
    scale = models.CharField(max_length=20, choices=SCALE_TYPES)

    def __str__(self):
        return self.name


class PettyCashFund(BaseModel):
    title = models.CharField(max_length=150)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    holders = models.ManyToManyField('account.User', related_name='petty_cash_funds')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class PettyCashHolder(BaseModel):
    user = models.OneToOneField('account.User', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}'


class PettyCashTransactionType(models.TextChoices):
    EXPENSE = 'expense', _('Expense')
    INCOME = 'income', _('Income')


class PettyCashTransactionQuerySet(models.QuerySet):

    def this_week(self):
        now = timezone.now()
        start = now - timedelta(days=now.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        return self.filter(created_at__gte=start, created_at__lte=now)

    def this_month(self):
        now = timezone.now()
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return self.filter(created_at__gte=start, created_at__lte=now)


class PettyCashTransaction(BaseModel):
    fund = models.ForeignKey(PettyCashFund, on_delete=models.PROTECT)
    holder = models.ForeignKey(PettyCashHolder, on_delete=models.PROTECT)
    transaction_type = models.CharField(max_length=10, choices=PettyCashTransactionType.choices)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    reference_number = models.CharField(max_length=100, blank=True)

    objects = PettyCashTransactionQuerySet.as_manager()

    def __str__(self):
        return f'{self.transaction_type} - {self.amount}'

    def files(self):
        return self.documents.all()


class PettyCashTransactionDocument(BaseModel):
    transaction = models.ForeignKey(
        PettyCashTransaction,
        on_delete=models.CASCADE,
        related_name='documents'
    )

    file = models.FileField(upload_to='petty_cash_docs/')
    title = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return self.title or self.file.name

    def get_file_url(self):
        try:
            return self.file.url
        except AttributeError:
            return None