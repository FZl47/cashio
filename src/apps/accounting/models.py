from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from django.urls import reverse_lazy

from django_jalali.db import models as jmodels

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
    holders = models.ManyToManyField('PettyCashHolder', related_name='petty_cash_funds')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class PettyCashHolder(BaseModel):
    user = models.OneToOneField('account.User', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}'

    @property
    def funds(self):
        return self.petty_cash_funds.all()


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
    created_by = models.ForeignKey('account.User', on_delete=models.PROTECT)
    transaction_type = models.CharField(max_length=10, choices=PettyCashTransactionType.choices)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    date = jmodels.jDateField(null=True, blank=True)

    objects = PettyCashTransactionQuerySet.as_manager()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Create Default Status
        PettyCashTransactionStatus.objects.create(
            transaction=self,
            status='pending',
            note=_('Created Automatically by System'),
            created_by=self.created_by
        )

    def __str__(self):
        return f'{self.transaction_type} - {self.amount}'

    @property
    def statuses(self):
        return self.pettycashtransactionstatus_set.all()

    def get_absolute_url(self):
        return reverse_lazy('accounting:petty_cash_transaction__detail', args=(self.id,))

    @property
    def is_approved(self):
        return self.statuses.filter(status='approved').exists()

    def files(self):
        return self.documents.all()


class PettyCashTransactionDocument(BaseModel):
    transaction = models.ForeignKey(
        PettyCashTransaction,
        on_delete=models.CASCADE,
        related_name='document'
    )
    created_by = models.ForeignKey('account.User', on_delete=models.PROTECT)

    file = models.FileField(upload_to='petty_cash_docs/')
    title = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.title or self.file.name

    def get_file_url(self):
        try:
            return self.file.url
        except AttributeError:
            return None


class PettyCashTransactionStatus(BaseModel):
    STATUS_TYPES = (
        ('pending', _('Pending')),
        ('rejected', _('Rejected')),
        ('approved', _('Approved')),
    )
    transaction = models.ForeignKey(PettyCashTransaction, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_TYPES)
    note = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey('account.User', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.get_status_display()} / {self.created_by}'


class Document(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='document/%Y/%m/%d/')
    uploaded_by = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='uploaded_documents')
    required_approvers = models.ManyToManyField(
        'account.User', blank=True, related_name='documents_to_approve',
        help_text=_("If selected, these users must approve the document.")
    )

    class Meta:
        ordering = ('-id',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Create default status
        DocumentStatus.objects.create(
            created_by=self.uploaded_by,
            document=self,
            status='pending',
            note=_('Created Automatically by System')
        )

    @property
    def statuses(self):
        return self.documentstatus_set.all()

    @property
    def approved_statuses(self):
        return self.statuses.filter(status='approved')

    @property
    def is_fully_approved(self):
        if not self.required_approvers.exists():
            return True
        return self.statuses.filter(status='approved').count() == self.required_approvers.count()

    @property
    def status_label(self):
        if not self.required_approvers.exists():
            return 'no_approval_needed'
        if self.is_fully_approved:
            return 'approved'
        if self.statuses.filter(status='rejected').exists():
            return 'rejected'
        return 'pending'

    def get_absolute_url(self):
        return reverse_lazy('accounting:document__detail', args=(self.id,))


class DocumentStatus(BaseModel):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    )

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    created_by = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='document_approvals')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(blank=True)

    def __str__(self):
        return f'{self.created_by} - {self.document.title} ({self.get_status_display()})'
