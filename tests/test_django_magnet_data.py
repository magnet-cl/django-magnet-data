# standard library
from decimal import Decimal
from unittest.mock import MagicMock
from unittest.mock import patch
import datetime

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

    def test_non_CLP_currencies(self):
        magnet_data_client = MagnetDataClient()
        currencies = magnet_data_client.currencies

        usd_to_clf_converter = currencies.get_pair(currencies.USD, currencies.CLF)

        # get the current value
        clf_in_usd = usd_to_clf_converter.now()
        self.assertGreater(clf_in_usd, 1)

        # get the latest value
        clf_in_usd = usd_to_clf_converter.latest()
        self.assertGreater(clf_in_usd, 1)

        # get the value for a given date
        date = datetime.date(2022, 7, 5)
        clf_in_usd_on_july_fifth = usd_to_clf_converter.on_date(date=date)
        self.assertEqual(
            clf_in_usd_on_july_fifth,
            Decimal("33152.68") / Decimal("927.53")
        )

    def test_non_CLP_currencies_last_knowable_dates(self):
        magnet_data_client = MagnetDataClient()
        currencies = magnet_data_client.currencies

        usd_to_clf_converter = currencies.get_pair(currencies.CLF, currencies.USD)

        # check future dates since only CLF is known in the future
        assert usd_to_clf_converter.last_knowable_date() == utils.today()
        clf_in_usd_on_tomorrow = usd_to_clf_converter.latest()
        self.assertLess(clf_in_usd_on_tomorrow, 1)


class TestHolidays(TestCase):
    def test_holidays(self):
        magnet_data_client = MagnetDataClient()
        self.assertEqual(Holiday.objects.count(), 0)
        holidays = magnet_data_client.holidays
        holidays.update(country_code=holidays.CL, year=2023)

        self.assertGreater(Holiday.objects.count(), 0)

        self.assertFalse(holidays.is_workday(datetime.date(2023, 1, 2), holidays.CL))
        self.assertTrue(holidays.is_workday(datetime.date(2023, 1, 3), holidays.CL))

        self.assertEqual(
            holidays.get_next_business_day(
                country_code=holidays.CL,
                from_date=datetime.date(2022, 12, 31),
            ),
            datetime.date(2023, 1, 3),
        )

        self.assertEqual(
            holidays.get_next_business_day(
                country_code=holidays.CL,
                from_date=datetime.date(2022, 12, 31),
                business_days_count=3,
            ),
            datetime.date(2023, 1, 5),
        )

        self.assertEqual(
            holidays.get_next_business_day(
                country_code=holidays.CL,
                from_date=datetime.date(2022, 12, 31),
                step=3,
            ),
            datetime.date(2023, 1, 3),
        )

        self.assertEqual(
            holidays.get_next_business_day(
                country_code=holidays.CL,
                from_date=datetime.date(2023, 1, 1),
                step=3,
            ),
            datetime.date(2023, 1, 4),
        )

        self.assertEqual(
            holidays.get_holidays_count_during_weekdays(
                holidays.CL,
                datetime.date(2022, 12, 30),
                datetime.date(2023, 1, 7),
            ),
            1
        )

        self.assertFalse(holidays.is_workday(datetime.date(2020, 9, 18), holidays.CL))
        self.assertFalse(holidays.is_workday(datetime.date(2024, 1, 1), holidays.CL))

    @patch('magnet_data.holidays.models.urlopen')
    def test_holiday_name_change(self, mock_urlopen):
        initial_response_content = '''
        {
            "objects": [
                {
                    "countryCode": "CL",
                    "date": "2023-01-01",
                    "name": "Feliz Año",
                    "resourceUri": "/api/v1/holidays/cl/161/"
                }
            ]
        }
        '''
        initial_response = MagicMock()
        initial_response.read.return_value = initial_response_content.encode('utf-8')
        initial_response.status = 200

        # Define the second mock API response with the updated holiday name
        updated_response = MagicMock()
        updated_response_content = '''
        {
            "objects": [
                {
                    "countryCode": "CL",
                    "date": "2023-01-01",
                    "name": "Nuevo Año",
                    "resourceUri": "/api/v1/holidays/cl/161/"
                }
            ]
        }
        '''
        updated_response.status = 200
        updated_response.read.return_value = updated_response_content.encode('utf-8')

        mock_urlopen.side_effect = [initial_response, updated_response]
        magnet_data_client = MagnetDataClient()
        self.assertEqual(mock_urlopen.call_count, 0)

        holidays = magnet_data_client.holidays
        holidays.update(country_code=holidays.CL, year=2023)
        self.assertEqual(mock_urlopen.call_count, 1)

        holiday_queryset = Holiday.objects.filter(
            country_code=holidays.CL,
            date='2023-01-01',
        )
        self.assertTrue(holiday_queryset.filter(name="Feliz Año").exists())

        # test that holiday was updated
        holidays.reset_cache()
        holidays.update(country_code=holidays.CL, year=2023)
        self.assertEqual(mock_urlopen.call_count, 2)
        self.assertTrue(holiday_queryset.filter(name="Nuevo Año").exists())

    @patch('magnet_data.holidays.models.urlopen')
    def test_holiday_date_change(self, mock_urlopen):
        """
        Test that when a holiday changes date, the original date is deleted
        """
        Holiday.objects.create(country_code="CO", date="2023-01-01", name="Feliz Año")
        initial_response_content = '''
        {
            "objects": [
                {
                    "countryCode": "CL",
                    "date": "2023-01-01",
                    "name": "Feliz Año",
                    "resourceUri": "/api/v1/holidays/cl/161/"
                }, {
                    "countryCode": "CL",
                    "date": "2024-01-01",
                    "name": "Feliz Año",
                    "resourceUri": "/api/v1/holidays/cl/162/"
                }, {
                    "countryCode": "CL",
                    "date": "2025-01-01",
                    "name": "Feliz Año",
                    "resourceUri": "/api/v1/holidays/cl/162/"
                }
            ]
        }
        '''
        initial_response = MagicMock()
        initial_response.read.return_value = initial_response_content.encode('utf-8')
        initial_response.status = 200

        # Define the second mock API response with the updated holiday date
        updated_response = MagicMock()
        updated_response_content = '''
        {
            "objects": [
                {
                    "countryCode": "CL",
                    "date": "2023-01-02",
                    "name": "Feliz Año",
                    "resourceUri": "/api/v1/holidays/cl/161/"
                }
            ]
        }
        '''
        updated_response.status = 200
        updated_response.read.return_value = updated_response_content.encode('utf-8')

        mock_urlopen.side_effect = [initial_response, updated_response]
        magnet_data_client = MagnetDataClient()
        self.assertEqual(mock_urlopen.call_count, 0)

        holidays = magnet_data_client.holidays
        holidays.update(country_code=holidays.CL, year=2023)
        self.assertEqual(mock_urlopen.call_count, 1)

        self.assertEqual(Holiday.objects.count(), 4)

        # test that holiday was updated
        holidays.reset_cache()
        holidays.update(country_code=holidays.CL, year=2023)
        self.assertEqual(mock_urlopen.call_count, 2)
        self.assertEqual(Holiday.objects.count(), 4)

        self.assertTrue(Holiday.objects.filter(date="2023-01-02").count() == 1)
