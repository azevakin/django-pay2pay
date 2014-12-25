# -*- coding: utf-8 -*-

import conf
import base64
from django import forms
from inspect import isfunction
from .utils import get_signature, build_xml_string, get_urls
from .models import Payment


class PayForm(forms.ModelForm):
    xml = forms.CharField()
    sign = forms.CharField()

    def __init__(self, *args, **kwargs):
        super(PayForm, self).__init__(*args, **kwargs)

        initial = kwargs.get('initial', {})
        data = get_urls(initial.get('site'))
        if conf.PAY2PAY_TEST_MODE:
            data['test_mode'] = 1
        for name in Payment.names:
            if name in initial:
                data[name] = initial[name]
            else:
                default = self.fields[name].initial
                if isfunction(default):
                    data[name] = default()
                else:
                    data[name] = default

        xml = build_xml_string(data)
        self.fields['xml'].initial = base64.b64encode(xml)
        self.fields['sign'].initial = get_signature(xml, conf.PAY2PAY_SECRET_KEY)

        if conf.PAY2PAY_HIDE_FORM_FIELD:
            for name in self.fields:
                self.fields[name].widget = forms.HiddenInput()

    class Meta:
        exclude = ('created',)
        model = Payment
