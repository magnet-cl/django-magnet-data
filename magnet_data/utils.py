# django
from django.utils import timezone


def today():
    """
    This method obtains today's date in local time
    """
    return timezone.localtime(timezone.now()).date()
