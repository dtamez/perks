#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Blueprint main for perks app.
"""
from __future__ import absolute_import

from flask import Blueprint

main = Blueprint('main', __name__)


from . import views, errors  # NOQA
