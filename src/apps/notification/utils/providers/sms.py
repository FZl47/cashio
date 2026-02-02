import json
import requests

from django.conf import settings

from apps.notification.utils.providers import BaseProvider
from apps.notification.models import NotificationUser


class SmsProvider(BaseProvider):
    """
    SMS notification provider implementation.

    This provider sends SMS notifications using the IPPanel service
    (https://ippanel.com). It supports pattern-based SMS messages
    configured through Django settings.

    The actual sending logic is executed asynchronously via the
    BaseProvider `send` method.
    """

    #: SMS provider configuration loaded from Django settings
    config = settings.IPPANEL_SMS_CONFIG

    def _send(self, notification: NotificationUser) -> None:
        """
        Send an SMS notification to the target user.

        This method prepares the payload based on the notification type,
        validates the recipient phone number, and sends the request to
        the IPPanel API.

        Args:
            notification (NotificationUser):
                Notification instance containing the recipient and
                notification metadata.

        Returns:
            None

        Notes:
            - This method is called internally inside a background thread.
            - Any exceptions related to invalid payload configuration
              are silently ignored (logging can be added later).
        """
        try:
            pattern, data = self._get_payload()
        except (AttributeError, TypeError) as e:
            # TODO: add logging for invalid payload configuration
            return None

        if not data:
            data = {}

        phonenumber = notification.to_user.phonenumber
        if not phonenumber:
            # TODO: add logging for missing phone number
            return None

        phonenumber = str(phonenumber).replace('+', '')

        payload = json.dumps({
            "pattern_code": pattern,
            "originator": self.config['ORIGINATOR'],
            "recipient": phonenumber,
            "values": data
        })

        headers = {
            "Authorization": f"AccessKey {self.config['API_KEY']}",
            "Content-Type": "application/json"
        }

        requests.request(
            method='POST',
            url=self.config['API_URL'],
            headers=headers,
            data=payload
        )

    def _get_payload(self):
        """
        Resolve the payload builder method based on notification type.

        This method dynamically maps the notification type to a
        corresponding payload method following the naming convention:

            `_payload_<notification.type>`

        Args:
            notification (NotificationUser):
                Notification instance containing the type identifier.

        Returns:
            tuple:
                A tuple containing:
                - pattern code (str)
                - payload data (dict)

        Raises:
            AttributeError:
                If no matching payload method exists.
        """
        return getattr(self, f'_payload_{self.notification.type}')()

    def _payload_test(self):
        """
        Test payload definition for SMS notifications.

        This method is an example payload builder and should match
        a valid pattern configured in the IPPanel dashboard.

        Returns:
            tuple:
                - pattern code (str)
                - pattern values (dict)
        """
        return '#testpattern', {'key': 'value'}
