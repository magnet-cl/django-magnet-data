# django
from django.utils.translation import ugettext_lazy as _


class ValueNotFoundException(Exception):
    """
    Exception raised when a value was not found for
    a currency pair on a given date

    Attributes:
        currency_pair -- CurrencyPair object
        date -- the date where the value was not found
    """

    def __init__(self, currency_pair, date):
        self.currency_pair = currency_pair
        self.date = date
        self.message = _("Value for %(currency_pair)s on %(date)s was not found") % {
            "currency_pair": str(self.currency_pair),
            "date": str(self.date),
        }
        super().__init__(self.message)
