# -*- coding: utf-8 -*-

from django.conf import settings


PAY2PAY_MERCHANT_ID = getattr(settings, 'PAY2PAY_MERCHANT_ID')
PAY2PAY_SEKRET_KEY = getattr(settings, 'PAY2PAY_SEKRET_KEY')
PAY2PAY_CURRENCY = getattr(settings, 'PAY2PAY_CURRENCY', 'RUB')
PAY2PAY_SUCCESS_URL = getattr(settings, 'PAY2PAY_SUCCESS_URL')
PAY2PAY_FAIL_URL = getattr(settings, 'PAY2PAY_FAIL_URL')
PAY2PAY_RESULT_URL = getattr(settings, 'PAY2PAY_RESULT_URL')
PAY2PAY_TEST_MODE = getattr(settings, 'PAY2PAY_TEST_MODE', False)
