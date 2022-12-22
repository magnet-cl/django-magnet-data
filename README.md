# django-magnet-data
An API client for data.magnet.cl

## Features

-   Obtain values for multiple currencies in CLP

## Requirements

-   Django >=2.2
-   Python >=3.6

## Installation

### Get the distribution

Install django-magnet-data with pip:
```bash

    pip install django-magnet-data
```

### Configuration

Add `magnet_data` to your `INSTALLED_APPS`:
```bash
    INSTALLED_APPS =(
        ...
        "magnet_data",
        ...
    )
```

## Currency API

Magnet data handles the value of 4 currencies: `CLP`, `USD`, `EUR`, and `CLF`. Currently the api can only return the values of this currencies in `CLP`.

Values are returned as [decimal.Decimal](https://docs.python.org/3/library/decimal.html "decimal.Decimal")

To get the value of a non  `CLP` currency for a given date in  `CLP`:

``` python
import datetime
from magnet_data.magnet_data_client import MagnetDataClient

magnet_data_client = MagnetDataClient()
currencies = magnet_data_client.currencies

clf_to_clp_converter = currencies.get_pair(currencies.CLF, currencies.CLP)
# same as
clf_to_clp_converter = currencies.get_pair(
    base_currency=currencies.CLF, 
    counter_currency=currencies.CLP
)

# get the current value
clf_in_clp = clf_to_clp_converter.now()

# get the latest value
last_known_clf_in_clp = clf_to_clp_converter.latest()

# get the value for a given date
date = datetime.date(2022, 7, 5)
clf_in_clp_on_july_fifth = clf_to_clp_converter.on_date(date=date)

# get a dict of values values for a month where the key is a datetime.date
clf_in_clp_on_july = clf_to_clp_converter.on_month(2022, 7)
```

### choices for a django model

If you require a currency attribute in your models it can be done with
`CurrencyAcronyms`:

```
from django.db import models
from magnet_data.currencies.enums import CurrencyAcronyms

class MyModel(models.Model):
    currency = models.CharField(
        _("currency"),
        max_length=5,
        choices=CurrencyAcronyms.django_model_choices,
    )

```


## Contribute

### Local development

To develop locally, install requirements using
[poetry](https://python-poetry.org/).

```bash

    poetry install
```

### Testing

Test are written using the django testing framework: https://docs.djangoproject.com/en/4.1/topics/testing/

All tests are stored in the `tests` folder.

All new features have to be tested.
[poetry](https://python-poetry.org/).

```bash

    python manage.py test
```


### New features

To develop new features, create a pull request, specifying what you are
fixing / adding and the issue it's addressing if there is one.

All new features need a test in the `tests` folder.

All tests need to pass in order for a maintainer to merge the pull request.


### Publish

Use poetry to publish. You'll need a pypi token to publish in the project
root.

On the project root, run:

```bash

    poetry publish
```
