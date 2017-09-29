#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gevent.wsgi import WSGIServer
from werkzeug.debug import DebuggedApplication
from werkzeug.serving import run_with_reloader
from app import create_app


@run_with_reloader
def run_server():
    app = create_app('development')
    debug = app.config['DEBUG']
    if debug:
        http_server = WSGIServer(('', 5000), DebuggedApplication(app))
    else:
        http_server = WSGIServer(('', 5000), app)
    http_server.serve_forever()


if __name__ == "__main__":
    run_server()
