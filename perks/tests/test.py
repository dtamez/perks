#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Tests!
"""
from flask_testing import TestCase

from .. import app, db
from ..models import TierType, User
from .model_factory import (
    BeneficiaryFactory,
    CancerPlanFactory,
    CancerTieredPremiumFactory,
    CarrierFactory,
    DentalPlanFactory,
    DentalTieredPremiumFactory,
    DependentFactory,
    Employee401KPlanFactory,
    Employee401KTieredPremiumFactory,
    EmployeeFactory,
    MedicalPlanFactory,
    MedicalTieredPremiumFactory,
    ParkingTransitPlanFactory,
    ParkingTransitTieredPremiumFactory,
    SupplumentalInsurancePlanFactory,
    SupllementalInsuranceTieredPremiumFactory,
    VisionPlanFactory,
    VisionTieredPremiumFactory,
)


class TestModels(TestCase):

    def create_app(self):
        return app

    def test_nothing(self):

        # set up an employee
        dt = User.query.filter(User.username == 'dtamez').one()

        deps = (DependentFactory(last_name=dt.last_name),
                DependentFactory(last_name=dt.last_name),
                DependentFactory(last_name=dt.last_name))

        bens = (BeneficiaryFactory(last_name=dt.last_name),)

        emp = EmployeeFactory.create(user=dt, dependents=deps,
                                     beneficiaries=bens)
        db.session.add(emp)
        db.session.commit()

        # carriers
        carrier = CarrierFactory()
        db.session.add(carrier)
        db.session.commit()

        # medical plan 1
        med_plan = MedicalPlanFactory(carrier_id=carrier.id)
        db.session.add(med_plan)
        db.session.commit()
        eo_premium = MedicalTieredPremiumFactory(
            plan=med_plan, tier_type=TierType.employee_only)
        es_premium = MedicalTieredPremiumFactory(
            plan=med_plan, tier_type=TierType.employee_spouse)
        ec_premium = MedicalTieredPremiumFactory(
            plan=med_plan, tier_type=TierType.employee_children)
        ef_premium = MedicalTieredPremiumFactory(
            plan=med_plan, tier_type=TierType.employee_family)
        db.session.add(eo_premium)
        db.session.add(es_premium)
        db.session.add(ec_premium)
        db.session.add(ef_premium)
        db.session.commit()

        # medical plan 2
        med_plan_2 = MedicalPlanFactory(carrier_id=carrier.id)
        db.session.add(med_plan)
        db.session.commit()
        eo_premium = MedicalTieredPremiumFactory(
            plan=med_plan_2, tier_type=TierType.employee_only)
        es_premium = MedicalTieredPremiumFactory(
            plan=med_plan_2, tier_type=TierType.employee_spouse)
        ec_premium = MedicalTieredPremiumFactory(
            plan=med_plan_2, tier_type=TierType.employee_children)
        ef_premium = MedicalTieredPremiumFactory(
            plan=med_plan_2, tier_type=TierType.employee_family)
        db.session.add(eo_premium)
        db.session.add(es_premium)
        db.session.add(ec_premium)
        db.session.add(ef_premium)
        db.session.commit()

        # dental plan
        dental_plan = DentalPlanFactory(carrier_id=carrier.id)
        db.session.add(dental_plan)
        db.session.commit()
        eo_premium = DentalTieredPremiumFactory(
            plan=dental_plan, tier_type=TierType.employee_only)
        es_premium = DentalTieredPremiumFactory(
            plan=dental_plan, tier_type=TierType.employee_spouse)
        ec_premium = DentalTieredPremiumFactory(
            plan=dental_plan, tier_type=TierType.employee_children)
        ef_premium = DentalTieredPremiumFactory(
            plan=dental_plan, tier_type=TierType.employee_family)
        db.session.add(eo_premium)
        db.session.add(es_premium)
        db.session.add(ec_premium)
        db.session.add(ef_premium)
        db.session.commit()
        # vision plan
        vision_plan = VisionPlanFactory(carrier_id=carrier.id)
        db.session.add(vision_plan)
        db.session.commit()
        eo_premium = VisionTieredPremiumFactory(
            plan=vision_plan, tier_type=TierType.employee_only)
        es_premium = VisionTieredPremiumFactory(
            plan=vision_plan, tier_type=TierType.employee_spouse)
        ec_premium = VisionTieredPremiumFactory(
            plan=vision_plan, tier_type=TierType.employee_children)
        ef_premium = VisionTieredPremiumFactory(
            plan=vision_plan, tier_type=TierType.employee_family)
        db.session.add(eo_premium)
        db.session.add(es_premium)
        db.session.add(ec_premium)
        db.session.add(ef_premium)
        db.session.commit()
        # supplemental life
        supp_life_plan = SupplumentalInsurancePlanFactory()
        db.session.add(supp_life_plan)
        db.session.commit()
        eo_premium = SupllementalInsuranceTieredPremiumFactory(
            plan=supp_life_plan, tier_type=TierType.employee_only)
        db.session.add(eo_premium)
        db.session.commit()
        # cancer
        cancer_plan = CancerPlanFactory()
        db.session.add(cancer_plan)
        db.session.commit()
        eo_premium = CancerTieredPremiumFactory(
            plan=cancer_plan, tier_type=TierType.employee_only)
        db.session.add(eo_premium)
        db.session.commit()
        # parking
        parking_plan = ParkingTransitPlanFactory()
        db.session.add(parking_plan)
        db.session.commit()
        eo_premium = ParkingTransitTieredPremiumFactory(
            plan=parking_plan, tier_type=TierType.employee_only)
        db.session.add(eo_premium)
        db.session.commit()
        # 401k
        employee_401k_plan = Employee401KPlanFactory()
        db.session.add(employee_401k_plan)
        db.session.commit()
        eo_premium = Employee401KTieredPremiumFactory(
            plan=employee_401k_plan, tier_type=TierType.employee_only)
        db.session.add(eo_premium)
        db.session.commit()
