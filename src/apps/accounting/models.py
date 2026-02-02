from typing import Any

from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone
from django.urls import reverse_lazy
from django.core.validators import MinValueValidator

from django_jalali.db import models as jmodels

from datetime import timedelta

from apps.core.models import BaseModel
from apps.notification.utils import NotificationModelMixin


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


class PettyCashFund(NotificationModelMixin, BaseModel):
    title = models.CharField(max_length=150)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    holders = models.ManyToManyField('PettyCashHolder', related_name='petty_cash_funds')
    is_active = models.BooleanField(default=True)

    _notif_title = _('A new Petty Cash Fund has been created.')
    _notif_type = 'petty_cash_fund_created'

    def __str__(self):
        return self.title

    def get_notif_to_users(self):
        return NotificationModelMixin.admin_users()

    def get_absolute_url(self):
        return reverse_lazy('accounting:petty_cash_fund__detail', args=(self.id,))

    def get_holders(self):
        return self.holders.all().select_related('user')

    def get_transactions(self):
        return self.pettycashtransaction_set.all().select_related('holder__user')


class PettyCashHolder(BaseModel):
    user = models.OneToOneField('account.User', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user}'

    @property
    def funds(self):
        return self.petty_cash_funds.all()

    def get_absolute_url(self):
        return self.user.get_absolute_url()


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


class PettyCashTransaction(NotificationModelMixin, BaseModel):
    fund = models.ForeignKey(PettyCashFund, on_delete=models.PROTECT)
    holder = models.ForeignKey(PettyCashHolder, on_delete=models.PROTECT)
    created_by = models.ForeignKey('account.User', on_delete=models.PROTECT)
    transaction_type = models.CharField(max_length=10, choices=PettyCashTransactionType.choices)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.TextField(blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    date = jmodels.jDateField(null=True, blank=True)

    _notif_title = _('A new transaction has been created.')
    _notif_type = 'petty_cash_fund_transaction_created'

    def get_notif_to_users(self):
        return NotificationModelMixin.admin_users()

    def get_notif_kwargs(self) -> dict:
        return {
            'fund_title': self.fund.title
        }

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
        return self.document.all()


class PettyCashTransactionDocument(NotificationModelMixin, BaseModel):
    transaction = models.ForeignKey(
        PettyCashTransaction,
        on_delete=models.CASCADE,
        related_name='document'
    )
    created_by = models.ForeignKey('account.User', on_delete=models.PROTECT)

    file = models.FileField(upload_to='petty_cash_docs/')
    title = models.CharField(max_length=150, blank=True, null=True)

    _notif_title = _('A new document has been added to the transaction.')
    _notif_type = 'petty_cash_fund_transaction_doc_created'

    def get_notif_to_users(self) -> Any:
        return list(NotificationModelMixin.admin_users()).append(self.created_by)

    def __str__(self):
        return self.title or self.file.name

    def get_file_url(self):
        try:
            return self.file.url
        except AttributeError:
            return None


class PettyCashTransactionStatus(NotificationModelMixin, BaseModel):
    STATUS_TYPES = (
        ('pending', _('Pending')),
        ('rejected', _('Rejected')),
        ('approved', _('Approved')),
    )
    transaction = models.ForeignKey(PettyCashTransaction, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_TYPES)
    note = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey('account.User', on_delete=models.CASCADE)

    _notif_title = _('The transaction status has changed.')
    _notif_type = 'petty_cash_fund_transaction_status_changed'

    def get_notif_to_users(self) -> Any:
        return list(NotificationModelMixin.admin_users()).extend([self.created_by, self.transaction.created_by])

    def __str__(self):
        return f'{self.get_status_display()} / {self.created_by}'


class DocumentApprover(BaseModel):
    priority = models.IntegerField(validators=[MinValueValidator(0)])
    document = models.ForeignKey('Document', on_delete=models.CASCADE, related_name='required_approvers')
    user = models.ForeignKey('account.User', on_delete=models.CASCADE,
                             help_text=_("If selected, these users must approve the document."))


class Document(NotificationModelMixin, BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='document/%Y/%m/%d/')
    uploaded_by = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='uploaded_documents')

    _notif_title = _('A new document has been submitted that requires your approval.')
    _notif_type = 'document_has_been_added'

    def get_notif_to_users(self) -> Any:
        return self.required_approvers.all()

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

    def pending_required_approvers(self):
        return self.required_approvers.exclude(
            user__in=self.statuses.exclude(status='pending').values_list('created_by', flat=True))

    def can_create_status(self, user):
        if self.status_label != 'pending':
            return False

        if not user.has_perm('accounting.add_documentstatus'):
            return False

        try:
            approver = self.required_approvers.get(user=user)
        except DocumentApprover.MultipleObjectsReturned:
            approver = self.required_approvers.filter(user=user).order_by('-priority').first()
        except DocumentApprover.DoesNotExist:
            return False

        if self.statuses.filter(status='rejected',
                                created_by__in=self.required_approvers.filter(priority__lt=approver.priority).values(
                                    'user')).exists():
            return False

        if self.statuses.filter(created_by=user, status='accepted').exists():
            return False

        pending_approvers = self.required_approvers.exclude(
            user__in=self.statuses.filter(status='accepted').values_list('created_by', flat=True)).order_by('priority')

        if not pending_approvers.exists():
            return False
        #
        # if pending_approvers.first().user != user:
        #     return False

        return True


class DocumentStatus(NotificationModelMixin, BaseModel):
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    )

    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    created_by = models.ForeignKey('account.User', on_delete=models.CASCADE, related_name='document_approvals')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    note = models.TextField(blank=True)

    _notif_type = 'document_status_has_been_changed'

    def get_notif_to_users(self) -> Any:
        return [self.document.uploaded_by]

    def get_notif_title(self) -> Any:
        return _('Document %(title)s has been %(status)s by %(user)s') % {
            'title': self.document.title,
            'status': self.get_status_display(),
            'user': self.created_by.get_full_name()
        }

    def __str__(self):
        return f'{self.created_by} - {self.document.title} ({self.get_status_display()})'


class DocumentApprovalProcessGroup(BaseModel):
    title = models.CharField(max_length=100)
    users = models.ManyToManyField('account.User')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

    def get_users(self):
        return self.users.all()

    def get_approver_users(self):
        return self.documentapprovalprocessgroupuser_set.all().order_by('priority')


class DocumentApprovalProcessGroupUser(BaseModel):
    group = models.ForeignKey(DocumentApprovalProcessGroup, on_delete=models.CASCADE)
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    priority = models.IntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f'{self.group} / {self.user}({self.priority})'
