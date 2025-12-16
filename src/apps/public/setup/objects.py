from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission, ContentType

from apps.public import models


def initial_setup_config_object():
    models.SetupConfig.objects.create()


def initial_setup_journal_status_config_object():
    # Create default journal status permissions config
    ct = ContentType.objects.get(app_label='accounting', model='journalentrystatus')
    # STEP 1.
    permission, created = Permission.objects.get_or_create(
        codename='review_journal_step_one_permission',
        defaults={
            'name': _('Review journal step one'),
            'content_type': ct,
        }
    )
    step_one_status_config = models.JournalStatusConfig.objects.create(number_of_step=1)
    if created:
        step_one_status_config.permissions.add(permission)

    # STEP 2.
    # permission, created = Permission.objects.get_or_create(
    #     codename='review_journal_step_two_permission',
    #     defaults={
    #         'name': _('Review journal step two'),
    #         'content_type': ct,
    #     }
    # )
    # step_two_status_config = models.JournalStatusConfig.objects.create(number_of_step=2)
    # if created:
    #     step_two_status_config.permissions.add(permission)
