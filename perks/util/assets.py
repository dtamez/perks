# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from flask_assets import Bundle, Environment
from .. import app

bundles = {
    'perks_css': Bundle(
        'css/custom.css',
        output='gen/perks.css'
    )
}

assets = Environment(app)
assets.register(bundles)
