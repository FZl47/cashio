from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission

from . import models

admin.site.register(Permission)
admin.site.register(models.UserLoginActivity)


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = (
        'id',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
        'profile_is_completed',
        'created_at',
    )

    list_filter = (
        'role',
        'is_active',
        'is_staff',
        'is_superuser',
    )

    search_fields = (
        'email',
        'first_name',
        'last_name',
        'phonenumber',
    )

    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'email',
                'password',
            )
        }),
        (_('Personal info'), {
            'fields': (
                'first_name',
                'last_name',
                'phonenumber',
            )
        }),
        (_('Role & Permissions'), {
            'fields': (
                'role',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Important dates'), {
            'fields': (
                'last_login',
                'created_at',
                'updated_at',
            )
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'role',
                'is_active',
                'is_staff',
            ),
        }),
    )

    readonly_fields = (
        'last_login',
        'created_at',
        'updated_at',
    )

    filter_horizontal = (
        'groups',
        'user_permissions',
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'username' in form.base_fields:
            form.base_fields.pop('username')
        return form

