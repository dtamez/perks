#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from datetime import date
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
import logging
import logzero
import os

from tests.test_models import get_date_of_birth

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from app import create_app, db  # NOQA


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


def add_plan(plan_factory, name, carrier, matrix, premium_factory, er_percentage_contributed=0,
             er_flat_amount_contributed=0, required_plan=None):
    plan = plan_factory(name=name, carrier=carrier, er_percentage_contributed=er_percentage_contributed,
                        er_flat_amount_contributed=er_flat_amount_contributed)
    pf = premium_factory(plan, matrix)
    plan.premiums = pf.get_premiums()
    if required_plan:
        plan.required_plan = required_plan

    db.session.add(plan)
    db.session.commit()
    return plan


@manager.command
def seed_data():
    from app.models import IRSLimits

    limits = IRSLimits()
    limits.max_401k_salary_deferal = 100000
    limits.max_401k_salary_deferal_over_50 = 11000
    limits.max_fsa_dependent_care_contribution = 2200
    limits.max_fsa_medical_contribution = 3000
    limits.max_hsa_family_contribution = 4600
    limits.max_hsa_family_over_55_contribution = 5500
    limits.max_hsa_individual_contribution = 2600

    db.session.add(limits)
    db.session.commit()

    from tests import model_factory as mf
    # locations
    hou = mf.LocationFactory(code='HOU', description='Houston Office')
    dal = mf.LocationFactory(code='DAL', description='Dallas Office')
    db.session.add_all([hou, dal])
    db.session.commit()

    # employees and dependents
    jane = mf.DependentFactory(first_name='Jane', last_name='Doe', dependent_type='wife', gender='F')
    jill = mf.DependentFactory(first_name='Jill', last_name='Doe', dependent_type='daughter', gender='F')
    bill = mf.DependentFactory(first_name='Bill', last_name='Doe', dependent_type='son', gender='M')
    u_joe = mf.UserFactory(email='joe@doe.com', password='password')
    dob = get_date_of_birth(48)
    joe = mf.EmployeeFactory(location=hou, first_name='Joe', last_name='Doe', gender='M',
                             dependents=[jane, jill, bill], user=u_joe, dob=dob)

    sam = mf.DependentFactory(first_name='Sam', last_name='Blue', dependent_type='husband', gender='M')
    mary = mf.DependentFactory(first_name='Mary', last_name='Blue', dependent_type='daughter', gender='F')
    harry = mf.DependentFactory(first_name='Harry', last_name='Blue', dependent_type='son', gender='M')
    u_sue = mf.UserFactory(email='sue@blue.com', password='password')
    sue = mf.EmployeeFactory(location=dal, first_name='Sue', last_name='Blue', gender='F',
                             dependents=[sam, mary, harry], user=u_sue, dob=dob)
    db.session.add_all([jane, jill, bill, joe, sam, mary, harry, sue])
    db.session.commit()

    # carriers
    aetna = mf.CarrierFactory(name='Aetna')
    cigna = mf.CarrierFactory(name='Cigna')
    met_life = mf.CarrierFactory(name='Mettopolitan Life')
    db.session.add_all([aetna, cigna, met_life])
    db.session.commit()

    # TIERED ELECTION
    # medical plans
    matrix = [
        ['EO', '100'],
        ['ES', '200'],
        ['EC', '225'],
        ['EF', '300'],
    ]
    add_plan(mf.MedicalPlanFactory, 'Medical Base Plan', cigna, matrix, mf.TieredPremiumFactory,
             er_percentage_contributed=1)
    matrix = [
        ['EO', '150'],
        ['ES', '250'],
        ['EC', '275'],
        ['EF', '350'],
    ]
    med_buy_up = add_plan(mf.MedicalPlanFactory, 'Medical Buy Up Plan', aetna, matrix, mf.TieredPremiumFactory,
                          er_percentage_contributed=.8)

    # dental plans
    matrix = [
        ['EO', '50'],
        ['ES', '75'],
        ['EC', '100'],
        ['EF', '125'],
    ]
    add_plan(mf.DentalPlanFactory, 'Dental Base Plan', aetna, matrix, mf.TieredPremiumFactory,
             er_percentage_contributed=1)
    matrix = [
        ['EO', '75'],
        ['ES', '125'],
        ['EC', '150'],
        ['EF', '175'],
    ]
    add_plan(mf.DentalPlanFactory, 'Dental Buy Up Plan', aetna, matrix, mf.TieredPremiumFactory,
             er_percentage_contributed=.6)

    # vision plans
    matrix = [
        ['EO', '30'],
        ['ES', '45'],
        ['EC', '60'],
        ['EF', '75'],
    ]
    add_plan(mf.VisionPlanFactory, 'Vision Plan', aetna, matrix, mf.TieredPremiumFactory,
             er_flat_amount_contributed=30)

    # Long Term Care Plan
    matrix = [
        ['EO', '150'],
        ['ES', '250'],
        ['EC', '275'],
        ['EF', '350'],
    ]
    add_plan(mf.LongTermCarePlanFactory, 'Long Term Care Plan', met_life, matrix, mf.TieredPremiumFactory)

    # Criticcl Illness Plan
    matrix = [
        ['EO', '100'],
        ['ES', '125'],
        ['EC', '150'],
        ['EF', '200'],
    ]
    add_plan(mf.CriticalIllnessPlanFactory, 'Critical Illnes Plan', met_life, matrix, mf.TieredPremiumFactory)

    # Cancer Plan
    matrix = [
        ['EO', '100'],
        ['ES', '125'],
        ['EC', '150'],
        ['EF', '200'],
    ]
    add_plan(mf.CancerPlanFactory, 'Cancer Plan', met_life, matrix, mf.TieredPremiumFactory)

    # Accident Plan
    matrix = [
        ['EO', '100'],
        ['ES', '125'],
        ['EC', '150'],
        ['EF', '200'],
    ]
    add_plan(mf.AccidentPlanFactory, 'Accident Plan', met_life, matrix, mf.TieredPremiumFactory)

    # Hospital Confinement Plan
    matrix = [
        ['EO', '50'],
        ['ES', '70'],
        ['EC', '100'],
        ['EF', '120'],
    ]
    add_plan(mf.HospitalConfinementPlanFactory, 'Hospital Confinement Plan', met_life, matrix, mf.TieredPremiumFactory)

    # Identity Theft Plan
    matrix = [
        ['EO', '20'],
        ['ES', '30'],
        ['EC', '40'],
        ['EF', '60'],
    ]
    add_plan(mf.IdentityTheftPlanFactory, 'Identity Theft Protection Plan', met_life, matrix,
             mf.TieredPremiumFactory)

    # AMOUNT CHOSEN ELECTION
    # Voluntary Life
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
    ee_voluntary_life = add_plan(mf.VoluntaryLifePlanFactory, 'Employee Voluntary Life Plan', met_life, matrix,
                                 mf.AgeBandedPremiumFactory)
    ee_standalone_add = add_plan(mf.StandaloneADDPlanFactory, 'Employee Standalone AD&D Plan', met_life, matrix,
                                 mf.AgeBandedPremiumFactory)

    matrix = [
        [0, 24, 1.81],
        [25, 29, 2.69],
        [30, 34, 3.98],
        [35, 39, 4.63],
        [40, 44, 7.91],
        [45, 49, 13.17],
        [50, 54, 26.23],
        [55, 59, 41.32],
        [60, 64, 81.29],
        [65, 69, 81.29],
        [70, 74, 133.08],
        [75, 100, 133.08]]
    add_plan(mf.SpouseVoluntaryLifePlanFactory, 'Spouse Voluntary Life Plan', met_life, matrix,
             mf.AgeBandedPremiumFactory, required_plan=ee_voluntary_life)
    add_plan(mf.SpouseStandaloneADDPlanFactory, 'Spouse Standalone AD&D Plan', met_life, matrix,
             mf.AgeBandedPremiumFactory, required_plan=ee_standalone_add)

    matrix = [[0, 24, 0.81]]
    add_plan(mf.ChildVoluntaryLifePlanFactory, 'Child Voluntary Life Plan', met_life, matrix,
             mf.AgeBandedPremiumFactory, required_plan=ee_voluntary_life)
    add_plan(mf.ChildStandaloneADDPlanFactory, 'Child Standalone AD&D Plan', met_life, matrix,
             mf.AgeBandedPremiumFactory, required_plan=ee_standalone_add)

    # Whole Life & Universal Life
    matrix = [
        [0, 17, 'NS', 50000, 8.93],
        [0, 17, 'SM', 50000, 10.43],
        [0, 17, 'NS', 75000, 7.93],
        [0, 17, 'SM', 75000, 9.43],
        [0, 17, 'NS', 100000, 9.93],
        [0, 17, 'SM', 100000, 11.43],
        [0, 17, 'NS', 150000, 11.93],
        [0, 17, 'SM', 150000, 13.43],
        [18, 48, 'NS', 50000, 28.04],
        [18, 48, 'SM', 50000, 36.35],
        [18, 48, 'NS', 75000, 29.04],
        [18, 48, 'SM', 75000, 37.35],
        [18, 48, 'NS', 100000, 31.04],
        [18, 48, 'SM', 100000, 39.35],
        [49, 59, 'NS', 50000, 30.53],
        [49, 59, 'SM', 50000, 39.101],
    ]
    add_plan(mf.WholeLifePlanFactory, 'Whole Life Plan', met_life, matrix,
             mf.AgeBandedSmokingPayoutPremiumFactory)
    add_plan(mf.UniversalLifePlanFactory, 'Universal Life Plan', met_life, matrix,
             mf.AgeBandedSmokingPayoutPremiumFactory)

    # FSA Medical
    plan = mf.FSAMedicalPlanFactory(name='FSA Medical Plan')
    db.session.add(plan)
    db.session.commit()

    # FSA Dependent Care
    plan = mf.FSADependentCarePlanFactory(name='FSA Dependent Care Plan')
    db.session.add(plan)
    db.session.commit()

    # HSA
    plan = mf.HSAPlanFactory(name='HSA Plan')
    plan.required_plan = med_buy_up
    db.session.add(plan)
    db.session.commit()

    # 401K
    plan = mf.Employee401KPlanFactory(name='Employee 401K Plan')
    db.session.add(plan)
    db.session.commit()

    # BOOLEAN ELECTION
    # Basic Life
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
    add_plan(mf.BasicLifePlanFactory, 'Basic Life Plan', met_life, matrix,
             mf.AgeBandedPremiumFactory, er_percentage_contributed=1)

    # Long Term Disability
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
    add_plan(mf.LTDPlanFactory, 'Long Term Disability Plan', met_life, matrix,
             mf.AgeBandedPremiumFactory)

    # Short Term Disability
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
    add_plan(mf.STDPlanFactory, 'Short Term Disability Plan', met_life, matrix,
             mf.AgeBandedPremiumFactory)

    plan = mf.HRAPlanFactory(name='Health Reimbursement Plan')
    plan.premiums = [mf.PremiumFactory(amount=250, plan=plan)]
    db.session.add(plan)
    db.session.commit()

    plan = mf.EAPPlanFactory(name='Employee Assistance Plan', er_percentage_contributed=.8)
    plan.premiums = [mf.PremiumFactory(amount=250, plan=plan)]
    db.session.add(plan)
    db.session.commit()

    plan = mf.ParkingTransitPlanFactory(name='Parking Transit Plan', er_percentage_contributed=1)
    plan.premiums = [mf.PremiumFactory(amount=250, plan=plan)]
    db.session.add(plan)
    db.session.commit()


@manager.command
@manager.option('-e', '--email', help='Admin email address')
def create_admin(email, password):
    from app.models import User

    admin = User()
    admin.active = True
    admin.confirmed_at = date.today()
    admin.email = email
    admin.password = password
    admin.is_admin = True

    db.session.add(admin)
    db.session.commit()


def make_shell_context():
    from app import models
    return dict(app=app, db=db, models=models)


manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    logzero.loglevel(level=logging.FATAL)
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


if __name__ == "__main__":
    manager.run()
