#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Tests for application models that have any logic/methods.
"""
from __future__ import absolute_import

from datetime import date, timedelta
from decimal import Decimal
import unittest

from app import create_app, db
from tests import model_factory as mf


def get_date_of_birth(years_old):
    today = date.today()
    dob = today - timedelta(years_old * 366)
    return dob


class ModelsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # User model
    def test_password_get(self):
        user = mf.UserFactory(password='test')
        with self.assertRaises(AttributeError):
            user.password

    def test_password_set(self):
        user = mf.UserFactory(password='test')
        self.assertTrue(user.password_hash is not None)

    def test_verify_password(self):
        user = mf.UserFactory(password='test')
        self.assertTrue(user.verify_password('test'))

    # PersonMixin
    def test_full_name(self):
        dep_middle = mf.DependentFactory(first_name='a', middle_name='b', last_name='c')
        dep_no_middle = mf.DependentFactory(first_name='a', middle_name=None, last_name='c')

        self.assertEqual(dep_middle.full_name, 'a b c')
        self.assertEqual(dep_no_middle.full_name, 'a c')

    # Employee
    def test_empoyee_age(self):
        emp = mf.EmployeeFactory(dob=get_date_of_birth(52))

        self.assertEqual(52, emp.age)

    def test_salary_calculations(self):
        emp = mf.EmployeeFactory(salary=120000)

        self.assertEqual(120000, emp.annual_salary)
        self.assertEqual(10000, emp.monthly_salary)
        self.assertEqual(2307, emp.weekly_salary)

    # BooleanElectionMixin - BasicLife, LTD, STD, HRA, EAP, Parking
    def test_boolean_get_premium_choices_basic_life(self):
        """ per premium matrix:
            42 yr old employee making $100,000 annually should have a rate of 8.91 per $1000 of coverage
            coverage = 2 * salary = $200,000
            Total premium is 8.91% of $200,000 / 1000  -> 17.82
            monthly premium = total premium / 12 -> 1.485 (1.49)
            employer is paying 90% of the premium.
            Employer portion is 90% -> 1.3365  (1.34)
            Employee portion is 10% -> .1485  (.15)
        """
        # set up employee
        emp = mf.EmployeeFactory(dob=get_date_of_birth(42), salary=100000)
        # set up plan
        beneficiaries = [mf.BeneficiaryFactory(employee=emp) for i in range(3)]
        plan = mf.BasicLifePlanFactory(beneficiaries=beneficiaries, er_percentage_contributed=.9,
                                       multiple_of_salary_paid=2)
        # set up premiums
        matrix = [
            [0, 24, .0281],
            [25, 29, .0369],
            [30, 34, .0498],
            [35, 39, .0563],
            [40, 44, .0891],
            [45, 49, .1417],
            [50, 54, .2723],
            [55, 59, .4232],
            [60, 64, .8229],
            [65, 69, .8229],
            [70, 74, 1.3408],
            [75, 100, 1.3408]]
        age_banded_premium_factory = mf.AgeBandedPremiumFactory(plan, matrix)
        plan.premiums = age_banded_premium_factory.get_premiums()
        db.session.add(plan)
        db.session.commit()

        TOTAL = '$17.82'
        ER = '$16.04'
        EE = '$1.78'
        choices = plan.get_premium_choices(False, emp)
        for id, label, selected, total, er, ee in choices:
            if label == 'Enroll':
                self.assertEqual(selected, False)
                self.assertEqual(total, TOTAL)
                self.assertEqual(ee, EE)
                self.assertEqual(er, ER)

    def test_boolean_get_premium_choices_age_banded_smoker_gender(self):
        """ per premium matrix:
            emloyee....................rate...coverage..........total...........ER.....EE
            male, 32, smoker       ->  5.98% * $200000 / 1000 -> 11.96  * .8 ->  9.57   2.39
            female, 50, non-smoker -> 26.23% * $200000 / 1000 -> 52.46  * .8 -> 41.97  10.49
            male, 42, non-smoker   ->  8.91% * $200000 / 1000 -> 17.82  * .8 -> 14.26   3.56
            female, 17, smoker     ->  2.81% * $200000 / 1000 ->  5.62  * .8 ->  4.50   1.12

        """
        # set up some employees
        m_32_sm = mf.EmployeeFactory(dob=get_date_of_birth(32), salary=100000, gender='M', smoker_type='SM')
        f_50_ns = mf.EmployeeFactory(dob=get_date_of_birth(50), salary=100000, gender='F', smoker_type='NS')
        m_42_ns = mf.EmployeeFactory(dob=get_date_of_birth(42), salary=100000, gender='M', smoker_type='NS')
        f_17_sm = mf.EmployeeFactory(dob=get_date_of_birth(17), salary=100000, gender='F', smoker_type='SM')
        # set up plan
        plan = mf.BasicLifePlanFactory(er_percentage_contributed=.8, multiple_of_salary_paid=2)
        # set up premiums
        matrix = [
            [0, 24, 'SM', 'M', .0381],
            [25, 29, 'SM', 'M', .0469],
            [30, 34, 'SM', 'M', .0598],
            [35, 39, 'SM', 'M', .0663],
            [40, 44, 'SM', 'M', .0991],
            [45, 49, 'SM', 'M', .1517],
            [50, 54, 'SM', 'M', .2823],
            [55, 59, 'SM', 'M', .4332],
            [60, 64, 'SM', 'M', .8329],
            [65, 69, 'SM', 'M', .8329],
            [70, 74, 'SM', 'M', 1.3508],
            [75, 100, 'SM', 'M', 1.3508],
            [0, 24, 'NS', 'M', .0281],
            [25, 29, 'NS', 'M', .0369],
            [30, 34, 'NS', 'M', .0498],
            [35, 39, 'NS', 'M', .0563],
            [40, 44, 'NS', 'M', .0891],
            [45, 49, 'NS', 'M', .1417],
            [50, 54, 'NS', 'M', .2723],
            [55, 59, 'NS', 'M', .4232],
            [60, 64, 'NS', 'M', .8229],
            [65, 69, 'NS', 'M', .8229],
            [70, 74, 'NS', 'M', 1.3408],
            [75, 100, 'NS', 'M', 1.3408],
            [0, 24, 'SM', 'F', .0281],
            [25, 29, 'SM', 'F', .0369],
            [30, 34, 'SM', 'F', .0498],
            [35, 39, 'SM', 'F', .0563],
            [40, 44, 'SM', 'F', .0891],
            [45, 49, 'SM', 'F', .1417],
            [50, 54, 'SM', 'F', .2723],
            [55, 59, 'SM', 'F', .4232],
            [60, 64, 'SM', 'F', .8229],
            [65, 69, 'SM', 'F', .8229],
            [70, 74, 'SM', 'F', 1.3408],
            [75, 100, 'SM', 'F', 1.3408],
            [0, 24, 'NS', 'F', .0181],
            [25, 29, 'NS', 'F', .0269],
            [30, 34, 'NS', 'F', .0398],
            [35, 39, 'NS', 'F', .0463],
            [40, 44, 'NS', 'F', .0791],
            [45, 49, 'NS', 'F', .1317],
            [50, 54, 'NS', 'F', .2623],
            [55, 59, 'NS', 'F', .4132],
            [60, 64, 'NS', 'F', .8129],
            [65, 69, 'NS', 'F', .8129],
            [70, 74, 'NS', 'F', 1.3308],
            [75, 100, 'NS', 'F', 1.3308],
        ]
        premium_factory = mf.AgeBandedPremiumSmokingGenderFactory(plan, matrix)
        plan.premiums = premium_factory.get_premiums()
        db.session.add(plan)
        db.session.commit()

        TOTAL = '$11.96'
        ER = '$9.57'
        EE = '$2.39'
        choices = plan.get_premium_choices(True, m_32_sm)
        for id, label, selected, total, er, ee in choices:
            if label == 'Enroll':
                self.assertEqual(selected, True)
                self.assertEqual(total, TOTAL)
                self.assertEqual(ee, EE)
                self.assertEqual(er, ER)

        TOTAL = '$52.46'
        ER = '$41.97'
        EE = '$10.49'
        choices = plan.get_premium_choices(False, f_50_ns)
        for id, label, selected, total, er, ee in choices:
            if label == 'Enroll':
                self.assertEqual(selected, False)
                self.assertEqual(total, TOTAL)
                self.assertEqual(ee, EE)
                self.assertEqual(er, ER)

        TOTAL = '$17.82'
        ER = '$14.26'
        EE = '$3.56'
        choices = plan.get_premium_choices(True, m_42_ns)
        for id, label, selected, total, er, ee in choices:
            if label == 'Enroll':
                self.assertEqual(selected, True)
                self.assertEqual(total, TOTAL)
                self.assertEqual(ee, EE)
                self.assertEqual(er, ER)

        TOTAL = '$5.62'
        ER = '$4.50'
        EE = '$1.12'
        choices = plan.get_premium_choices(False, f_17_sm)
        for id, label, selected, total, er, ee in choices:
            if label == 'Enroll':
                self.assertEqual(selected, False)
                self.assertEqual(total, TOTAL)
                self.assertEqual(ee, EE)
                self.assertEqual(er, ER)

    def test_boolean_get_premium_choices_ltd(self):
        """
        premium is based on monthly salary / 100 * the rate
        35 yr old has a 5.63% rate, * ((100000 / 12) / 100)  -> 4.67, 3.75, .94
        """
        # set up some employees
        emp = mf.EmployeeFactory(dob=get_date_of_birth(35), salary=100000)
        # set up plan
        plan = mf.LTDPlanFactory(er_percentage_contributed=.8, percentage_of_salary_paid=.6, max_monthly_benefit=5000)
        # set up premiums
        matrix = [
            [0, 24, .0281],
            [25, 29, .0369],
            [30, 34, .0498],
            [35, 39, .0563],
            [40, 44, .0891],
            [45, 49, .1417],
            [50, 54, .2723],
            [55, 59, .4232],
            [60, 64, .8229],
            [65, 69, .8229],
            [70, 74, 1.3408],
            [75, 100, 1.3408]]
        premium_factory = mf.AgeBandedPremiumFactory(plan, matrix)
        plan.premiums = premium_factory.get_premiums()
        db.session.add(plan)
        db.session.commit()

        TOTAL = '$4.67'
        ER = '$3.74'
        EE = '$0.93'
        choices = plan.get_premium_choices(True, emp)
        for id, label, selected, total, er, ee in choices:
            if label == 'Enroll':
                self.assertEqual(selected, True)
                self.assertEqual(total, TOTAL)
                self.assertEqual(ee, EE)
                self.assertEqual(er, ER)

    def test_boolean_get_premium_choices_std(self):
        """
        option 1) cost = benefit amount / (10 * rate)
        option 2) cost = weekly salary / (10 * rate)

        rate is 5.63 for 35 year old
        opt1 benefit amount is $1000 * .6 -> $600
        opt2 weekly salary is $1000
        opt1 cost = $600 / 56.3   -> $10.66
        opt2 cost = $1000 / 56.3  -> $17.76
        """
        emp = mf.EmployeeFactory(dob=get_date_of_birth(35), salary=52000)
        # set up plan
        plan_opt1 = mf.STDPlanFactory(er_percentage_contributed=0, percentage_of_salary_paid=.6,
                                      max_weekly_benefit=1000, premium_based_on_benefit=True)
        plan_opt2 = mf.STDPlanFactory(er_percentage_contributed=0, percentage_of_salary_paid=.6,
                                      max_weekly_benefit=1000)
        # set up premiums
        matrix = [
            [0, 24, 2.81],
            [25, 29, 3.69],
            [30, 34, 4.98],
            [35, 39, 5.63],
            [40, 44, 8.91],
            [45, 49, 14.17],
            [50, 54, 27.23],
            [55, 59, 42.32],
            [60, 64, 82.29],
            [65, 69, 82.29],
            [70, 74, 134.08],
            [75, 100, 134.08]]
        premium_factory = mf.AgeBandedPremiumFactory(plan_opt1, matrix)
        plan_opt1.premiums = premium_factory.get_premiums()
        premium_factory = mf.AgeBandedPremiumFactory(plan_opt2, matrix)
        plan_opt2.premiums = premium_factory.get_premiums()
        db.session.add(plan_opt1)
        db.session.add(plan_opt2)
        db.session.commit()

        TOTAL = '$10.66'
        ER = '$0.00'
        EE = '$10.66'
        choices = plan_opt1.get_premium_choices(True, emp)
        for id, label, selected, total, er, ee in choices:
            if label == 'Enroll':
                self.assertEqual(selected, True)
                self.assertEqual(total, TOTAL)
                self.assertEqual(ee, EE)
                self.assertEqual(er, ER)

        TOTAL = '$17.76'
        ER = '$0.00'
        EE = '$17.76'
        choices = plan_opt2.get_premium_choices(True, emp)
        for id, label, selected, total, er, ee in choices:
            if label == 'Enroll':
                self.assertEqual(selected, True)
                self.assertEqual(total, TOTAL)
                self.assertEqual(ee, EE)
                self.assertEqual(er, ER)

    def test_boolean_get_premium_choices_hra(self):
        emp = mf.EmployeeFactory(dob=get_date_of_birth(35), salary=52000)
        # set up plan
        plan = mf.HRAPlanFactory(er_percentage_contributed=1)
        plans = [
            mf.HRAPlanFactory(er_percentage_contributed=1),
            mf.EAPPlanFactory(er_percentage_contributed=1),
            mf.ParkingTransitPlanFactory(er_percentage_contributed=1),
        ]
        TOTAL = '$250.00'
        ER = '$250.00'
        EE = '$0.00'
        for plan in plans:
            plan.premiums = [mf.PremiumFactory(amount=250, plan=plan)]
            db.session.add(plan)
            db.session.commit()

            choices = plan.get_premium_choices(True, emp)
            for id, label, selected, total, er, ee in choices:
                if label == 'Enroll':
                    self.assertEqual(selected, True)
                    self.assertEqual(total, TOTAL)
                    self.assertEqual(ee, EE)
                    self.assertEqual(er, ER)

    def test_boolean_get_premium_choices_flat_amt_greater_than_premium(self):
        emp = mf.EmployeeFactory(dob=get_date_of_birth(35), salary=52000)
        # set up plan
        plan = mf.HRAPlanFactory(er_percentage_contributed=1)
        plans = [
            mf.HRAPlanFactory(er_flat_amount_contributed=200),
            mf.EAPPlanFactory(er_flat_amount_contributed=200),
            mf.ParkingTransitPlanFactory(er_flat_amount_contributed=200),
        ]
        TOTAL = '$150.00'
        ER = '$150.00'
        EE = '$0.00'
        for plan in plans:
            plan.premiums = [mf.PremiumFactory(amount=150, plan=plan)]
            db.session.add(plan)
            db.session.commit()

            choices = plan.get_premium_choices(True, emp)
            for id, label, selected, total, er, ee in choices:
                if label == 'Enroll':
                    self.assertEqual(selected, True)
                    self.assertEqual(total, TOTAL)
                    self.assertEqual(ee, EE)
                    self.assertEqual(er, ER)

    # tiered_election get_premium_choices
    def test_tiered_get_premium_choices_single_tiers(self):
        emp = mf.EmployeeFactory(dob=get_date_of_birth(35), salary=52000)
        plans = [
            mf.MedicalPlanFactory(er_percentage_contributed=1),
            mf.DentalPlanFactory(er_percentage_contributed=1),
            mf.VisionPlanFactory(er_percentage_contributed=1),
            mf.MedicalDentalVisionBundlePlanFactory(er_percentage_contributed=1),
            mf.MedicalDentalBundlePlanFactory(er_percentage_contributed=1),
            mf.MedicalVisionBundlePlanFactory(er_percentage_contributed=1),
            mf.DentalVisionBundlePlanFactory(er_percentage_contributed=1),
            mf.LongTermCarePlanFactory(er_percentage_contributed=1),
            mf.CriticalIllnessPlanFactory(er_percentage_contributed=1),
            mf.CancerPlanFactory(er_percentage_contributed=1),
            mf.AccidentPlanFactory(er_percentage_contributed=1),
            mf.HospitalConfinementPlanFactory(er_percentage_contributed=1),
            mf.IdentityTheftPlanFactory(er_percentage_contributed=1),
            mf.OtherPlanFactory(er_percentage_contributed=1),
        ]
        matrix = [
            ['EO', '100'],
            ['ES', '200'],
            ['EC', '225'],
            ['EF', '300'],
        ]
        for idx, plan in enumerate(plans):
            premium_factory = mf.TieredPremiumFactory(plan, matrix)
            plan.premiums = premium_factory.get_premiums()
            db.session.add(plan)
            db.session.commit()

            choices = plan.get_premium_choices('', emp)
            expected = [
                ('EF|{}'.format(idx * 4 + 4), 'Employee and Family', False, '$300.00', '$300.00', '$0.00'),
                ('EC|{}'.format(idx * 4 + 3), 'Employee and Children', False, '$225.00', '$225.00', '$0.00'),
                ('ES|{}'.format(idx * 4 + 2), 'Employee and Spouse', False, '$200.00', '$200.00', '$0.00'),
                ('EO|{}'.format(idx * 4 + 1), 'Employee Only', False, '$100.00', '$100.00', '$0.00'),
                ('DE', 'Decline', False, '', '', '')
            ]
            self.assertSequenceEqual(choices, expected)

    def test_tiered_get_premium_choices_single_tiers_flat_amt_greater_than_premium(self):
        emp = mf.EmployeeFactory(dob=get_date_of_birth(35), salary=52000)
        plans = [
            mf.MedicalPlanFactory(er_flat_amount_contributed=215),
            mf.DentalPlanFactory(er_flat_amount_contributed=215),
            mf.VisionPlanFactory(er_flat_amount_contributed=215),
            mf.MedicalDentalVisionBundlePlanFactory(er_flat_amount_contributed=215),
            mf.MedicalDentalBundlePlanFactory(er_flat_amount_contributed=215),
            mf.MedicalVisionBundlePlanFactory(er_flat_amount_contributed=215),
            mf.DentalVisionBundlePlanFactory(er_flat_amount_contributed=215),
            mf.LongTermCarePlanFactory(er_flat_amount_contributed=215),
            mf.CriticalIllnessPlanFactory(er_flat_amount_contributed=215),
            mf.CancerPlanFactory(er_flat_amount_contributed=215),
            mf.AccidentPlanFactory(er_flat_amount_contributed=215),
            mf.HospitalConfinementPlanFactory(er_flat_amount_contributed=215),
            mf.IdentityTheftPlanFactory(er_flat_amount_contributed=215),
            mf.OtherPlanFactory(er_flat_amount_contributed=215),
        ]
        matrix = [
            ['EO', '100'],
            ['ES', '200'],
            ['EC', '225'],
            ['EF', '300'],
        ]
        for idx, plan in enumerate(plans):
            premium_factory = mf.TieredPremiumFactory(plan, matrix)
            plan.premiums = premium_factory.get_premiums()
            db.session.add(plan)
            db.session.commit()

            choices = plan.get_premium_choices('', emp)
            expected = [
                ('EF|{}'.format(idx * 4 + 4), 'Employee and Family', False, '$300.00', '$215.00', '$85.00'),
                ('EC|{}'.format(idx * 4 + 3), 'Employee and Children', False, '$225.00', '$215.00', '$10.00'),
                ('ES|{}'.format(idx * 4 + 2), 'Employee and Spouse', False, '$200.00', '$200.00', '$0.00'),
                ('EO|{}'.format(idx * 4 + 1), 'Employee Only', False, '$100.00', '$100.00', '$0.00'),
                ('DE', 'Decline', False, '', '', '')
            ]
            self.assertSequenceEqual(choices, expected)

    def test_tiered_get_premium_choices_age_banded_smoker(self):
        emp = mf.EmployeeFactory(dob=get_date_of_birth(20), smoker_type='NS')
        matrix = [
            ['SM', 17, 24, 'EO', 13],   # 1
            ['SM', 25, 45, 'EO', 22],   # 2
            ['SM', 46, 90, 'EO', 40],   # 3
            ['NS', 17, 24, 'EO', 8],    # 4
            ['NS', 25, 45, 'EO', 17],   # 5
            ['NS', 46, 90, 'EO', 35],   # 6
            ['SM', 17, 24, 'ES', 23],   # 7
            ['SM', 25, 45, 'ES', 32],   # 8
            ['SM', 46, 90, 'ES', 50],   # 9
            ['NS', 17, 24, 'ES', 18],   # 10
            ['NS', 25, 45, 'ES', 27],   # 11
            ['NS', 46, 90, 'ES', 45],   # 12
            ['SM', 17, 24, 'EC', 23],   # 13
            ['SM', 25, 45, 'EC', 32],   # 14
            ['SM', 46, 90, 'EC', 50],   # 15
            ['NS', 17, 24, 'EC', 18],   # 16
            ['NS', 25, 45, 'EC', 27],   # 17
            ['NS', 46, 90, 'EC', 45],   # 18
            ['SM', 17, 24, 'EF', 33],   # 19
            ['SM', 25, 45, 'EF', 42],   # 20
            ['SM', 46, 90, 'EF', 60],   # 21
            ['NS', 17, 24, 'EF', 28],   # 22
            ['NS', 25, 45, 'EF', 37],   # 23
            ['NS', 46, 90, 'EF', 55],   # 24
        ]
        plans = [
            mf.MedicalPlanFactory(er_flat_amount_contributed=5),
            mf.DentalPlanFactory(er_flat_amount_contributed=5),
            mf.VisionPlanFactory(er_flat_amount_contributed=5),
            mf.MedicalDentalVisionBundlePlanFactory(er_flat_amount_contributed=5),
            mf.MedicalDentalBundlePlanFactory(er_flat_amount_contributed=5),
            mf.MedicalVisionBundlePlanFactory(er_flat_amount_contributed=5),
            mf.DentalVisionBundlePlanFactory(er_flat_amount_contributed=5),
            mf.LongTermCarePlanFactory(er_flat_amount_contributed=5),
            mf.CriticalIllnessPlanFactory(er_flat_amount_contributed=5),
            mf.CancerPlanFactory(er_flat_amount_contributed=5),
            mf.AccidentPlanFactory(er_flat_amount_contributed=5),
            mf.HospitalConfinementPlanFactory(er_flat_amount_contributed=5),
            mf.IdentityTheftPlanFactory(er_flat_amount_contributed=5),
            mf.OtherPlanFactory(er_flat_amount_contributed=5),
        ]
        for idx, plan in enumerate(plans):
            premium_factory = mf.AgeBandedPremiumSmokingTieredFactory(plan, matrix)
            plan.premiums = premium_factory.get_premiums()
            db.session.add(plan)
            db.session.commit()

            choices = plan.get_premium_choices(u'EF|{}'.format(idx * 24 + 22), emp)

            expected = [
                (u'EF|{}'.format(idx * 24 + 22), u'Employee and Family', True, '$28.00', '$5.00', '$23.00'),
                (u'EC|{}'.format(idx * 24 + 16), u'Employee and Children', False, '$18.00', '$5.00', '$13.00'),
                (u'ES|{}'.format(idx * 24 + 10), u'Employee and Spouse', False, '$18.00', '$5.00', '$13.00'),
                (u'EO|{}'.format(idx * 24 + 4), u'Employee Only', False, '$8.00', '$5.00', '$3.00'),
                ('DE', 'Decline', False, '', '', '')]

            self.assertSequenceEqual(choices, expected)

    def test_tiered_get_premium_choices_age_banded_smoker_gender(self):
        jack = mf.EmployeeFactory(dob=get_date_of_birth(20), smoker_type='NS', gender='M')
        jill = mf.EmployeeFactory(dob=get_date_of_birth(30), smoker_type='SM', gender='F')
        matrix = [
            ['M', 'SM', 17, 24, 'EO', 14],   # 1
            ['M', 'SM', 25, 45, 'EO', 23],   # 2
            ['M', 'SM', 46, 90, 'EO', 41],   # 3
            ['M', 'NS', 17, 24, 'EO', 9],    # 4
            ['M', 'NS', 25, 45, 'EO', 18],   # 5
            ['M', 'NS', 46, 90, 'EO', 36],   # 6
            ['M', 'SM', 17, 24, 'ES', 24],   # 7
            ['M', 'SM', 25, 45, 'ES', 33],   # 8
            ['M', 'SM', 46, 90, 'ES', 51],   # 9
            ['M', 'NS', 17, 24, 'ES', 19],   # 10
            ['M', 'NS', 25, 45, 'ES', 28],   # 11
            ['M', 'NS', 46, 90, 'ES', 46],   # 12
            ['M', 'SM', 17, 24, 'EC', 24],   # 13
            ['M', 'SM', 25, 45, 'EC', 33],   # 14
            ['M', 'SM', 46, 90, 'EC', 51],   # 15
            ['M', 'NS', 17, 24, 'EC', 19],   # 16
            ['M', 'NS', 25, 45, 'EC', 28],   # 17
            ['M', 'NS', 46, 90, 'EC', 46],   # 18
            ['M', 'SM', 17, 24, 'EF', 34],   # 19
            ['M', 'SM', 25, 45, 'EF', 43],   # 20
            ['M', 'SM', 46, 90, 'EF', 61],   # 21
            ['M', 'NS', 17, 24, 'EF', 29],   # 22
            ['M', 'NS', 25, 45, 'EF', 38],   # 23
            ['M', 'NS', 46, 90, 'EF', 56],   # 24
            ['F', 'SM', 17, 24, 'EO', 13],   # 25
            ['F', 'SM', 25, 45, 'EO', 22],   # 26
            ['F', 'SM', 46, 90, 'EO', 40],   # 27
            ['F', 'NS', 17, 24, 'EO', 8],    # 28
            ['F', 'NS', 25, 45, 'EO', 17],   # 29
            ['F', 'NS', 46, 90, 'EO', 35],   # 30
            ['F', 'SM', 17, 24, 'ES', 23],   # 31
            ['F', 'SM', 25, 45, 'ES', 32],   # 32
            ['F', 'SM', 46, 90, 'ES', 50],   # 33
            ['F', 'NS', 17, 24, 'ES', 18],   # 34
            ['F', 'NS', 25, 45, 'ES', 27],   # 35
            ['F', 'NS', 46, 90, 'ES', 45],   # 36
            ['F', 'SM', 17, 24, 'EC', 23],   # 37
            ['F', 'SM', 25, 45, 'EC', 32],   # 38
            ['F', 'SM', 46, 90, 'EC', 50],   # 39
            ['F', 'NS', 17, 24, 'EC', 18],   # 40
            ['F', 'NS', 25, 45, 'EC', 27],   # 41
            ['F', 'NS', 46, 90, 'EC', 45],   # 42
            ['F', 'SM', 17, 24, 'EF', 33],   # 43
            ['F', 'SM', 25, 45, 'EF', 42],   # 44
            ['F', 'SM', 46, 90, 'EF', 60],   # 45
            ['F', 'NS', 17, 24, 'EF', 28],   # 46
            ['F', 'NS', 25, 45, 'EF', 37],   # 47
            ['F', 'NS', 46, 90, 'EF', 55],   # 48
        ]
        plans = [
            mf.MedicalPlanFactory(er_percentage_contributed=.8),
            mf.DentalPlanFactory(er_percentage_contributed=.8),
            mf.VisionPlanFactory(er_percentage_contributed=.8),
            mf.MedicalDentalVisionBundlePlanFactory(er_percentage_contributed=.8),
            mf.MedicalDentalBundlePlanFactory(er_percentage_contributed=.8),
            mf.MedicalVisionBundlePlanFactory(er_percentage_contributed=.8),
            mf.DentalVisionBundlePlanFactory(er_percentage_contributed=.8),
            mf.LongTermCarePlanFactory(er_percentage_contributed=.8),
            mf.CriticalIllnessPlanFactory(er_percentage_contributed=.8),
            mf.CancerPlanFactory(er_percentage_contributed=.8),
            mf.AccidentPlanFactory(er_percentage_contributed=.8),
            mf.HospitalConfinementPlanFactory(er_percentage_contributed=.8),
            mf.IdentityTheftPlanFactory(er_percentage_contributed=.8),
            mf.OtherPlanFactory(er_percentage_contributed=.8),
        ]
        for idx, plan in enumerate(plans):
            premium_factory = mf.AgeBandedPremiumSmokingGenderTieredFactory(plan, matrix)
            plan.premiums = premium_factory.get_premiums()
            db.session.add(plan)
            db.session.commit()

            jack_choices = plan.get_premium_choices(u'EF|{}'.format(idx * 48 + 22), jack)
            jill_choices = plan.get_premium_choices(u'EO|{}'.format(idx * 48 + 26), jill)

            jack_expected = [
                (u'EF|{}'.format(idx * 48 + 22), u'Employee and Family', True, '$29.00', '$23.20', '$5.80'),
                (u'EC|{}'.format(idx * 48 + 16), u'Employee and Children', False, '$19.00', '$15.20', '$3.80'),
                (u'ES|{}'.format(idx * 48 + 10), u'Employee and Spouse', False, '$19.00', '$15.20', '$3.80'),
                (u'EO|{}'.format(idx * 48 + 4), u'Employee Only', False, '$9.00', '$7.20', '$1.80'),
                ('DE', 'Decline', False, '', '', '')]

            jill_expected = [
                (u'EF|{}'.format(idx * 48 + 44), u'Employee and Family', False, '$42.00', '$33.60', '$8.40'),
                (u'EC|{}'.format(idx * 48 + 38), u'Employee and Children', False, '$32.00', '$25.60', '$6.40'),
                (u'ES|{}'.format(idx * 48 + 32), u'Employee and Spouse', False, '$32.00', '$25.60', '$6.40'),
                (u'EO|{}'.format(idx * 48 + 26), u'Employee Only', True, '$22.00', '$17.60', '$4.40'),
                ('DE', 'Decline', False, '', '', '')]

            self.assertSequenceEqual(jack_choices, jack_expected)
            self.assertSequenceEqual(jill_choices, jill_expected)

    # AmountChosenElectionMixin VoluntaryLife, StandaloneADD, WholeLife, UniversalLife
    def test_amount_chosen_get_premium_choices(self):
        emp = mf.EmployeeFactory(dob=get_date_of_birth(35), salary=52000)
        # set up plan
        plans = [
            mf.VoluntaryLifePlanFactory(er_percentage_contributed=0, min_election=10000,
                                        max_election=40000, increments=10000),
            mf.StandaloneADDPlanFactory(er_percentage_contributed=0, min_election=10000,
                                        max_election=40000, increments=10000),
        ]
        matrix = [
            [0, 24, 2.81],        # 1
            [25, 29, 3.69],       # 2
            [30, 34, 4.98],       # 3
            [35, 39, 5.63],       # 4
            [40, 44, 8.91],       # 5
            [45, 49, 14.17],      # 6
            [50, 54, 27.23],      # 7
            [55, 59, 42.32],      # 8
            [60, 64, 82.29],      # 9
            [65, 69, 82.29],      # 10
            [70, 74, 134.08],     # 11
            [75, 100, 134.08]]    # 12
        for idx, plan in enumerate(plans):
            expected = [
                (u'10000|{}'.format(idx * 12 + 4), 10000, False, '$56.30', '$0.00', '$56.30'),
                (u'20000|{}'.format(idx * 12 + 4), 20000, False, '$112.60', '$0.00', '$112.60'),
                (u'30000|{}'.format(idx * 12 + 4), 30000, True, '$168.90', '$0.00', '$168.90'),
                (u'40000|{}'.format(idx * 12 + 4), 40000, False, '$225.20', '$0.00', '$225.20'),
                (u'DE', u'Decline', False, u'', u'', u'')
            ]
            premium_factory = mf.AgeBandedPremiumFactory(plan, matrix)
            plan.premiums = premium_factory.get_premiums()
            db.session.add(plan)
            db.session.commit()

            choices = plan.get_premium_choices('30000|4', emp)

            self.assertSequenceEqual(choices, expected)

    def test_amount_chosen_get_premium_choices_payout(self):
        emp_17_sm = mf.EmployeeFactory(dob=get_date_of_birth(17), smoker_type='SM')
        emp_48_ns = mf.EmployeeFactory(dob=get_date_of_birth(48), smoker_type='NS')
        emp_59_ns = mf.EmployeeFactory(dob=get_date_of_birth(59), smoker_type='NS')
        # set up plan
        plans = [
            mf.WholeLifePlanFactory(er_percentage_contributed=0),
            mf.UniversalLifePlanFactory(er_percentage_contributed=0),
        ]
        # abbreviated matrix with all entries for ages 17 (8), 48 (6) and 59 (2)
        matrix = [
            [17, 'NS', 50000, 8.93],      # 1
            [17, 'SM', 50000, 10.43],     # 2
            [17, 'NS', 75000, 7.93],      # 3
            [17, 'SM', 75000, 9.43],      # 4
            [17, 'NS', 100000, 9.93],     # 5
            [17, 'SM', 100000, 11.43],    # 6
            [17, 'NS', 150000, 11.93],    # 7
            [17, 'SM', 150000, 13.43],    # 8
            [48, 'NS', 50000, 28.04],     # 9
            [48, 'SM', 50000, 36.35],     # 10
            [48, 'NS', 75000, 29.04],     # 11
            [48, 'SM', 75000, 37.35],     # 12
            [48, 'NS', 100000, 31.04],    # 13
            [48, 'SM', 100000, 39.35],    # 14
            [59, 'NS', 50000, 30.53],     # 15
            [59, 'SM', 50000, 39.101],    # 16
        ]
        for idx, plan in enumerate(plans):
            expected_emp_17_sm = [
                (u'150000|{}'.format(idx * 16 + 8), 150000, False, '$13.43', '$0.00', '$13.43'),
                (u'100000|{}'.format(idx * 16 + 6), 100000, False, '$11.43', '$0.00', '$11.43'),
                (u'75000|{}'.format(idx * 16 + 4), 75000, False, '$9.43', '$0.00', '$9.43'),
                (u'50000|{}'.format(idx * 16 + 2), 50000, False, '$10.43', '$0.00', '$10.43'),
                (u'DE', u'Decline', False, u'', u'', u''),
            ]
            expected_emp_48_ns = [
                (u'100000|{}'.format(idx * 16 + 13), 100000, False, '$31.04', '$0.00', '$31.04'),
                (u'75000|{}'.format(idx * 16 + 11), 75000, False, '$29.04', '$0.00', '$29.04'),
                (u'50000|{}'.format(idx * 16 + 9), 50000, False, '$28.04', '$0.00', '$28.04'),
                (u'DE', u'Decline', False, u'', u'', u''),
            ]
            expected_emp_59_ns = [
                (u'50000|{}'.format(idx * 16 + 15), 50000, False, '$30.53', '$0.00', '$30.53'),
                (u'DE', u'Decline', False, u'', u'', u''),
            ]
            premium_factory = mf.AgeSmokingPayoutPremiumFactory(plan, matrix)
            plan.premiums = premium_factory.get_premiums()
            db.session.add(plan)
            db.session.commit()

            emp_17_sm_choices = plan.get_premium_choices('', emp_17_sm)
            emp_48_ns_choices = plan.get_premium_choices('', emp_48_ns)
            emp_59_ns_choices = plan.get_premium_choices('', emp_59_ns)

            self.assertSequenceEqual(emp_17_sm_choices, expected_emp_17_sm)
            self.assertSequenceEqual(emp_48_ns_choices, expected_emp_48_ns)
            self.assertSequenceEqual(emp_59_ns_choices, expected_emp_59_ns)

    # AmountSupplied FSAMedical, FSADependentCare, HSA, 401K
    def test_amount_supplied_get_premium_choices(self):
        emp = mf.EmployeeFactory(dob=get_date_of_birth(47))
        plans = [
            mf.FSAMedicalPlanFactory(er_percentage_contributed=0, min_contribution=250),
            mf.FSADependentCarePlanFactory(er_percentage_contributed=0, min_contribution=500),
            mf.HSAPlanFactory(er_percentage_contributed=0, min_contribution=750),
            mf.Employee401KPlanFactory(er_percentage_contributed=0, employer_max_contribution=6000,
                                       min_contribution=1000),
        ]
        limits = mf.IRSLimitsFactory()
        db.session.add(limits)
        db.session.commit()

        expected_fsa_medical = [(250, Decimal('1200.00'), None, 0, 0, 0)]
        expected_fsa_dependent = [(500, Decimal('1200.00'), None, 0, 0, 0)]
        expected_hsa = [(750, Decimal('800.00'), None, 0, 0, 0)]
        expected_401k = [(1000, Decimal('5000.00'), None, 0, 0, 0)]
        expectations = [
            expected_fsa_medical,
            expected_fsa_dependent,
            expected_hsa,
            expected_401k,
        ]
        for plan, expected in zip(plans, expectations):
            choices = plan.get_premium_choices('|', emp)

            self.assertSequenceEqual(choices, expected)
