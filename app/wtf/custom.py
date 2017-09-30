#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

from __future__ import absolute_import
from wtforms import (
    IntegerField,
    widgets,
)
from wtforms.compat import text_type


class PercentageInput(widgets.TextInput):
    """A widget that accepts values from 0 to 100 as input but stores and retrieves
       that value divided by 100.   The text input will have a % symbol to the right
       of it to reenforce that the value is a percentage.
    """
    def __init__(self, *args, **kwargs):
        super(PercentageInput, self).__init__(*args, **kwargs)

    def __call__(self, field, **kwargs):
        kwargs.update({'min': '0', 'max': '100', 'type': 'number'})
        div_start = '<div class="ui right labeled input">'
        fld = super(PercentageInput, self).__call__(field, **kwargs)
        extra = '<div class="ui basic label">%</div>'
        div_end = '</div>'
        return '{}{}{}{}'.format(div_start, fld, extra, div_end)


class PercentageField(IntegerField):
    """A field that accepts values from 0 to 100 as input but stores and retrieves
       that value divided by 100.   The text input will have a % symbol to the right
       of it to reenforce that the value is a percentage.
    """
    widget = PercentageInput()

    def __init__(self, label=None, validators=None, **kwargs):
        super(IntegerField, self).__init__(label, validators, **kwargs)

    def _value(self):
        if self.raw_data:
            return self.raw_data[0]
        elif self.data is not None:
            return text_type(int(self.data * 100))
        else:
            return '0'

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = int(valuelist[0]) / 100.0
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid integer value'))
