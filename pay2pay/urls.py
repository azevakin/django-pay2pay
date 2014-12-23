# -*- coding: utf-8 -*-

try:
    from django.conf.urls import patterns, url
except ImportError:
    from django.conf.urls.defaults import patterns, url

from .views import *

urlpatterns = patterns('',
    url(r'^confirm/$', PaymentConfirm.as_view(), name='pay2pay_confirm'),
    url(r'^success/$', PaymentSuccess.as_view(), name='pay2pay_success'),
    url(r'^fail/$', PaymentFail.as_view(), name='pay2pay_fail'),
)
