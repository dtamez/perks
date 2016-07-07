# -*- coding: utf-8 -*-
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
