# -*- coding: utf-8 -*-

import conf
import logging
import xmltodict
import lxml.etree
import lxml.builder
import decimal
from django.http import HttpResponse
from django.views.generic import View, TemplateView
from annoying.functions import get_object_or_None
from django.views.decorators.csrf import csrf_exempt

from .utils import get_signature
from .models import Payment

logger = logging.getLogger('pay2pay')


class PaymentConfirm(View):
    pay2pay_key = conf.PAY2PAY_HIDE_KEY

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(PaymentConfirm, self).dispatch(*args, **kwargs)

    def get_signature(self, xml):
        return get_signature(xml, self.pay2pay_key)

    def get_payment(self, request):
        error_msg = ''
        response = {}
        order_id = None
        payment = None
        xml = request.POST.get('xml', '').replace(' ', '+').decode('base64')

        try:
            response = self._get_obj_response(xml)
        except (ValueError, TypeError, xmltodict.expat.ExpatError):
            error_msg = Payment.ERROR_CAN_NOT_PARSE_XML 
            logger.error(error_msg, exc_info=True)
        else:
            order_id = response.get('order_id')
            if order_id:
                payment = get_object_or_None(Payment, order_id=order_id)
                if payment:
                    sig_encode = request.POST.get('sign', '')
                    sign = self.get_signature(xml)
                    if sig_encode == sign:
                        currency = response.get('currency', '')
                        if payment.currency.upper() == currency:
                            amount = response.get('amount', 0)
                            if decimal.Decimal(amount) < payment.amount:
                                # Сумма платежа может превышать сумму заказа.
                                # Например, в случае оплаты через системы
                                # денежных переводов
                                error_msg = Payment.ERROR_AMOUNT_CHECK_FAILED
                        else:
                            error_msg = Payment.ERROR_CURRENCY_CHECK_FAILED
                    else:
                        error_msg = Payment.ERROR_SECURITY_CHECK_FAILED
                else:
                    error_msg = Payment.ERROR_UNKNOWN_ORDER_ID
            else:
                error_msg = Payment.ERROR_INCORRECT_ORDER_ID

        if error_msg:
            extra = ''
            if order_id:
                extra = ' for order_id "%s"' % order_id
            logger.error('%s%s', error_msg, extra)

        return (error_msg, response, payment)

    def post(self, request, *args, **kwargs):
        error_msg, response, payment = self.get_payment(request)
        xml_response = self._get_xml_response(error_msg)
        return HttpResponse(xml_response, content_type='text/xml')

    def _get_xml_response(self, error_msg_value):
        e = lxml.builder.ElementMaker()

        result = e.result(
            e.status('no' if error_msg_value else 'yes'),
            e.error_msg(error_msg_value)
        )
        return lxml.etree.tostring(result, encoding='utf-8',
                                   xml_declaration=True).replace('\n', '')

    def _get_obj_response(self, xml):
        xml = xml.replace('<?xmlversion="1.0"encoding="UTF-8"?>', '').replace('\n', '')
        return xmltodict.parse(xml)['response']


class PaymentResponse(TemplateView, PaymentConfirm):
    pay2pay_key = conf.PAY2PAY_SECRET_KEY
    error_status = None

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        error_msg, response, payment = self.get_payment(request)

        if not payment and error_msg:
            payment = Payment()

        payment.status = response.get('status', '')

        if not error_msg:
            payment.paymode = response.get('paymode', '')
            payment.trans_id = response.get('trans_id', '')
            payment.error_msg = response.get('error_msg', '')
            payment.save()
        else:
            error_status = payment.ERROR_STATUS.get(error_msg, error_msg)
            self.error_status = error_status.format(payment, response)
            
        payment.error_status = self.error_status
        payment.send_signals(request, response)

        context['response'] = response
        context['payment'] = payment
        return self.render_to_response(context)


class PaymentSuccess(PaymentResponse):
    template_name = 'pay2pay/payment_success.html'

    def post(self, request, *args, **kwargs):
        return super(PaymentSuccess, self).post(request, *args, **kwargs)


class PaymentFail(PaymentResponse):
    template_name = 'pay2pay/payment_fail.html'

    def post(self, request, *args, **kwargs):
        return super(PaymentFail, self).post(request, *args, **kwargs)
