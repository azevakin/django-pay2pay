# -*- coding: utf-8 -*-

from django.dispatch import Signal

payment_process = Signal(providing_args=['payment', 'request'])
payment_completed = Signal(providing_args=['payment', 'request'])
payment_fail = Signal(providing_args=['payment', 'request'])
