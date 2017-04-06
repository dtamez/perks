#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Bulk load import of records.
"""
from datetime import date
from decimal import Decimal

import pandas

from . import db
from .models import (
    Address,
    Beneficiary,
    CancerPlan,
    Carrier,
    CriticalIllnessPlan,
    DentalPlan,
    EAPPlan,
    Employee,
    Employee401KPlan,
    FSAPlan,
    HSAPlan,
    LifeADDPlan,
    LifeADDDependentPlan,
    LongTermCarePlan,
    LTDPlan,
    Location,
    MedicalPlan,
    OtherPlan,
    ParkingTransitPlan,
    PlanTierPremium,
    Role,
    STDPlan,
    SupplumentalInsurancePlan,
    user_manager,
    User,
    VisionPlan,
)


class ValidationError(Exception):
    pass


def do_bulk_load(stream):
    xls = pandas.ExcelFile(stream)
    try:
        import_locations(xls)
        import_carriers(xls)
        import_employees(xls)
        import_beneficiaries(xls)
        import_admins(xls)
        import_medical_plans(xls)
        import_dental_plans(xls)
        import_vision_plans(xls)
        import_eap_plans(xls)
        import_ltd_plans(xls)
        import_std_plans(xls)
        import_life_add_plans(xls)
        import_life_add_dependent_plans(xls)
        import_fsa_plans(xls)
        import_parking_and_transit_plans(xls)
        import_hsa_plans(xls)
        import_employee_401k_plans(xls)
        import_supplemental_insurance_plans(xls)
        import_long_term_care_plans(xls)
        import_cancer_plans(xls)
        import_critical_illness_plans(xls)
        import_other_plans(xls)
    except:
        db.session.rollback()
    else:
        db.session.commit()


def import_locations(xls):
    loc_sheet = xls.parse('Locations', skiprows=[0])
    CODE = 1
    DESCRIPTION = 2
    EFFECTIVE_DATE = 3
    for row in loc_sheet.itertuples():
        loc = Location()
        loc.code = row[CODE]
        loc.description = row[DESCRIPTION]
        loc.effective_date = row[EFFECTIVE_DATE]
        db.session.add(loc)


def import_carriers(xls):
    NAME = 1
    PHONE = 2
    API_ENDPOINT = 3
    converters = {PHONE - 1: str}
    carrier_sheet = xls.parse('Carriers', skiprows=[0], converters=converters)
    for row in carrier_sheet.itertuples():
        carrier = Carrier()
        carrier.name = row[NAME]
        carrier.phone = row[PHONE]
        carrier.api_endpoint = row[API_ENDPOINT]
        db.session.add(carrier)


def import_employees(xls):
    EMPLOYEE_NUMBER = 1
    FIRST_NAME = 2
    MIDDLE_NAME = 3
    LAST_NAME = 4
    SSN = 5
    DOB = 6
    GENDER = 7
    MARITAL_STATUS = 8
    SMOKER_TYPE = 9
    STREET_1 = 10
    STREET_2 = 11
    CITY = 12
    STATE = 13
    ZIP = 14
    USERNAME = 15
    PASSWORD = 16
    EMAIL = 17
    ACTIVE = 18
    HIRE_DATE = 19
    EFFECTIVE_DATE = 20
    TERMINATION_DATE = 21
    GROUP_ID = 22
    SUB_GROUP_ID = 23
    SUB_GROUP_EFFECTIVE_DATE = 24
    SALARY = 25
    SALARY_MODE = 26
    SALARY_EFFECTIVE_DATE = 27
    PHONE = 28
    ALTERNATE_PHONE = 29
    EMERGENCY_CONTACT_NAME = 30
    EMERGENCY_CONTACT_RELATIONSHIP = 31
    EMERGENCY_CONTACT_PHONE = 32
    LOCATION_CODE = 33

    converters = {EMPLOYEE_NUMBER - 1: str, PASSWORD - 1: str, SSN - 1: str, PHONE - 1: str,
                  ALTERNATE_PHONE - 1: str, EMERGENCY_CONTACT_PHONE - 1: str}
    employee_sheet = xls.parse('Employees', skiprows=[0], converters=converters, keep_default_na=False)

    for row in employee_sheet.itertuples():
        employee = Employee()
        employee.employee_number = row[EMPLOYEE_NUMBER]
        employee.first_name = row[FIRST_NAME]
        employee.middle_name = row[MIDDLE_NAME]
        employee.last_name = row[LAST_NAME]
        employee.ssn = row[SSN]
        employee.dob = row[DOB]
        employee.gender = row[GENDER]
        employee.marital_status = row[MARITAL_STATUS]
        employee.smoker_type = row[SMOKER_TYPE]
        addr = Address()
        addr.street_1 = row[STREET_1]
        addr.street_2 = row[STREET_2]
        addr.city = row[CITY]
        addr.state = row[STATE]
        addr.zip_code = row[ZIP]
        employee.address = addr
        user = User()
        user.username = row[USERNAME]
        password = row[PASSWORD] or '{}{}{}'.format(employee.first_name[0], employee.last_name, employee.ssn[:-4])
        user_manager.update_password(user, user_manager.hash_password(password))
        user.email = row[EMAIL]
        user.active = bool(row[ACTIVE])
        user.confirmed_at = date.today()
        employee.user = user
        employee.hire_date = row[HIRE_DATE]
        employee.effective_date = row[EFFECTIVE_DATE]
        employee.TERMINATION_DATE = row[TERMINATION_DATE]
        employee.group_id = row[GROUP_ID]
        employee.sub_group_id = row[SUB_GROUP_ID]
        employee.sub_group_effective_date = row[SUB_GROUP_EFFECTIVE_DATE]
        employee.salary = Decimal(row[SALARY])
        employee.salary_mode = row[SALARY_MODE]
        employee.salary_effective_date = row[SALARY_EFFECTIVE_DATE]
        employee.phone = row[PHONE]
        employee.ALTERNATE_PHONE = row[ALTERNATE_PHONE]
        employee.emergency_contact_name = row[EMERGENCY_CONTACT_NAME]
        employee.emergency_contact_relationship = row[EMERGENCY_CONTACT_RELATIONSHIP]
        employee.emergency_contact_phone = row[EMERGENCY_CONTACT_PHONE]
        location = Location.query.filter(Location.code == row[LOCATION_CODE]).one()
        employee.location_id = location.id

        db.session.add(employee)


def import_beneficiaries(xls):
    EMPLOYEE_NUMBER = 1
    BENEFICIARY_TYPE = 2
    FIRST_NAME = 3
    MIDDLE_NAME = 4
    LAST_NAME = 5
    SSN = 6
    DOB = 7
    GENDER = 8
    MARITAL_STATUS = 9
    SMOKER_TYPE = 10
    SAME_ADDR_AS_EMPLOYEE = 11
    STREET_1 = 12
    STREET_2 = 13
    CITY = 14
    STATE = 15
    ZIP = 16
    converters = {EMPLOYEE_NUMBER - 1: str, SSN - 1: str, ZIP - 1: str}
    beneficiaries_sheet = xls.parse('Beneficiaries', skiprows=[0], converters=converters)

    for row in beneficiaries_sheet.itertuples():
        ben = Beneficiary()
        employee = Employee.query.filter(Employee.employee_number == row[EMPLOYEE_NUMBER]).one()
        ben.employee_id = employee.id
        ben.beneficiary_type = row[BENEFICIARY_TYPE]
        ben.first_name = row[FIRST_NAME]
        ben.middle_name = row[MIDDLE_NAME]
        ben.last_name = row[LAST_NAME]
        ben.ssn = row[SSN]
        ben.dob = row[DOB]
        ben.GENDER = row[GENDER]
        ben.marital_status = row[MARITAL_STATUS]
        ben.smoker_type = row[SMOKER_TYPE]
        if bool(row[SAME_ADDR_AS_EMPLOYEE]):
            ben.address_id = employee.address_id
        else:
            addr = Address()
            addr.street_1 = row[STREET_1]
            addr.street_2 = row[STREET_2]
            addr.city = row[CITY]
            addr.state = row[STATE]
            addr.zip_code = row[ZIP]
            ben.address = addr
        db.session.add(ben)


def import_admins(xls):
    EMPLOYEE_NUMBER = 1
    USERNAME = 2
    PASSWORD = 3
    converters = {EMPLOYEE_NUMBER - 1: str, PASSWORD - 1: str}
    admins_sheet = xls.parse('Admins', skiprows=[0], converters=converters, keep_default_na=False)

    admin_role = Role.query.filter(Role.name == 'admin').one()

    for row in admins_sheet.itertuples():
        if row[EMPLOYEE_NUMBER]:
            employee = Employee.query.filter(Employee.employee_number == row[EMPLOYEE_NUMBER]).one()
            employee.user.roles.append(admin_role)
            db.session.add(employee)
        else:
            user = User()
            user.username = row[USERNAME]
            password = user_manager.hash_password(row[PASSWORD])
            user_manager.update_password(user, password)
            db.session.add(user)


def import_medical_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    PLAN_TERMINATION_TIMING_TYPE = 7
    GROUP_NUMBER = 8
    ORIGINAL_EFFECTIVE_DATE = 9
    RENEWAL_DATE = 10
    EXISTING = 11
    LIST_BILLED = 12
    DOCTOR_SELECTION_REQUIRED = 13
    ACCOUNT_REP_NAME = 14
    COBRA_ELIGIBLE = 15
    PRE_TAX = 16
    SELF_FUNDED = 17
    CARRIER = 18

    FLAT_AMOUNT = 19
    MULTIPLIER = 20
    EMPLOYEE_ONLY = 21
    EMPLOYEE_SPOUSE = 22
    EMPLOYEE_CHILDREN = 23
    EMPLOYEE_FAMILY = 24
    EMPLOYEE_PLUS_1 = 25
    EMPLOYEE_PLUS_2 = 26
    EMPLOYEE_PLUS_3 = 27
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str, GROUP_NUMBER - 1: str}
    medical_plans_sheet = xls.parse('Medical Plans', skiprows=[0], converters=converters,
                                    keep_default_na=False)

    for row in medical_plans_sheet.itertuples():
        plan = MedicalPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.active = bool(row[ACTIVE])
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.plan_termination_timing_type_id = row[PLAN_TERMINATION_TIMING_TYPE]
        plan.group_number = row[GROUP_NUMBER]
        plan.original_effective_date = row[ORIGINAL_EFFECTIVE_DATE]
        plan.renewal_date = row[RENEWAL_DATE]
        plan.existing = bool(row[EXISTING])
        plan.list_billed = bool(row[LIST_BILLED])
        plan.doctor_selection_required = bool(row[DOCTOR_SELECTION_REQUIRED])
        plan.account_rep_name = row[ACCOUNT_REP_NAME]
        plan.cobra_eligible = bool(row[COBRA_ELIGIBLE])
        plan.pre_tax = bool(row[PRE_TAX])
        plan.self_funded = bool(row[SELF_FUNDED])
        carrier = Carrier.query.filter(Carrier.name == row[CARRIER]).one()
        plan.carrier = carrier
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        es = row[EMPLOYEE_SPOUSE]
        ec = row[EMPLOYEE_CHILDREN]
        ef = row[EMPLOYEE_FAMILY]
        ep1 = row[EMPLOYEE_PLUS_1]
        ep2 = row[EMPLOYEE_PLUS_2]
        ep3 = row[EMPLOYEE_PLUS_3]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)
        create_plan_tier_premium(es, 'ES', plan, flat_amount, multiplier)
        create_plan_tier_premium(ec, 'EC', plan, flat_amount, multiplier)
        create_plan_tier_premium(ef, 'EF', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep1, 'E1', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep2, 'E2', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep3, 'E3', plan, flat_amount, multiplier)


def create_plan_tier_premium(premium, tier_type, plan, flat_amount, multiplier):
    if premium:
        ptp = PlanTierPremium()
        ptp.plan = plan
        ptp.tier_type = tier_type
        ptp.premium = premium
        if flat_amount:
            ptp.flat_amount = flat_amount
            ptp.employer_portion = flat_amount
        elif multiplier:
            if not (0 <= multiplier <= 1):
                raise ValidationError('Multipler must be between 0.0 and 1.0 inclusive.')
            ptp.multiplier = multiplier
            ptp.employer_portion = multiplier * premium
        else:
            raise ValidationError('Must have either flat_amount or multiplier.')
        ptp.employee_portion = premium - ptp.employer_portion
        db.session.add(ptp)


def import_dental_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    PLAN_TERMINATION_TIMING_TYPE = 7
    GROUP_NUMBER = 8
    ORIGINAL_EFFECTIVE_DATE = 9
    RENEWAL_DATE = 10
    EXISTING = 11
    LIST_BILLED = 12
    DOCTOR_SELECTION_REQUIRED = 13
    ACCOUNT_REP_NAME = 14
    COBRA_ELIGIBLE = 15
    PRE_TAX = 16
    CARRIER = 17
    FLAT_AMOUNT = 18
    MULTIPLIER = 19
    EMPLOYEE_ONLY = 20
    EMPLOYEE_SPOUSE = 21
    EMPLOYEE_CHILDREN = 22
    EMPLOYEE_FAMILY = 23
    EMPLOYEE_PLUS_1 = 24
    EMPLOYEE_PLUS_2 = 25
    EMPLOYEE_PLUS_3 = 26
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str, GROUP_NUMBER - 1: str}
    dental_plans_sheet = xls.parse('Dental Plans', skiprows=[0], converters=converters, keep_default_na=False)

    for row in dental_plans_sheet.itertuples():
        plan = DentalPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.active = bool(row[ACTIVE])
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.plan_termination_timing_type_id = row[PLAN_TERMINATION_TIMING_TYPE]
        plan.group_number = row[GROUP_NUMBER]
        plan.original_effective_date = row[ORIGINAL_EFFECTIVE_DATE]
        plan.renewal_date = row[RENEWAL_DATE]
        plan.existing = bool(row[EXISTING])
        plan.list_billed = bool(row[LIST_BILLED])
        plan.doctor_selection_required = bool(row[DOCTOR_SELECTION_REQUIRED])
        plan.account_rep_name = row[ACCOUNT_REP_NAME]
        plan.cobra_eligible = bool(row[COBRA_ELIGIBLE])
        plan.pre_tax = bool(row[PRE_TAX])
        carrier = Carrier.query.filter(Carrier.name == row[CARRIER]).one()
        plan.carrier = carrier
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        es = row[EMPLOYEE_SPOUSE]
        ec = row[EMPLOYEE_CHILDREN]
        ef = row[EMPLOYEE_FAMILY]
        ep1 = row[EMPLOYEE_PLUS_1]
        ep2 = row[EMPLOYEE_PLUS_2]
        ep3 = row[EMPLOYEE_PLUS_3]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)
        create_plan_tier_premium(es, 'ES', plan, flat_amount, multiplier)
        create_plan_tier_premium(ec, 'EC', plan, flat_amount, multiplier)
        create_plan_tier_premium(ef, 'EF', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep1, 'E1', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep2, 'E2', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep3, 'E3', plan, flat_amount, multiplier)


def import_vision_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    PLAN_TERMINATION_TIMING_TYPE = 7
    GROUP_NUMBER = 8
    ORIGINAL_EFFECTIVE_DATE = 9
    RENEWAL_DATE = 10
    EXISTING = 11
    LIST_BILLED = 12
    DOCTOR_SELECTION_REQUIRED = 13
    ACCOUNT_REP_NAME = 14
    COBRA_ELIGIBLE = 15
    PRE_TAX = 16
    CARRIER = 17
    FLAT_AMOUNT = 18
    MULTIPLIER = 19
    EMPLOYEE_ONLY = 20
    EMPLOYEE_SPOUSE = 21
    EMPLOYEE_CHILDREN = 22
    EMPLOYEE_FAMILY = 23
    EMPLOYEE_PLUS_1 = 24
    EMPLOYEE_PLUS_2 = 25
    EMPLOYEE_PLUS_3 = 26

    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str, GROUP_NUMBER - 1: str}
    vision_plans_sheet = xls.parse('Vision Plans', skiprows=[0], converters=converters, keep_default_na=False)

    for row in vision_plans_sheet.itertuples():
        plan = VisionPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.active = bool(row[ACTIVE])
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.plan_termination_timing_type_id = row[PLAN_TERMINATION_TIMING_TYPE]
        plan.group_number = row[GROUP_NUMBER]
        plan.original_effective_date = row[ORIGINAL_EFFECTIVE_DATE]
        plan.renewal_date = row[RENEWAL_DATE]
        plan.existing = bool(row[EXISTING])
        plan.list_billed = bool(row[LIST_BILLED])
        plan.doctor_selection_required = bool(row[DOCTOR_SELECTION_REQUIRED])
        plan.account_rep_name = row[ACCOUNT_REP_NAME]
        plan.cobra_eligible = bool(row[COBRA_ELIGIBLE])
        plan.pre_tax = bool(row[PRE_TAX])
        carrier = Carrier.query.filter(Carrier.name == row[CARRIER]).one()
        plan.carrier = carrier
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        es = row[EMPLOYEE_SPOUSE]
        ec = row[EMPLOYEE_CHILDREN]
        ef = row[EMPLOYEE_FAMILY]
        ep1 = row[EMPLOYEE_PLUS_1]
        ep2 = row[EMPLOYEE_PLUS_2]
        ep3 = row[EMPLOYEE_PLUS_3]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)
        create_plan_tier_premium(es, 'ES', plan, flat_amount, multiplier)
        create_plan_tier_premium(ec, 'EC', plan, flat_amount, multiplier)
        create_plan_tier_premium(ef, 'EF', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep1, 'E1', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep2, 'E2', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep3, 'E3', plan, flat_amount, multiplier)


def import_eap_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11

    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    eap_plans_sheet = xls.parse('EAP Plans', skiprows=[0], converters=converters, keep_default_na=False)

    for row in eap_plans_sheet.itertuples():
        plan = EAPPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)


def import_ltd_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('LTD Plans', skiprows=[0], converters=converters, keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = LTDPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)


def import_std_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    PAYOUT_INTERVAL = 9
    MAX_WEEKLY_BENEFIT = 10
    MAX_MONTHLY_BENEFIT = 11
    BENEFFIT_PERCENTAGE = 12
    MANDATORY_IN_STATES = 13
    FLAT_AMOUNT = 14
    MULTIPLIER = 15
    EMPLOYEE_ONLY = 16
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str, MAX_WEEKLY_BENEFIT - 1: zero_if_blank,
                  MAX_MONTHLY_BENEFIT - 1: zero_if_blank, BENEFFIT_PERCENTAGE - 1: zero_if_blank}
    plans_sheet = xls.parse('STD Plans', skiprows=[0], converters=converters, keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = STDPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        plan.payout_interval = row[PAYOUT_INTERVAL]
        plan.max_weekly_benefit = Decimal(row[MAX_WEEKLY_BENEFIT])
        plan.max_monthly_benefit = Decimal(row[MAX_MONTHLY_BENEFIT])
        plan.benefit_percentage = Decimal(row[BENEFFIT_PERCENTAGE])
        plan.mandatory_in_states = row[MANDATORY_IN_STATES]
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)


def import_life_add_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('Life ADD Plans', skiprows=[0], converters=converters, keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = LifeADDPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)


def import_life_add_dependent_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_SPOUSE = 11
    EMPLOYEE_CHILDREN = 12
    EMPLOYEE_FAMILY = 13
    EMPLOYEE_PLUS_1 = 14
    EMPLOYEE_PLUS_2 = 15
    EMPLOYEE_PLUS_3 = 16
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('Life ADD Dependent Plans', skiprows=[0], converters=converters,
                            keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = LifeADDDependentPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        es = row[EMPLOYEE_SPOUSE]
        ec = row[EMPLOYEE_CHILDREN]
        ef = row[EMPLOYEE_FAMILY]
        ep1 = row[EMPLOYEE_PLUS_1]
        ep2 = row[EMPLOYEE_PLUS_2]
        ep3 = row[EMPLOYEE_PLUS_3]
        create_plan_tier_premium(es, 'ES', plan, flat_amount, multiplier)
        create_plan_tier_premium(ec, 'EC', plan, flat_amount, multiplier)
        create_plan_tier_premium(ef, 'EF', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep1, 'E1', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep2, 'E2', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep3, 'E3', plan, flat_amount, multiplier)


def import_fsa_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('FSA Plans', skiprows=[0], converters=converters, keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = FSAPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_contribution = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_contribution = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)


def import_parking_and_transit_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('Parking and Transit Plans', skiprows=[0], converters=converters,
                            keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = ParkingTransitPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)


def import_hsa_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('HSA Plans', skiprows=[0], converters=converters, keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = HSAPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)


def import_employee_401k_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('401K Plans', skiprows=[0], converters=converters, keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = Employee401KPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)


def import_supplemental_insurance_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('Supplemental Insurance Plans', skiprows=[0], converters=converters,
                            keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = SupplumentalInsurancePlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)


def import_long_term_care_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11
    EMPLOYEE_SPOUSE = 12
    EMPLOYEE_CHILDREN = 13
    EMPLOYEE_FAMILY = 14
    EMPLOYEE_PLUS_1 = 15
    EMPLOYEE_PLUS_2 = 16
    EMPLOYEE_PLUS_3 = 17
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('Long Term Care Plans', skiprows=[0], converters=converters,
                            keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = LongTermCarePlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        es = row[EMPLOYEE_SPOUSE]
        ec = row[EMPLOYEE_CHILDREN]
        ef = row[EMPLOYEE_FAMILY]
        ep1 = row[EMPLOYEE_PLUS_1]
        ep2 = row[EMPLOYEE_PLUS_2]
        ep3 = row[EMPLOYEE_PLUS_3]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)
        create_plan_tier_premium(es, 'ES', plan, flat_amount, multiplier)
        create_plan_tier_premium(ec, 'EC', plan, flat_amount, multiplier)
        create_plan_tier_premium(ef, 'EF', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep1, 'E1', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep2, 'E2', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep3, 'E3', plan, flat_amount, multiplier)


def import_cancer_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11
    EMPLOYEE_SPOUSE = 12
    EMPLOYEE_CHILDREN = 13
    EMPLOYEE_FAMILY = 14
    EMPLOYEE_PLUS_1 = 15
    EMPLOYEE_PLUS_2 = 16
    EMPLOYEE_PLUS_3 = 17

    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('Cancer Plans', skiprows=[0], converters=converters, keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = CancerPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        es = row[EMPLOYEE_SPOUSE]
        ec = row[EMPLOYEE_CHILDREN]
        ef = row[EMPLOYEE_FAMILY]
        ep1 = row[EMPLOYEE_PLUS_1]
        ep2 = row[EMPLOYEE_PLUS_2]
        ep3 = row[EMPLOYEE_PLUS_3]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)
        create_plan_tier_premium(es, 'ES', plan, flat_amount, multiplier)
        create_plan_tier_premium(ec, 'EC', plan, flat_amount, multiplier)
        create_plan_tier_premium(ef, 'EF', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep1, 'E1', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep2, 'E2', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep3, 'E3', plan, flat_amount, multiplier)


def import_critical_illness_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11
    EMPLOYEE_SPOUSE = 12
    EMPLOYEE_CHILDREN = 13
    EMPLOYEE_FAMILY = 14
    EMPLOYEE_PLUS_1 = 15
    EMPLOYEE_PLUS_2 = 16
    EMPLOYEE_PLUS_3 = 17
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('Critical Illness Plans', skiprows=[0], converters=converters,
                            keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = CriticalIllnessPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        es = row[EMPLOYEE_SPOUSE]
        ec = row[EMPLOYEE_CHILDREN]
        ef = row[EMPLOYEE_FAMILY]
        ep1 = row[EMPLOYEE_PLUS_1]
        ep2 = row[EMPLOYEE_PLUS_2]
        ep3 = row[EMPLOYEE_PLUS_3]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)
        create_plan_tier_premium(es, 'ES', plan, flat_amount, multiplier)
        create_plan_tier_premium(ec, 'EC', plan, flat_amount, multiplier)
        create_plan_tier_premium(ef, 'EF', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep1, 'E1', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep2, 'E2', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep3, 'E3', plan, flat_amount, multiplier)


def import_other_plans(xls):
    CODE = 1
    NAME = 2
    CUST_SERVICE_PHONE = 3
    WEBSITE = 4
    NOT_AVAILABLE_IN = 5
    ACTIVE = 6
    MINIMUM_BENEFIT = 7
    MAXIMUM_BENEFIT = 8
    FLAT_AMOUNT = 9
    MULTIPLIER = 10
    EMPLOYEE_ONLY = 11
    EMPLOYEE_SPOUSE = 12
    EMPLOYEE_CHILDREN = 13
    EMPLOYEE_FAMILY = 14
    EMPLOYEE_PLUS_1 = 15
    EMPLOYEE_PLUS_2 = 16
    EMPLOYEE_PLUS_3 = 17
    converters = {CODE - 1: str, CUST_SERVICE_PHONE - 1: str}
    plans_sheet = xls.parse('Other Plans', skiprows=[0], converters=converters, keep_default_na=False)

    for row in plans_sheet.itertuples():
        plan = OtherPlan()
        plan.code = row[CODE]
        plan.name = row[NAME]
        plan.cust_service_phone = row[CUST_SERVICE_PHONE]
        plan.website = row[WEBSITE]
        plan.not_available_in = row[NOT_AVAILABLE_IN]
        plan.active = bool(row[ACTIVE])
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        flat_amount = row[FLAT_AMOUNT]
        multiplier = row[MULTIPLIER]
        eo = row[EMPLOYEE_ONLY]
        es = row[EMPLOYEE_SPOUSE]
        ec = row[EMPLOYEE_CHILDREN]
        ef = row[EMPLOYEE_FAMILY]
        ep1 = row[EMPLOYEE_PLUS_1]
        ep2 = row[EMPLOYEE_PLUS_2]
        ep3 = row[EMPLOYEE_PLUS_3]
        create_plan_tier_premium(eo, 'EO', plan, flat_amount, multiplier)
        create_plan_tier_premium(es, 'ES', plan, flat_amount, multiplier)
        create_plan_tier_premium(ec, 'EC', plan, flat_amount, multiplier)
        create_plan_tier_premium(ef, 'EF', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep1, 'E1', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep2, 'E2', plan, flat_amount, multiplier)
        create_plan_tier_premium(ep3, 'E3', plan, flat_amount, multiplier)


def zero_if_blank(val):
    if val == '':
        return 0
    else:
        return val
