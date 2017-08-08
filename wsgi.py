#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from perks import app


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
