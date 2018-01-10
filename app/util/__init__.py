# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
import os
import time


def save_image_and_return_static_path(request, ):
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(ROOT_DIR, '..', 'static', 'images')
    _file = request.files['logo'] if request.files else None
    file_info_list = _file.filename.split('.')
    ts = int(round(time.time() * 1000))
    image_name = '{}_{}.{}'.format('logo', ts, file_info_list[-1])
    if file_info_list[-1] in ['png', 'jpeg']:
        image_path = '{}/{}'.format(
            image_dir, image_name)
        static_path = '{}/{}'.format('static/images', image_name)
        return image_path, static_path, _file