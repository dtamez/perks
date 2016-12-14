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

from .. import app, db_session
from ..models import TierType, User
from .model_factory import (
    BeneficiaryFactory,
    CancerPlanFactory,
    CancerPlanTierPremiumFactory,
    CarrierFactory,
    DentalPlanFactory,
    DentalPlanTierPremiumFactory,
    DependentFactory,
    Employee401KPlanFactory,
    Employee401KPlanTierPremiumFactory,
    EmployeeFactory,
    MedicalPlanFactory,
    MedicalPlanTierPremiumFactory,
    ParkingTransitPlanFactory,
    ParkingTransitPlanTierPremiumFactory,
    SupplumentalInsurancePlanFactory,
    SupllementalInsurancePlanTierPremiumFactory,
    VisionPlanFactory,
    VisionPlanTierPremiumFactory,
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
        db_session.add(emp)
        db_session.commit()

        # carriers
        carrier = CarrierFactory()
        db_session.add(carrier)
        db_session.commit()

        # medical plan 1
        med_plan = MedicalPlanFactory(carrier_id=carrier.id)
        db_session.add(med_plan)
        db_session.commit()
        ptp_eo = MedicalPlanTierPremiumFactory(
            plan=med_plan, tier_type=TierType.employee_only)
        ptp_es = MedicalPlanTierPremiumFactory(
            plan=med_plan, tier_type=TierType.employee_spouse)
        ptp_ec = MedicalPlanTierPremiumFactory(
            plan=med_plan, tier_type=TierType.employee_children)
        ptp_ef = MedicalPlanTierPremiumFactory(
            plan=med_plan, tier_type=TierType.employee_family)
        db_session.add(ptp_eo)
        db_session.add(ptp_es)
        db_session.add(ptp_ec)
        db_session.add(ptp_ef)
        db_session.commit()

        # medical plan 2
        med_plan_2 = MedicalPlanFactory(carrier_id=carrier.id)
        db_session.add(med_plan)
        db_session.commit()
        ptp_eo = MedicalPlanTierPremiumFactory(
            plan=med_plan_2, tier_type=TierType.employee_only)
        ptp_es = MedicalPlanTierPremiumFactory(
            plan=med_plan_2, tier_type=TierType.employee_spouse)
        ptp_ec = MedicalPlanTierPremiumFactory(
            plan=med_plan_2, tier_type=TierType.employee_children)
        ptp_ef = MedicalPlanTierPremiumFactory(
            plan=med_plan_2, tier_type=TierType.employee_family)
        db_session.add(ptp_eo)
        db_session.add(ptp_es)
        db_session.add(ptp_ec)
        db_session.add(ptp_ef)
        db_session.commit()

        # dental plan
        dental_plan = DentalPlanFactory(carrier_id=carrier.id)
        db_session.add(dental_plan)
        db_session.commit()
        ptp_eo = DentalPlanTierPremiumFactory(
            plan=dental_plan, tier_type=TierType.employee_only)
        ptp_es = DentalPlanTierPremiumFactory(
            plan=dental_plan, tier_type=TierType.employee_spouse)
        ptp_ec = DentalPlanTierPremiumFactory(
            plan=dental_plan, tier_type=TierType.employee_children)
        ptp_ef = DentalPlanTierPremiumFactory(
            plan=dental_plan, tier_type=TierType.employee_family)
        db_session.add(ptp_eo)
        db_session.add(ptp_es)
        db_session.add(ptp_ec)
        db_session.add(ptp_ef)
        db_session.commit()
        # vision plan
        vision_plan = VisionPlanFactory(carrier_id=carrier.id)
        db_session.add(vision_plan)
        db_session.commit()
        ptp_eo = VisionPlanTierPremiumFactory(
            plan=vision_plan, tier_type=TierType.employee_only)
        ptp_es = VisionPlanTierPremiumFactory(
            plan=vision_plan, tier_type=TierType.employee_spouse)
        ptp_ec = VisionPlanTierPremiumFactory(
            plan=vision_plan, tier_type=TierType.employee_children)
        ptp_ef = VisionPlanTierPremiumFactory(
            plan=vision_plan, tier_type=TierType.employee_family)
        db_session.add(ptp_eo)
        db_session.add(ptp_es)
        db_session.add(ptp_ec)
        db_session.add(ptp_ef)
        db_session.commit()
        # supplemental life
        supp_life_plan = SupplumentalInsurancePlanFactory()
        db_session.add(supp_life_plan)
        db_session.commit()
        ptp_eo = SupllementalInsurancePlanTierPremiumFactory(
            plan=supp_life_plan, tier_type=TierType.employee_only)
        db_session.add(ptp_eo)
        db_session.commit()
        # cancer
        cancer_plan = CancerPlanFactory()
        db_session.add(cancer_plan)
        db_session.commit()
        ptp_eo = CancerPlanTierPremiumFactory(
            plan=cancer_plan, tier_type=TierType.employee_only)
        db_session.add(ptp_eo)
        db_session.commit()
        # parking
        parking_plan = ParkingTransitPlanFactory()
        db_session.add(parking_plan)
        db_session.commit()
        ptp_eo = ParkingTransitPlanTierPremiumFactory(
            plan=parking_plan, tier_type=TierType.employee_only)
        db_session.add(ptp_eo)
        db_session.commit()
        # 401k
        employee_401k_plan = Employee401KPlanFactory()
        db_session.add(employee_401k_plan)
        db_session.commit()
        ptp_eo = Employee401KPlanTierPremiumFactory(
            plan=employee_401k_plan, tier_type=TierType.employee_only)
        db_session.add(ptp_eo)
        db_session.commit()
