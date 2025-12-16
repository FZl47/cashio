from django.shortcuts import redirect
from django.conf import settings
from django.core.cache import cache

from apps.public.models import SetupConfig


class ProjectIsSetup:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = str(request.path)
        setup_obj = cache.get(SetupConfig.cache_name)
        if not setup_obj:
            setup_obj = SetupConfig.objects.first()
            cache.set('setup_obj', SetupConfig.cache_name, timeout=(3600 * 24 * 30))

        if (not path == settings.SETUP_URL) and not setup_obj:
            return redirect(settings.SETUP_URL)

        response = self.get_response(request)
        return response
