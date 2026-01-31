import uuid

from django.utils.translation import gettext_lazy as _, ngettext
from django.db import models
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils import timezone

from mptt.models import MPTTModel, TreeForeignKey

from model_utils.managers import InheritanceManager

from apps.core.models import BaseModel
from apps.core.utils import random_str


def file_raw_src(instance, pth):
    extension = str(pth).split('.')[-1]
    return f'file-management/raw-files/{random_str(20)}.{extension}'


class FileRaw(BaseModel):
    file = models.FileField(upload_to=file_raw_src)
    name = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    extension = models.CharField(max_length=50)
    size = models.FloatField(default=0, blank=True)  # KB


class ResourcePin(BaseModel):
    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    resource = models.ForeignKey('ResourceBase', on_delete=models.CASCADE)


class ResourceEvent(BaseModel):
    ACTIONS = (
        ('open', _('Open')),
        ('download', _('Download')),
    )

    user = models.ForeignKey('account.User', on_delete=models.CASCADE)
    resource = models.ForeignKey('ResourceBase', on_delete=models.CASCADE)
    action = models.CharField(max_length=50, choices=ACTIONS)

    @property
    def date(self):
        now = timezone.now()
        diff = now - self.created_at

        seconds = diff.total_seconds()

        if seconds < 60:
            count = int(seconds)
            return ngettext(
                '%(count)d second ago',
                '%(count)d seconds ago',
                count
            ) % {'count': count}

        minutes = seconds / 60
        if minutes < 60:
            count = int(minutes)
            return ngettext(
                '%(count)d minute ago',
                '%(count)d minutes ago',
                count
            ) % {'count': count}

        hours = minutes / 60
        if hours < 24:
            count = int(hours)
            return ngettext(
                '%(count)d hour ago',
                '%(count)d hours ago',
                count
            ) % {'count': count}

        days = hours / 24
        count = int(days)
        return ngettext(
            '%(count)d day ago',
            '%(count)d days ago',
            count
        ) % {'count': count}


class ResourceBase(BaseModel):
    type = None  # ABC
    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey('account.User', on_delete=models.SET_NULL, null=True)
    shared_with = models.ManyToManyField('account.User', related_name='resource_shared')
    is_active = models.BooleanField(default=True)

    objects = InheritanceManager()

    def last_opened(self):
        return self.resourceevent_set.filter(action='open').order_by('-id').first()

    def get_absolute_url(self):
        return reverse_lazy('communication:resource__detail', args=(self.id,))


class FileResource(ResourceBase):
    type = models.CharField(max_length=5, default='file')
    files = models.ManyToManyField(FileRaw)
    parent = models.ForeignKey('FolderResource', on_delete=models.CASCADE, null=True, blank=True)

    @property
    def extension(self):
        files = self.get_files()
        if not files:
            return 'empty'

        if self.has_multiple:
            return 'multiple_files'
        return files.first().extension

    @property
    def size(self):
        return self.files.aggregate(total_size=Sum('size'))['total_size'] or 0

    @property
    def has_multiple(self):
        return True if self.files.count() > 1 else False

    def get_files(self):
        return self.files.all()


class FolderResource(MPTTModel, ResourceBase):
    type = models.CharField(max_length=7, default='folder')
    parent = TreeForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)

    @property
    def extension(self):
        return 'folder'

    @property
    def size(self):
        return self.get_resource_files().aggregate(total_size=Sum('files__size'))['total_size'] or 0

    def get_resource_files(self, shared_with=None):
        files = self.fileresource_set.all()
        if not shared_with:
            return files
        if shared_with.is_superuser:
            return files

        return files.filter(shared_with__in=[shared_with])

    def get_children(self, shared_with=None):
        children = super().get_children()
        if not shared_with:
            return children
        if shared_with.is_superuser:
            return children

        return children.filter(shared_with__in=[shared_with])

    def get_parents(self):
        return super().get_ancestors()

    def get_parents_self(self):
        return super().get_ancestors(include_self=True)
