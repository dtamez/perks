#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Tests for the admininstrative views.
"""
from __future__ import absolute_import

import unittest

from flask import url_for

from app import create_app, db
from app.models import User


class AdminLoginTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.admin = User(email=u'admin@admin.com', is_admin=True, password='password')
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'), follow_redirects=True)

        self.assertTrue('Log-in to your account' in response.get_data(as_text=True))

    def test_admin_login(self):
        data = {'email': u'admin@admin.com', 'password': 'password'}

        db.session.add(self.admin)
        admin = User.query.one()
        self.assertEqual(admin.email, u'admin@admin.com')
        response = self.client.post(url_for('auth.login'), data=data, follow_redirects=True)
        html = response.get_data(as_text=True)

        self.assertTrue('Admin' in html)
