import uuid

from django.utils.translation import gettext_lazy as _
from django.db import models
from django.urls import reverse_lazy

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
        return self.created_at.strftime('%m-%d')

class ResourceBase(BaseModel):
    type = None  # ABC
    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    size = models.PositiveBigIntegerField(default=0, blank=True)  # KB
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

    @property
    def extension(self):
        files = self.files.all()
        if not files:
            return 'empty'

        if files.count() > 1:
            return 'multiple_files'
        return files.first().extension


class FolderResource(MPTTModel, ResourceBase):
    type = models.CharField(max_length=7, default='folder')
    file_resources = models.ManyToManyField(FileResource, blank=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)

    @property
    def extension(self):
        return 'folder'

    def get_resource_files(self):
        return self.file_resources.all()

    def get_children(self):
        return super().get_children()
    
    def get_parents(self):
        return super().get_ancestors()