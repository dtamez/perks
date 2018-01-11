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

from datetime import date
from decimal import Decimal
import unittest

from flask import url_for

from app import create_app, db
from app.models import (
    Configuration,
    Employee,
    Location,
    User,
)
from tests import model_factory as mf


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


class LocationTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.admin = User(email=u'admin@admin.com', is_admin=True, password='password')
        db.session.add(self.admin)
        self.client = self.app.test_client(use_cookies=True)
        self.loc_1 = mf.LocationFactory()
        self.loc_2 = mf.LocationFactory()
        db.session.add(self.loc_1)
        db.session.add(self.loc_2)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        data = {'email': self.admin.email, 'password': 'password'}
        self.client.post(url_for('auth.login'), data=data, follow_redirects=True)

    def test_get_locations(self):
        loc_1, loc_2 = self.loc_1, self.loc_2
        self.login()

        response = self.client.get(url_for('main.admin_people'))

        self.assertEqual(200, response.status_code)
        html = response.get_data(as_text=True)
        self.assertIn(loc_1.code, html, 'location code {} not found in response'.format(loc_1.code))
        self.assertIn(loc_1.description, html,
                      'location description {} not found in response'.format(loc_1.description))
        self.assertIn(str(loc_1.effective_date), html,
                      'location effective_date {} not found in response'.format(loc_1.effective_date))
        self.assertIn(loc_2.code, html, 'location code {} not found in response'.format(loc_2.code))
        self.assertIn(loc_2.description, html,
                      'location description {} not found in response'.format(loc_2.description))
        self.assertIn(str(loc_2.effective_date), html,
                      'location effective_date {} not found in response'.format(loc_2.effective_date))

    def test_edit_location(self):
        loc_1 = self.loc_1
        self.login()

        data = {'location-id': loc_1.id, 'location-code': 'updated', 'location-description': 'also updated',
                'location-effective_date': date.today()}
        response = self.client.put(url_for('main.location_ajax', id=loc_1.id), data=data)

        self.assertEqual(200, response.status_code)
        loc_1_from_db = Location.query.get(loc_1.id)
        self.assertEqual(loc_1_from_db.code, data['location-code'])
        self.assertEqual(loc_1_from_db.description, data['location-description'])
        self.assertEqual(loc_1_from_db.effective_date, data['location-effective_date'])

    def test_create_location(self):
        self.login()
        data = {'location-code': 'DAL', 'location-description': 'Dallas Main Office',
                'location-effective_date': date.today()}

        response = self.client.post(url_for('main.location_ajax'), data=data)

        self.assertEqual(200, response.status_code)
        loc = Location.query.filter_by(code='DAL').one()
        self.assertIsNotNone(loc)


class TestRequestObject(object):

    def __init__(self, _file=None, form=None):
        if not form:
            form = {}
        if not _file:
            _file = {}
        self.files = _file
        self.form = form


class ConfigurationTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.admin = User(email=u'admin@admin.com', is_admin=True, password='password')
        db.session.add(self.admin)
        self.client = self.app.test_client(use_cookies=True)
        db.session.commit()
        self.login()

    def login(self):
        data = {'email': self.admin.email, 'password': 'password'}
        self.client.post(url_for('auth.login'), data=data, follow_redirects=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_configuration(self):
        data = {'company_text': 'Company Text 1'}
        config = Configuration.query.first()

        self.assertFalse(config)

        r = self.client.post(url_for('main.admin_configurator'), data=data)
        config = Configuration.query.first()

        self.assertEqual(200, r.status_code)
        self.assertEqual(data.get('company_text'), config.company_text)

    def test_update_configuration(self):
        data_v1 = {'company_text': 'Company Text 1'}
        data_v2 = {'company_text': 'Company Text 2'}

        self.client.post(url_for('main.admin_configurator'), data=data_v1)
        config_v1 = Configuration.query.first()

        self.assertEqual(data_v1.get('company_text'), config_v1.company_text)

        self.client.post(url_for('main.admin_configurator'), data=data_v2)
        config_v2 = Configuration.query.first()

        self.assertEqual(data_v2.get('company_text'), config_v2.company_text)


class EmployeeTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.admin = User(email=u'admin@admin.com', is_admin=True, password='password')
        db.session.add(self.admin)
        self.client = self.app.test_client(use_cookies=True)
        self.emp1 = mf.EmployeeFactory()
        self.emp2 = mf.EmployeeFactory()
        db.session.add(self.emp1)
        db.session.add(self.emp2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        data = {'email': self.admin.email, 'password': 'password'}
        self.client.post(url_for('auth.login'), data=data, follow_redirects=True)

    def test_get_employees(self):
        emp1, emp2 = self.emp1, self.emp2
        self.login()

        response = self.client.get(url_for('main.admin_people'))

        self.assertEqual(200, response.status_code)
        html = response.get_data(as_text=True)
        self.assertIn(emp1.last_name, html, 'employee last_name {} not found in response'.format(emp1.last_name))
        self.assertIn(emp1.first_name, html, 'employee first_name {} not found in response'.format(emp1.first_name))
        self.assertIn(emp1.user.email, html, 'employee email {} not found in response'.format(emp1.user.email))
        self.assertIn(str(emp1.phone), html, 'employee phone {} not found in response'.format(emp1.phone))
        self.assertIn(emp2.last_name, html, 'employee last_name {} not found in response'.format(emp2.last_name))
        self.assertIn(emp2.first_name, html, 'employee first_name {} not found in response'.format(emp2.first_name))
        self.assertIn(emp2.user.email, html, 'employee email {} not found in response'.format(emp2.user.email))
        self.assertIn(str(emp2.phone), html, 'employee phone {} not found in response'.format(emp2.phone))

    def test_edit_employee(self):
        emp1 = self.emp1
        self.login()
        data = {'employee-id': emp1.id, 'employee-employee_number': 'updated num', 'employee-group_id': 'updated grp',
                'employee-hire_date': date.today(), 'employee-effective_date': date.today(),
                'employee-sub_group_effective_date': date.today(), 'employee-salary_effective_date': date.today(),
                'employee-sub_group_id': 'updated sub', 'employee-first_name': 'updated first',
                'employee-last_name': 'updated last', 'employee-ssn': '123-45-6789', 'employee-dob': date.today(),
                'employee-gender': 'F', 'employee-marital_status': 'single', 'employee-smoker_type': 'SM',
                'user-email': 'updated@updated.com', 'employee-phone': '(214) 555-9999',
                'employee-alternate_phone': '(214) 555-5555', 'employee-emergency_contact_name': 'updated emerg',
                'employee-emergency_contact_phone': '(214) 555-2222', 'employee-location': self.emp1.location.id,
                'employee-emergency_contact_relationship': 'updated relationshp', 'employee-spouse_dob': date.today(),
                'employee-spouse_smoker_type': 'SM', 'employee-salary': '100', 'address-state': 'TX',
                'address-street_1': 'updated street', 'address-city': 'updated city', 'address-zip_code': '12345'}

        response = self.client.put(url_for('main.employee_ajax', id=emp1.id), data=data)

        self.assertEqual(200, response.status_code)
        emp1_from_db = Employee.query.get(emp1.id)
        self.assertEqual(emp1_from_db.employee_number, data['employee-employee_number'])
        self.assertEqual(emp1_from_db.group_id, data['employee-group_id'])
        self.assertEqual(emp1_from_db.sub_group_id, data['employee-sub_group_id'])
        self.assertEqual(emp1_from_db.first_name, data['employee-first_name'])
        self.assertEqual(emp1_from_db.last_name, data['employee-last_name'])
        self.assertEqual(emp1_from_db.ssn, data['employee-ssn'])
        self.assertEqual(emp1_from_db.dob, data['employee-dob'])
        self.assertEqual(emp1_from_db.gender, data['employee-gender'])
        self.assertEqual(emp1_from_db.marital_status, data['employee-marital_status'])
        self.assertEqual(emp1_from_db.smoker_type, data['employee-smoker_type'])
        self.assertEqual(emp1_from_db.email, data['user-email'])
        self.assertEqual(str(emp1_from_db.phone), data['employee-phone'])
        self.assertEqual(str(emp1_from_db.alternate_phone), data['employee-alternate_phone'])
        self.assertEqual(emp1_from_db.emergency_contact_name, data['employee-emergency_contact_name'])
        self.assertEqual(str(emp1_from_db.emergency_contact_phone), data['employee-emergency_contact_phone'])
        self.assertEqual(emp1_from_db.emergency_contact_relationship, data['employee-emergency_contact_relationship'])
        self.assertEqual(emp1_from_db.spouse_dob, data['employee-spouse_dob'])
        self.assertEqual(emp1_from_db.spouse_smoker_type, data['employee-spouse_smoker_type'])
        self.assertEqual(emp1_from_db.salary, Decimal(data['employee-salary']))

    def test_create_employee(self):
        self.login()
        data = {'employee-employee_number': u'created num', 'employee-group_id': 'created grp',
                'employee-hire_date': date.today(), 'employee-effective_date': date.today(),
                'employee-sub_group_effective_date': date.today(), 'employee-salary_effective_date': date.today(),
                'employee-sub_group_id': 'created sub', 'employee-first_name': 'created first',
                'employee-last_name': 'created last', 'employee-ssn': '123-45-6789', 'employee-dob': date.today(),
                'employee-gender': 'F', 'employee-marital_status': 'single', 'employee-smoker_type': 'SM',
                'user-email': 'created@created.com', 'employee-phone': '(214) 555-9999',
                'employee-alternate_phone': '(214) 555-5555', 'employee-emergency_contact_name': 'created emerg',
                'employee-emergency_contact_phone': '(214) 555-2222', 'employee-location': self.emp1.location.id,
                'employee-emergency_contact_relationship': 'created relationshp', 'employee-spouse_dob': date.today(),
                'employee-spouse_smoker_type': 'SM', 'employee-salary': '100', 'address-state': 'TX',
                'address-street_1': 'created street', 'address-city': 'created city', 'address-zip_code': '12345'}

        response = self.client.post(url_for('main.employee_ajax'), data=data)

        self.assertEqual(200, response.status_code)
        emp = Employee.query.filter_by(employee_number=u'created num').one()
        self.assertIsNotNone(emp)

