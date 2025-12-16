from django.shortcuts import redirect
from django.conf import settings


class UserIsAuthenticated:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = str(request.path)
        if request.user.is_anonymous:
            if not any([str(url) in path for url in settings.EXCEPT_USER_AUTH_URLS]):
                return redirect(settings.LOGIN_URL)
        response = self.get_response(request)
        return response
