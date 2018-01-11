# ~*~ coding: utf-8 ~*~

import unittest

from app.util.carriers.base import (
    Base,
    CarrierValidationException)


class TestBase(Base):
    document = None
    customer_info_spec = [
        ('one', str, 1, 1),
        ('two', int, 1, 2),
        ('filler', str, 11, 3),
        ('three', str, 5, 14)]

    def __init__(self, payload=None):
        self.errors = None
        self.payload = payload
        self.validate()
        self.document = self.create_document()


class TestCarriers(unittest.TestCase):
    def setUp(self):
        pass

    def test_carrier_validation_failure(self):
        payload = {'one': 's', 'two': '1', 'three': 'flask'}

        with self.assertRaises(CarrierValidationException):
            TestBase(payload)

    def test_carrier_validation_success(self):
        payload = {'one': 's', 'two': 1, 'three': 'flask'}

        base = TestBase(payload)

        self.assertTrue(base.document)
        self.assertEqual(base.document, 's1           flask')
        self.assertTrue(1, base.document[1:1])

    def test_carrier_value_placement(self):
        payload = {'one': 's', 'two': 1, 'three': 'flask'}

        base = TestBase(payload)
        two_value_spec = base.customer_info_spec[1]
        three_value_spec = base.customer_info_spec[3]
        two_value_length = two_value_spec[-2]
        two_value_position = two_value_spec[-1] - 1
        three_value_length = three_value_spec[-2]
        three_value_position = three_value_spec[-1] - 1

        self.assertEqual(
            str(payload.get('two')), base.document[two_value_position:two_value_position + two_value_length])
        self.assertEqual(
            payload.get('three'), base.document[three_value_position:three_value_position + three_value_length])
