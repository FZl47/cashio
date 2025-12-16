from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse_lazy


class HealthCheckMiddleWare:
    """
        A middleware to Check health project and third parties
    """
    _not_healthy_url = getattr(settings, 'NOT_HEALTHY_URL', reverse_lazy('public:health_fail'))
    _checkers = [
        'check_third_parties',
        'check_base'
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not self.check():
            path = str(request.path)
            if path != self._not_healthy_url:
                return redirect(self._not_healthy_url)
        response = self.get_response(request)
        return response

    @classmethod
    def check_third_parties(cls) -> bool:
        """
            Check third parties
        :return: bool
        """
        # TODO: must be completed
        return True

    @classmethod
    def check_base(cls) -> bool:
        """
            Check base project(apps | db connection and ...)
        :return: bool
        """
        # TODO: must be completed
        return True

    @classmethod
    def check(cls) -> bool:
        """
            Get all checkers
        :return: bool
        """
        for ct in cls._checkers:
            checker = getattr(cls, ct, None)
            if not checker():
                return False
        return True
