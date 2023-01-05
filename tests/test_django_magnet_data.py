# standard library
import datetime
from decimal import Decimal

# django
from django.test.testcases import TestCase

# magnet data
from magnet_data.magnet_data_client import MagnetDataClient
from magnet_data import utils
from magnet_data.models import Holiday


class TestCurrencies(TestCase):
    def test_currencies(self):
        magnet_data_client = MagnetDataClient()
        currencies = magnet_data_client.currencies

        clf_to_clp_converter = currencies.get_pair(currencies.CLF, currencies.CLP)
        # same as
        clf_to_clp_converter = currencies.get_pair(
            base_currency=currencies.CLF, counter_currency=currencies.CLP
        )

        # get the current value
        clf_in_clp = clf_to_clp_converter.now()
        self.assertGreater(clf_in_clp, 0)

        # get the latest value
        clf_in_clp = clf_to_clp_converter.latest()
        self.assertGreater(clf_in_clp, 0)

        # get the value for a given date
        date = datetime.date(2022, 7, 5)
        clf_in_clp_on_july_fifth = clf_to_clp_converter.on_date(date=date)
        self.assertEqual(clf_in_clp_on_july_fifth, Decimal("33152.680000"))

    def test_invalid_currency_acronyms(self):
        magnet_data_client = MagnetDataClient()
        currencies = magnet_data_client.currencies

        with self.assertRaises(ValueError):
            currencies.get_pair('UF', currencies.CLP)

    def test_last_knowable_date(self):
        magnet_data_client = MagnetDataClient()
        currencies = magnet_data_client.currencies

        clf_to_clp_converter = currencies.get_pair(currencies.CLF, currencies.CLP)

        self.assertGreaterEqual(
            clf_to_clp_converter.last_knowable_date(),
            utils.today()
        )

    def test_inverse_currencies(self):
        magnet_data_client = MagnetDataClient()
        currencies = magnet_data_client.currencies

        clp_to_clf_converter = currencies.get_pair(currencies.CLP, currencies.CLF)
        # same as
        clp_to_clf_converter = currencies.get_pair(
            base_currency=currencies.CLP, counter_currency=currencies.CLF
        )

        # get the current value
        clf_in_clp = clp_to_clf_converter.now()
        self.assertLess(clf_in_clp, 1)

        # get the latest value
        clf_in_clp = clp_to_clf_converter.latest()
        self.assertLess(clf_in_clp, 1)

        # get the value for a given date
        date = datetime.date(2022, 7, 5)
        clf_in_clp_on_july_fifth = clp_to_clf_converter.on_date(date=date)
        self.assertEqual(clf_in_clp_on_july_fifth, 1 / Decimal("33152.680000"))


class TestHolidays(TestCase):
    def test_holidays(self):
        magnet_data_client = MagnetDataClient()
        self.assertEqual(Holiday.objects.count(), 0)
        holidays = magnet_data_client.holidays
        holidays.update(country_code=holidays.CL)

        self.assertGreater(Holiday.objects.count(), 0)

        self.assertFalse(holidays.is_workday(datetime.date(2023, 1, 2), holidays.CL))
        self.assertTrue(holidays.is_workday(datetime.date(2023, 1, 3), holidays.CL))

        self.assertEqual(
            holidays.get_next_working_day(
                country_code=holidays.CL,
                from_date=datetime.date(2022, 12, 31),
            ),
            datetime.date(2023, 1, 3),
        )

        self.assertEqual(
            holidays.get_holidays_count_during_weekdays(
                holidays.CL,
                datetime.date(2022, 12, 30),
                datetime.date(2023, 1, 7),
            ),
            1
        )
