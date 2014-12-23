# -*- coding: utf-8 -*-

import conf
from django.db import models
from .signals import payment_process, payment_completed, payment_fail
from .utils import build_xml_string, get_signature


class Payment(models.Model):
    STATUS_UNCONFIRM = 'unconfirm'
    STATUS_PROCESS = 'process'
    STATUS_RESERVE = 'reserve'
    STATUS_SUCCESS = 'success'
    STATUS_FAIL = 'fail'
    STATUS_CHOICES = (
        (STATUS_PROCESS, 'Ожидается оплата'),
        (STATUS_RESERVE, 'Средства зарезервированы'),
        (STATUS_SUCCESS, 'Заказ оплачен'),
        (STATUS_FAIL, 'Оплата отменена'),
    )

    ERROR_AMOUNT_CHECK_FAILED = 'Amount check failed'
    ERROR_CURRENCY_CHECK_FAILED = 'Currency check failed'
    ERROR_SECURITY_CHECK_FAILED = 'Security check failed'
    ERROR_UNKNOWN_ORDER_ID = 'Unknown order_id'
    ERROR_INCORRECT_ORDER_ID = 'Incorrect order_id'
    ERROR_CAN_NOT_PARSE_XML = 'Can not parse xml'

    ERROR_STATUS = {
        ERROR_AMOUNT_CHECK_FAILED: 'Сумма заказа {0.amount} не совпадает '
                                   'с оплаченой {1[amount]}!',
        ERROR_CURRENCY_CHECK_FAILED: 'Валюта заказа {0.currency} не совпадает '
                                     'с оплаченой {1[currency]}!',
        ERROR_SECURITY_CHECK_FAILED: 'Ключ безопасности не совпадает!',
        ERROR_UNKNOWN_ORDER_ID: 'Заказ с номером {1[order_id]} не найден!',
        ERROR_INCORRECT_ORDER_ID: 'Не указан номер заказа!',
        ERROR_CAN_NOT_PARSE_XML: 'Не удалось получить данные об оплате, '
                                 'обратитесь в %s' % conf.PAY2PAY_CONTACTS_URL
    }

    version = models.CharField('Версия интерфейса', max_length=8, default='1.3')
    merchant_id = models.PositiveIntegerField('ID магазина', default=conf.PAY2PAY_MERCHANT_ID)
    order_id = models.CharField('Номер заказа', max_length=36)
    amount = models.DecimalField('Сумма', max_digits=12, decimal_places=2, default=.0)
    currency = models.CharField('Валюта', max_length=8, default=conf.PAY2PAY_CURRENCY)
    description = models.CharField('Описание', max_length=512, blank=True)

    paymode = models.CharField('Способ платежа', max_length=16, blank=True, null=True)
    trans_id = models.CharField('Номер транзакции', max_length=32, blank=True, null=True)
    status = models.CharField('Статус', max_length=16, choices=STATUS_CHOICES, default=STATUS_PROCESS)
    error_msg = models.CharField('Описание ошибки', max_length=256, blank=True, null=True)
    test_mode = models.BooleanField('Тестовый режим', default=conf.PAY2PAY_TEST_MODE)

    updated = models.DateTimeField('Обновлен', auto_now=True)
    created = models.DateTimeField('Создан', auto_now_add=True)

    def __unicode__(self):
        return '%s <%s>' % (
            self.order_id,
            self.get_status_display()
        )

    def send_signals(self, request, response):
        if not self.status:
            return

        status = self.status
        if status == self.STATUS_PROCESS or status == self.STATUS_RESERVE:
            payment_process.send(sender=self.__class__, payment=self,
                                 request=request, response=response)
        if status == self.STATUS_SUCCESS:
            payment_completed.send(sender=self.__class__, payment=self,
                                   request=request, response=response)
        if status == self.STATUS_FAIL:
            payment_fail.send(sender=self.__class__, payment=self,
                              request=request, response=response)

    @property
    def signature(self):
        return get_signature(self.xml, conf.PAY2PAY_SECRET_KEY)

    @property
    def xml(self):
        data = self._get_xml_data()
        return build_xml_string(data)

    def _get_xml_data(self):
        data = {
            'success_url': conf.PAY2PAY_SUCCESS_URL,
            'fail_url': conf.PAY2PAY_FAIL_URL,
            'result_url': conf.PAY2PAY_RESULT_URL,
        }
        if conf.PAY2PAY_TEST_MODE:
            data['test_mode'] = 1
        for name in self.names:
            value = getattr(self, name)
            if value:
                data[name] = value

        return data

    names = [
        'version',
        'merchant_id',
        'order_id',
        'amount',
        'currency',
        'description',
    ]

    class Meta:
        ordering = ('created',)
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
