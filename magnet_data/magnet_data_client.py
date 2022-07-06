from magnet_data.currencies.enums import CurrencyAcronyms
from magnet_data.currencies.currency_pair import CurrencyPair


class Currencies(CurrencyAcronyms):
    @staticmethod
    def get_pair(base_currency, counter_currency):
        """
        Returns a CurrencyPair object
        """
        return CurrencyPair(
            base_currency=base_currency,
            counter_currency=counter_currency
        )


class MagnetDataClient:
    def __init__(self):
        super().__init__()
        self.currencies = Currencies()
