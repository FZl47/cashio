from django.contrib.auth import authenticate, get_user_model, login, logout
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import Permission, Group
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, View
from django.urls import reverse_lazy
from django.contrib import messages

from apps.core.views import (CreateViewMixin, ListViewMixin, DetailViewMixin,
                             DeleteViewMixin, UpdateViewMixin)
from apps.core.auth.permissions import PermissionMixin
from apps.core.forms.utils import form_validate_err
from apps.core.utils import get_client_ip

from . import forms, models

User = get_user_model()


class Login(TemplateView):
    template_name = 'account/login.html'
    form = forms.LoginForm

    def post(self, request):
        data = request.POST
        f = self.form(data)
        if not form_validate_err(request, f):
            return redirect('account:login')

        data = f.cleaned_data
        email = data['email']
        password = data['password']
        user = authenticate(request, username=email, password=password)
        if not user:
            messages.error(request, _('User not found'))
            return redirect('account:login')

        login(request, user)

        # Create login activity
        models.UserLoginActivity.objects.create(
            user=user, ip=get_client_ip(request), agent=request.META['HTTP_USER_AGENT']
        )

        messages.success(request, _('Welcome'))
        return redirect('public:index')


class Logout(View):

    def get(self, request):
        logout(request)
        return redirect('account:login')


class UserCreate(PermissionMixin, CreateViewMixin, TemplateView):
    permissions = ('account.add_user',)
    template_name = 'account/user/create.html'
    form = forms.UserCreateForm

    def post(self, request):
        return self.create(request)

    def additional_data(self):
        return {
            'is_active': True
        }


class UserList(PermissionMixin, ListViewMixin, TemplateView):
    permissions = ('account.view_user',)
    template_name = 'account/user/list.html'

    def get(self, request, *args, **kwargs):
        return self.list(request)

    def get_queryset(self):
        return User.objects.filter(is_superuser=False)


class UserUpdate(PermissionMixin, View, UpdateViewMixin):
    permissions = ('account.change_user',)
    form = forms.UserUpdateForm

    def post(self, request, *args, **kwargs):
        return self.update(request)

    def get_instance(self):
        pk = self.kwargs['pk']
        return get_object_or_404(User, pk=pk)


class UserPermissionUpdate(PermissionMixin, View, UpdateViewMixin):
    permissions = ('account.change_user',)
    form = forms.UserPermissionUpdateForm

    def post(self, request, *args, **kwargs):
        return self.update(request)

    def get_instance(self, queryset=None):
        pk = self.kwargs['pk']
        return get_object_or_404(User, id=pk)


class UserDetail(PermissionMixin, View, DetailViewMixin):
    permissions = ('account.view_user',)
    template_name = 'account/user/detail.html'

    def get_instance(self, queryset=None):
        pk = self.kwargs['pk']
        return get_object_or_404(User, id=pk)

    def additional_context(self):
        return {
            'permission_groups': Group.objects.all()
        }


class UserDelete(PermissionMixin, View, DeleteViewMixin):
    permissions = ('account.delete_user',)
    redirect_url = reverse_lazy('apps.account:user__list')

    def get_instance(self, queryset=None):
        pk = self.kwargs['pk']
        return get_object_or_404(User, id=pk)


class Permissions(PermissionMixin, TemplateView):
    permissions = ('auth.view_permission',)
    template_name = 'account/permissions.html'
    redirect_url = reverse_lazy('apps.account:permissions')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'groups': Group.objects.all(),
            'permissions': Permission.objects.all()
        })
        return context

    def post(self, request):
        data = request.POST
        group_name = data.get('name')
        permission_ids = data.get('permissions', [])

        group, created = Group.objects.get_or_create(name=group_name)

        perms = Permission.objects.filter(id__in=permission_ids)
        group.permissions.set(perms)
        return redirect(self.redirect_url)


class PermissionGroupDelete(PermissionMixin, DeleteViewMixin, View):
    permissions = ('auth.delete_permission',)
    redirect_url = reverse_lazy('apps.account:permissions')

    def post(self, request):
        return self.delete(request)

    def get_instance(self, pk):
        return get_object_or_404(Group, id=pk)
