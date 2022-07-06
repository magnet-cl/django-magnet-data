# standard library
from decimal import Decimal
import datetime

# django
from django.core.cache import cache
from django.apps import apps

# magnet data
from magnet_data import utils
from magnet_data.currencies.enums import CurrencyAcronyms
from magnet_data.currencies.exceptions import ValueNotFoundException
from magnet_data.currencies.client import update_values


class CurrencyPair:
    """
    A currency pair is the dyadic quotation of the relative value of a currency unit
    against the unit of another currency in the foreign exchange market. The currency
    that is used as the reference is called the counter currency, and the currency that
    is quoted in relation is called the base currency or transaction currency.

    https://en.wikipedia.org/wiki/Currency_pair

    Currently only handles pairs in which the counter currency is CLP
    """

    def __init__(self, base_currency: str, counter_currency: str):
        super().__init__()
        if base_currency not in dict(CurrencyAcronyms.django_model_choices):
            raise ValueError(f"base_currency {base_currency} is not a valid choice")

        if counter_currency != CurrencyAcronyms.CLP:
            raise NotImplementedError

        if counter_currency not in dict(CurrencyAcronyms.django_model_choices):
            raise ValueError(
                f"counter_currency {counter_currency} is not a valid choice"
            )

        self.base_currency = base_currency
        self.counter_currency = counter_currency

    def __str__(self):
        return f"{self.base_currency}/{self.counter_currency}"

    def last_knowable_date(self):
        today = utils.today()

        # only CLF values are known beforehand
        if self.base_currency != CurrencyAcronyms.CLF:
            return today

        if today.day < 10:
            return datetime.date(today.year, today.month, 9)
        elif today.month < 12:
            return datetime.date(today.year, today.month + 1, 9)

        return datetime.date(today.year + 1, 1, 9)

    def is_convertion_possible(self, date):
        """
        Returns if the conversion s possible. Currently all future requests are being
        deneid except for CLF conversions, since it's published beforehand
        """
        return self.last_knowable_date() >= date

    def on_date(self, date):
        """returns the value for a given date"""
        if self.base_currency == self.counter_currency:
            return 1

        if not self.is_convertion_possible(date):
            raise ValueNotFoundException(self, date)

        CurrencyValue = apps.get_model(
            app_label='magnet_data',
            model_name='CurrencyValue'
        )

        cache_key = f"md-{self.base_currency}/{self.counter_currency}/{date}"

        value = cache.get(cache_key)
        if value:
            return Decimal(value)

        queryset = CurrencyValue.objects.filter(
            base_currency=self.base_currency,
            counter_currency=self.counter_currency,
            date=date,
        )

        try:
            currency_value = queryset.get()
        except CurrencyValue.DoesNotExist:
            update_values(
                date.year, date.month, self.base_currency, self.counter_currency
            )

            try:
                currency_value = queryset.get()
            except CurrencyValue.DoesNotExist:
                raise ValueNotFoundException(self, date)

        cache.set(cache_key, currency_value.value)
        return currency_value.value

    def now(self):
        """
        Return the current value of base_currency as counter_currency
        """
        return self.on_date(utils.today())

    def latest(self):
        """
        Return the current value of base_currency as counter_currency
        """
        return self.on_date(self.last_knowable_date())

    def on_month(self, year, month):
        raise NotImplementedError(f"{self.__class__.__name__}.on_month")
