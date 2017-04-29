#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent.wsgi import WSGIServer
from werkzeug.debug import DebuggedApplication
from werkzeug.serving import run_with_reloader
from perks import app


@run_with_reloader
def run_server():
    debug = app.config['DEBUG']
    if debug:
        http_server = WSGIServer(('', 5000), DebuggedApplication(app))
    else:
        http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()


if __name__ == "__main__":
    run_server()
