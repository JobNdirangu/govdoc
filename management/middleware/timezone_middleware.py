# myapp/middleware/timezone_middleware.py
from django.utils import timezone
from pytz import timezone as pytz_timezone
from django.conf import settings

class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Set the timezone for the entire request cycle to the desired local timezone
        user_timezone = pytz_timezone(settings.TIME_ZONE)
        timezone.activate(user_timezone)

        response = self.get_response(request)

        # Optionally deactivate timezone after response if needed
        timezone.deactivate()

        return response
