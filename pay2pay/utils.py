# -*- coding: utf-8 -*-

import base64
import hashlib
import lxml.etree
import lxml.builder

from django.contrib.sites.models import Site

from . import conf


def build_xml_string(data):
    e = lxml.builder.ElementMaker()

    request = e.request
    version = e.version
    merchant_id = e.merchant_id
    order_id = e.order_id
    amount = e.amount
    currency = e.currency
    description = e.description
    success_url = e.success_url
    fail_url = e.fail_url
    result_url = e.result_url
    test_mode = e.test_mode

    request = request(
        version(data['version']),
        merchant_id(str(data['merchant_id'])),
        order_id(data['order_id']),
        amount(str(data['amount'])),
        currency(data['currency']),
        description(data['description']),
        success_url(data['success_url']),
        fail_url(data['fail_url']),
        result_url(data['result_url']),
        test_mode(
            str(data.get('test_mode', ''))
        ),
    )
    return lxml.etree.tostring(request, encoding='utf-8').replace('\n', '')


def get_signature(xml, key):
    sign_str = '{0}{1}{0}'.format(key, xml)
    hsh = hashlib.md5()
    hsh.update(sign_str)
    sign_md5 = hsh.hexdigest()
    sign_encode = base64.b64encode(sign_md5)
    return sign_encode


def get_urls(domain=None):
    domain = isinstance(domain, Site) and domain.domain or domain or ''
    scheme = domain and 'http://' or ''
    return {key: '{0}{1}{2}'.format(scheme, domain, path)
            for key, path in (('success_url', conf.PAY2PAY_SUCCESS_URL),
                              ('fail_url', conf.PAY2PAY_FAIL_URL),
                              ('result_url', conf.PAY2PAY_RESULT_URL))}

