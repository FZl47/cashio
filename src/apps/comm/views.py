from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models import Q

from apps.core.auth.permissions.mixins import PermissionMixin
from apps.core.utils import get_space_detail_cached
from apps.core.views.mixins import CreateViewMixin, DetailViewMixin, DeleteViewMixin

from . import models, forms

User = get_user_model()


class Index(PermissionMixin, TemplateView):
    permissions = ('comm.view_resourcebase',)
    template_name = 'comm/index.html'

    def get_context_data(self, **kwargs):
        total_disk_space, used_disk_space, free_disk_space = get_space_detail_cached(settings.MEDIA_ROOT)
        free_disk_space_percent = round((free_disk_space / total_disk_space) * 100, 2)

        user = self.request.user
        resources = models.ResourceBase.objects.filter(
            Q(created_by=user) | Q(shared_with__in=[user])).distinct()

        resources_pinned = resources.filter(resourcepin__isnull=False, resourcepin__user=user)
        resources_pinned_ids = resources_pinned.values_list('id', flat=True)

        # Filter resources
        search_param = self.request.GET.get('search')
        if search_param:
            resources = resources.filter(Q(name__icontains=search_param))

        return {
            'total_disk_space': round(total_disk_space / (1024 ** 2), 2),
            'used_disk_space': round(used_disk_space / (1024 ** 2), 2),
            'free_disk_space': round(free_disk_space / (1024 ** 2), 2),
            'free_disk_space_percent': free_disk_space_percent,
            'used_disk_space_percent': round(100 - free_disk_space_percent, 2),

            'resources': resources.select_subclasses(),
            'resource_files': resources.filter(fileresource__isnull=False),
            'resource_folders': resources.filter(folderresource__isnull=False),
            'resources_pinned': resources_pinned.select_subclasses(),
            'resources_pinned_ids': resources_pinned_ids,

            'users': User.objects.filter(is_active=True)
        }


class ResourcePinChangeState(PermissionMixin, View):
    permissions = ('comm.view_resourcebase',)

    def get_redirect_url(self):
        return self.request.META.get('HTTP_REFERER', reverse_lazy('communication:index'))

    def get(self, request, pk):
        user = request.user
        resource = get_object_or_404(models.ResourceBase, id=pk)
        resource_pin = models.ResourcePin.objects.filter(resource=resource, user=user).first()
        if resource_pin:
            resource_pin.delete()
        else:
            models.ResourcePin.objects.create(resource=resource, user=user)

        return redirect(self.get_redirect_url())


class ResourceFolderCreate(PermissionMixin, CreateViewMixin, View):
    permissions = ('comm.add_folderresource',)
    form = forms.ResourceFolderCreateForm

    def post(self, request):
        return self.create(request)

    def additional_data(self):
        return {
            'created_by': self.request.user
        }


class ResourceFileCreate(PermissionMixin, CreateViewMixin, View):
    permissions = ('comm.add_filerresource',)
    form = forms.ResourceFileCreateForm

    def post(self, request):
        return self.create(request)

    def additional_data(self):
        raw_files_name = self.data.getlist('file_name')
        raw_files = list(models.FileRaw.objects.filter(name__in=raw_files_name))
        self.data.setlist('files', raw_files)
        return {
            'created_by': self.request.user
        }


class ResourceDetail(PermissionMixin, DetailViewMixin, TemplateView):
    permissions = ('comm.view_resource',)
    template_name = 'comm/resource/detail.html'

    def get_instance(self):
        pk = self.kwargs['pk']
        resource = models.ResourceBase.objects.get_subclass(id=pk)
        if not resource:
            raise Http404

        # Check user permission's
        user = self.request.user

        if not resource.created_by == user and not resource.shared_with.all().filter(
                id=user.id).first() and not user.is_superuser:
            raise Http404

        # Create resource event
        models.ResourceEvent.objects.create(
            resource=resource,
            user=user,
            action='open'
        )

        return resource

    def additional_context(self):
        user = self.request.user
        if not self.obj.type == 'folder':
            return None
        return {
            'resource_children': self.obj.get_children(shared_with=user),
            'resource_files': self.obj.get_resource_files(shared_with=user),
        }


class ResourceDelete(PermissionMixin, DeleteViewMixin, View):
    permissions = ('comm.delete_resourcebase',)

    def get_instance(self, pk):
        try:
            obj = models.ResourceBase.objects.get_subclass(id=pk)
        except models.ResourceBase.DoesNotExist:
            raise Http404

        user = self.request.user

        if not obj.created_by == user and not user.is_superuser:
            raise Http404

        return obj

    def get_redirect_url(self):
        parent = self.obj.parent
        if not parent:
            return reverse_lazy('communication:index')
        return parent.get_absolute_url()


@method_decorator(csrf_exempt, name='dispatch')
class FileRawUpload(PermissionMixin, View):
    permissions = ('comm.add_fileresource',)
    form = forms.FileRawUploadForm

    def post(self, request):
        f = self.form(files=request.FILES)
        if not f.is_valid():
            return JsonResponse({
                'status': 'error'
            })
        fm = f.save()

        return JsonResponse({
            'status': 'success',
            'file_name': fm.name
        })
