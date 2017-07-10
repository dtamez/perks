#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from gevent.wsgi import WSGIServer
from werkzeug.contrib.fixers import ProxyFix
from werkzeug.debug import DebuggedApplication
from werkzeug.serving import run_with_reloader

from perks import app


@run_with_reloader
def run_server():
    debug = app.config['DEBUG']
    if debug:
        http_server = WSGIServer(('', 5000), DebuggedApplication(app))
        http_server.serve_forever()
    else:
        app.wsgi_app = ProxyFix(app.wsgi_app)
        app.run()


if __name__ == "__main__":
    run_server()
