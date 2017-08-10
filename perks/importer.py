#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
"""
Bulk load import of records.
"""
from datetime import date
from decimal import Decimal

from flask import flash
import pandas

from . import db, models
from .models import (
    # AccidentPlan,
    Address,
    AgeBandedTier,
    AgeBasedReduction,
    BasicLifePlan,
    Beneficiary,
    # CancerPlan,
    Carrier,
    ChildVoluntaryLifePlan,
    CriticalIllnessPlan,
    DentalPlan,
    DentalVisionBundlePlan,
    Dependent,
    EAPPlan,
    Election,
    Employee,
    Employee401KPlan,
    Enrollment,
    EnrollmentPeriod,
    FSADependentCarePlan,
    FSAMedicalPlan,
    # HospitalConfinementPlan,
    # HRAPlan,
    HSAPlan,
    # IdentityTheftPlan,
    LTDPlan,
    LTDVoluntaryPlan,
    Location,
    LongTermCarePlan,
    MedicalDentalBundlePlan,
    MedicalDentalVisionBundlePlan,
    MedicalPlan,
    MedicalVisionBundlePlan,
    # ParkingTransitPlan,
    Plan,
    Premium,
    Role,
    SpouseVoluntaryLifePlan,
    STDPlan,
    STDVoluntaryPlan,
    StandaloneADDPlan,
    UniversalLifePlan,
    User,
    VisionPlan,
    VoluntaryLifePlan,
    WholeLifePlan,
    user_manager,
)
from .util.orm import get_or_create


class ValidationError(Exception):
    pass


gender_keys = [k for k, v in models.GENDER_TYPES]
smoker_keys = [k for k, v in models.SMOKER_TYPES]
family_tier_keys = [k for k, v in models.FAMILY_TIER_TYPES]


def do_bulk_load(stream):
    xls = pandas.ExcelFile(stream)
    try:
        import_locations(xls)
        import_carriers(xls)
        import_employees(xls)
        import_admins(xls)
        import_dependents(xls)
        import_beneficiaries(xls)
        import_core_plans(xls, 'Medical Plans', MedicalPlan)
        import_core_plans(xls, 'Dental Plans', DentalPlan)
        import_core_plans(xls, 'Vision Plans', VisionPlan)
        import_core_plans(xls, 'Medical with Dental Bundle Plans', MedicalDentalBundlePlan)
        import_core_plans(xls, 'Medical with Vision Bundle Plans', MedicalVisionBundlePlan)
        import_core_plans(xls, 'Medical with Dental and Vision Bundle Plans', MedicalDentalVisionBundlePlan)
        import_core_plans(xls, 'Dental with Vision Bundle Plans', DentalVisionBundlePlan)
        import_basic_life_plans(xls)
        import_voluntary_life_plans(xls, 'Employee Voluntary Life Plans', VoluntaryLifePlan)
        import_voluntary_life_plans(xls, 'Spouse Voluntary Life Plans', SpouseVoluntaryLifePlan, spouse=True)
        import_voluntary_life_plans(xls, 'Child Voluntary Life Plans', ChildVoluntaryLifePlan)
        import_standalone_add_plans(xls)
        # import_whole_life_plans(xls)
        # import_universal_life_plans(xls)
        import_ltd_plans(xls, 'LTD Plans', LTDPlan)
        import_ltd_plans(xls, 'Voluntary LTD Plans', LTDVoluntaryPlan)
        import_std_plans(xls, 'STD Plans', STDPlan)
        import_std_plans(xls, 'Voluntary STD Plans', STDVoluntaryPlan)
        import_fsa_plan(xls, 'FSA Medical Spending Plan', FSAMedicalPlan)
        import_fsa_plan(xls, 'FSA Dependent Care Spending Plan', FSADependentCarePlan)
        import_hsa_plan(xls, 'HSA Plan', HSAPlan)
        # import_hsa_plan(xls, 'HRA Plan', HRAPlan)
        # import_employee_401k_plans(xls)
        # import_eap_plans(xls)
        import_supplemental_plans(xls, 'Long Term Care Plans', LongTermCarePlan)
        import_supplemental_plans(xls, 'Critical Illness Plans', CriticalIllnessPlan)
        # import_supplemental_plans(xls, 'Cancer Plans', CancerPlan)
        # import_supplemental_plans(xls, 'Accident Plans', AccidentPlan)
        # import_supplemental_plans(xls, 'Hospital Confinement Plans', HospitalConfinementPlan)
        # import_supplemental_plans(xls, 'Parking and Transit Plans', ParkingTransitPlan)
        # import_supplemental_plans(xls, 'Identity Theft Plans', IdentityTheftPlan)
        # import_enrollments(xls)
        db.session.commit()
    except Exception as e:
        flash(e)
        db.session.rollback()


def make_bool(s):
    return s.lower() in ['yes', 'true']


def import_locations(xls):
    print 'importing locations'
    loc_sheet = xls.parse('Locations')
    CODE, DESCRIPTION, EFFECTIVE_DATE = range(1, 4)
    for row in loc_sheet.itertuples():
        loc = Location()
        loc.code = row[CODE]
        loc.description = row[DESCRIPTION]
        loc.effective_date = row[EFFECTIVE_DATE]
        db.session.add(loc)
        print loc


def import_carriers(xls):
    print 'importing carriers'
    NAME, PHONE, API_ENDPOINT = range(1, 4)
    converters = {PHONE - 1: str}
    carrier_sheet = xls.parse('Carriers', converters=converters)
    for row in carrier_sheet.itertuples():
        carrier = Carrier()
        carrier.name = row[NAME]
        carrier.phone = row[PHONE]
        carrier.api_endpoint = row[API_ENDPOINT]
        db.session.add(carrier)
        print carrier.name


def import_employees(xls):
    print 'importing employees'
    (EMPLOYEE_NUMBER, LOCATION_CODE,
     FIRST_NAME, MIDDLE_NAME, LAST_NAME,
     SSN, DOB, GENDER, MARITAL_STATUS, SPOUSE_DOB, SMOKER_TYPE, SPOUSE_SMOKER_TYPE,
     STREET_1, STREET_2, CITY, STATE, ZIP,
     USERNAME, PASSWORD, EMAIL, ACTIVE,
     HIRE_DATE, EFFECTIVE_DATE, TERMINATION_DATE,
     GROUP_ID, SUB_GROUP_ID, SUB_GROUP_EFFECTIVE_DATE,
     SALARY, SALARY_MODE, SALARY_EFFECTIVE_DATE,
     PHONE, ALTERNATE_PHONE,
     EMERGENCY_CONTACT_NAME, EMERGENCY_CONTACT_RELATIONSHIP, EMERGENCY_CONTACT_PHONE) = range(1, 36)
    converters = {n: strip for n in range(LOCATION_CODE)}

    converters.update({EMPLOYEE_NUMBER - 1: str, PASSWORD - 1: str, SSN - 1: str, PHONE - 1: str,
                       ALTERNATE_PHONE - 1: str, EMERGENCY_CONTACT_PHONE - 1: str})
    employee_sheet = xls.parse('Employees', converters=converters, keep_default_na=False)

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
        employee.spouse_dob = row[SPOUSE_DOB]
        employee.smoker_type = row[SMOKER_TYPE]
        employee.spouse_smoker_type = row[SPOUSE_SMOKER_TYPE]
        addr = Address()
        addr.street_1 = row[STREET_1]
        addr.street_2 = row[STREET_2]
        addr.city = row[CITY]
        addr.state = row[STATE]
        addr.zip_code = row[ZIP]
        employee.address = addr
        user = User()
        user.username = row[USERNAME]
        password = row[PASSWORD] or '{}{}{}'.format(employee.first_name[0], employee.last_name, employee.ssn[-4:])
        user_manager.update_password(user, user_manager.hash_password(password))
        user.email = row[EMAIL]
        user.active = row[ACTIVE]
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
        print employee.first_name, employee.last_name


def import_admins(xls):
    print 'importing admins'
    EMPLOYEE_NUMBER, USERNAME, PASSWORD = range(1, 4)
    converters = {n: strip for n in range(PASSWORD)}
    converters.update({EMPLOYEE_NUMBER - 1: str, PASSWORD - 1: str})
    admins_sheet = xls.parse('Admins', converters=converters, keep_default_na=False)

    admin_role = Role.query.filter(Role.name == 'admin').one()

    for row in admins_sheet.itertuples():
        if row[EMPLOYEE_NUMBER]:
            employee = Employee.query.filter(Employee.employee_number == row[EMPLOYEE_NUMBER]).one()
            employee.user.roles.append(admin_role)
            db.session.add(employee)
            print 'employee', employee.first_name, employee.last_name
        else:
            user = User()
            user.username = row[USERNAME]
            password = user_manager.hash_password(row[PASSWORD])
            user_manager.update_password(user, password)
            db.session.add(user)
            print 'user', user.username


def import_dependents(xls):
    print 'importing dependents'
    (EMPLOYEE_NUMBER, DEPENDENT_TYPE,
     FIRST_NAME, MIDDLE_NAME, LAST_NAME,
     SSN, DOB, GENDER, MARITAL_STATUS, SMOKER_TYPE,
     FULL_TIME_STUDENT, IS_DISABLED, DISABILITY_DATE,
     SAME_ADDR_AS_EMPLOYEE, STREET_1, STREET_2, CITY, STATE, ZIP) = range(1, 20)
    converters = {n: strip for n in range(ZIP)}
    converters.update({EMPLOYEE_NUMBER - 1: str, SSN - 1: str, ZIP - 1: str})
    sheet = xls.parse('Dependents', converters=converters)

    for row in sheet.itertuples():
        dep = Dependent()
        employee = Employee.query.filter(Employee.employee_number == row[EMPLOYEE_NUMBER]).one()
        dep.employee_id = employee.id
        dep.dependent_type = row[DEPENDENT_TYPE]
        dep.first_name = row[FIRST_NAME]
        dep.middle_name = row[MIDDLE_NAME]
        dep.last_name = row[LAST_NAME]
        dep.ssn = row[SSN]
        dep.dob = row[DOB]
        dep.GENDER = row[GENDER]
        dep.marital_status = row[MARITAL_STATUS]
        dep.smoker_type = row[SMOKER_TYPE]
        dep.full_time_student = row[FULL_TIME_STUDENT]
        if make_bool(row[SAME_ADDR_AS_EMPLOYEE]):
            dep.address_id = employee.address_id
        else:
            addr = Address()
            addr.street_1 = row[STREET_1]
            addr.street_2 = row[STREET_2]
            addr.city = row[CITY]
            addr.state = row[STATE]
            addr.zip_code = row[ZIP]
            dep.address = addr
        db.session.add(dep)
        print dep.first_name, dep.last_name


def import_beneficiaries(xls):
    print 'importing beneficiaries'
    (EMPLOYEE_NUMBER, BENEFICIARY_TYPE,
     FIRST_NAME, MIDDLE_NAME, LAST_NAME,
     SSN, DOB, GENDER, MARITAL_STATUS, SMOKER_TYPE,
     SAME_ADDR_AS_EMPLOYEE, STREET_1, STREET_2, CITY, STATE, ZIP) = range(1, 17)
    converters = {n: strip for n in range(ZIP)}
    converters.update({EMPLOYEE_NUMBER - 1: str, SSN - 1: str, ZIP - 1: str})
    beneficiaries_sheet = xls.parse('Beneficiaries', converters=converters)

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
        if make_bool(row[SAME_ADDR_AS_EMPLOYEE]):
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
        print ben.first_name, ben.last_name


def import_core_plans(xls, sheet_name, klass):
    print 'importing {} plans'.format(klass.__name__)
    (GROUP_NUMBER, ORIGINAL_EFFECTIVE_DATE, RENEWAL_DATE,
     LIST_BILLED, DOCTOR_SELECTION_REQUIRED, COBRA_ELIGIBLE,
     PRE_TAX, PLAN_TERMINATION_TIMING_TYPE) = range(10, 18)
    converters = {n: strip for n in range(PLAN_TERMINATION_TIMING_TYPE)}
    converters.update({0: str, 3: str, GROUP_NUMBER - 1: str})
    sheet = xls.parse(sheet_name, converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = klass()
        get_common(row, plan)
        get_premium_related(row, plan)

        plan.group_number = row[GROUP_NUMBER]
        plan.original_effective_date = row[ORIGINAL_EFFECTIVE_DATE]
        plan.renewal_date = row[RENEWAL_DATE]
        plan.list_billed = make_bool(row[LIST_BILLED])
        plan.doctor_selection_required = make_bool(row[DOCTOR_SELECTION_REQUIRED])
        plan.cobra_eligible = make_bool(row[COBRA_ELIGIBLE])
        plan.pre_tax = make_bool(row[PRE_TAX])
        plan.plan_termination_timing_type_id = row[PLAN_TERMINATION_TIMING_TYPE]
        db.session.add(plan)
        print plan.name


def get_common(row, plan):
    CODE, NAME, CARRIER, CUST_SERVICE_PHONE, WEBSITE, ACTIVE = range(1, 7)
    plan.code = row[CODE]
    plan.name = row[NAME]
    carrier = Carrier.query.filter(Carrier.name == row[CARRIER]).one()
    plan.carrier = carrier
    plan.cust_service_phone = row[CUST_SERVICE_PHONE]
    plan.website = row[WEBSITE]
    plan.active = make_bool(row[ACTIVE])


def get_premium_related(row, plan):
    FLAT_AMOUNT, PERCENTAGE, PREMIUM_MATRIX = range(7, 10)
    if row[FLAT_AMOUNT]:
        plan.er_flat_amount_contributed = row[FLAT_AMOUNT]
    elif row[PERCENTAGE]:
        plan.er_percentage_contributed = Decimal(row[PERCENTAGE]) / 100
    pr_matrix = row[PREMIUM_MATRIX]
    if pr_matrix:
        create_plan_premiums(plan, pr_matrix)


def import_basic_life_plans(xls):
    print 'importing basic life plan'
    (MINIMUM_BENEFIT, MAXIMUM_BENEFIT,
     MULTIPLE_OF_SALARY_PAID, SPOUSE_BENEFIT_AMOUNT, CHILD_BENEFIT_AMOUNT, GUARANTEE_ISSUE,
     BENEFIT_REDUCTIONS_BY_AGE, ADDL_SALARY_MULTIPLES_ACCIDENTAL_DEATH,
     ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT) = range(10, 19)
    converters = {n: strip for n in range(ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT)}
    converters.update({0: str, 3: str})
    sheet = xls.parse('Basic Life Plans', converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = BasicLifePlan()
        get_common(row, plan)
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        plan.multiple_of_salary_paid = Decimal(row[MULTIPLE_OF_SALARY_PAID])
        plan.spouse_benefit = Decimal(row[SPOUSE_BENEFIT_AMOUNT])
        plan.child_benefit = Decimal(row[CHILD_BENEFIT_AMOUNT])
        plan.guarantee_issue = Decimal(row[GUARANTEE_ISSUE])
        create_age_based_reductions(plan, row[BENEFIT_REDUCTIONS_BY_AGE])
        plan.addl_salary_multiple_accidental_death = Decimal(row[ADDL_SALARY_MULTIPLES_ACCIDENTAL_DEATH])
        plan.addl_salary_multiple_accidental_dismemberment = Decimal(
            row[ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT])
        db.session.add(plan)
        get_premium_related(row, plan)
        print plan.name


def import_voluntary_life_plans(xls, sheet_name, klass, spouse=False):
    print 'importing {} plans'.format(klass.__name__)
    if spouse:
        (USE_EMPLOYEE_AGE_FOR_SPOUSE,
         INCREMENTS, MINIMUM_ELECTION, MAXIMUM_ELECTION, GUARANTEE_ISSUE,
         ADDL_SALARY_MULTIPLES_ACCIDENTAL_DEATH, ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT) = range(10, 17)
    else:
        (INCREMENTS, MINIMUM_ELECTION, MAXIMUM_ELECTION, GUARANTEE_ISSUE,
         ADDL_SALARY_MULTIPLES_ACCIDENTAL_DEATH, ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT) = range(10, 16)
    converters = {n: strip for n in range(ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT)}
    converters.update({0: str, 3: str})
    sheet = xls.parse(sheet_name, converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = klass()
        get_common(row, plan)
        if spouse:
            plan.use_employee_age_for_spouse = make_bool(row[USE_EMPLOYEE_AGE_FOR_SPOUSE])
        plan.increments = int(row[INCREMENTS])
        plan.min_election = Decimal(row[MINIMUM_ELECTION])
        plan.max_election = Decimal(row[MAXIMUM_ELECTION])
        plan.guarantee_issue = Decimal(row[GUARANTEE_ISSUE])
        if row[ADDL_SALARY_MULTIPLES_ACCIDENTAL_DEATH]:
            plan.addl_salary_multiple_accidental_death = Decimal(row[ADDL_SALARY_MULTIPLES_ACCIDENTAL_DEATH])
        if row[ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT]:
            plan.addl_salary_multiple_accidental_dismemberment = Decimal(
                row[ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT])
        db.session.add(plan)
        get_premium_related(row, plan)
        print plan.name


def import_standalone_add_plans(xls):
    print 'importing Standalone ADD plans'
    (
     MINIMUM_BENEFIT, MAXIMUM_BENEFIT,
     SALARY_MULTIPLES_ACCIDENTAL_DEATH, SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT) = range(10, 14)
    converters = {n: strip for n in range(SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT)}
    converters.update({0: str, 3: str})
    sheet = xls.parse('Standalone ADD Plans', converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = StandaloneADDPlan()
        get_common(row, plan)
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        plan.salary_multiple_accidental_death = Decimal(row[SALARY_MULTIPLES_ACCIDENTAL_DEATH])
        plan.salary_multiple_accidental_dismemberment = Decimal(row[SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT])
        db.session.add(plan)
        get_premium_related(row, plan)
        print plan.name


def import_whole_life_plans(xls):
    print 'importing whole life plans'
    (MINIMUM_BENEFIT, MAXIMUM_BENEFIT,
     MULTIPLE_OF_SALARY_PAID, SPOUSE_BENEFIT_AMOUNT, CHILD_BENEFIT_AMOUNT,
     BENEFIT_REDUCTIONS_BY_AGE, ADDL_SALARY_MULTIPLES_ACCIDENTAL_DEATH,
     ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT) = range(10, 18)
    converters = {n: strip for n in range(ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT)}
    converters.update({0: str, 3: str})
    sheet = xls.parse('Whole Life Plans', converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = WholeLifePlan()
        get_common(row, plan)
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        plan.max_multiple_of_salary_paid = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        get_premium_related(row, plan)
        print plan.name


def import_universal_life_plans(xls):
    print 'importing Universal Life plans'
    (MINIMUM_BENEFIT, MAXIMUM_BENEFIT,
     MULTIPLE_OF_SALARY_PAID, SPOUSE_BENEFIT_AMOUNT, CHILD_BENEFIT_AMOUNT,
     BENEFIT_REDUCTIONS_BY_AGE, ADDL_SALARY_MULTIPLES_ACCIDENTAL_DEATH,
     ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT) = range(10, 18)
    converters = {n: strip for n in range(ADDL_SALARY_MULTIPLES_ACCIDENTAL_DISMEMBERMENT)}
    converters.update({0: str, 3: str})
    sheet = xls.parse('Universal Life Plans', converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = UniversalLifePlan()
        get_common(row, plan)
        plan.minimum_benefit = Decimal(row[MINIMUM_BENEFIT])
        plan.maximum_benefit = Decimal(row[MAXIMUM_BENEFIT])
        plan.max_multiple_of_salary_paid = Decimal(row[MAXIMUM_BENEFIT])
        db.session.add(plan)
        get_premium_related(row, plan)
        print plan.name


def get_age_bands_from_matrix(s):
    s = s.replace(' ', '')
    if '-' in s:
        vals = s.split('-')
        if len(vals) == 2 and vals[0].strip().isdigit() and vals[1].strip().isdigit():
            return int(vals[0].strip()), int(vals[1].strip())
    elif '+' in s:
        vals = s.split('+')
        if len(vals) == 2 and vals[0].strip().isdigit():
            return int(vals[0].strip()), None

    return None


def create_plan_premiums(plan, pr_matrix):  # NOQA
    pr_matrix = pr_matrix.replace(' ', '')
    matrix = pr_matrix.split('\n')
    for idx, line in enumerate(matrix):
        matrix[idx] = line.split(',')
    # Gender, Age, Age bands, Smoker, Family Tier, rate%, $amount
    for line in matrix:
        premium = Premium(plan=plan)
        print 'creating {} dimensional premium'.format(len(line))
        for dimension in line:
            age_bands = get_age_bands_from_matrix(dimension)
            print 'age_bands: ', age_bands
            if dimension in gender_keys:
                premium.gender = dimension
            elif dimension in smoker_keys:
                premium.smoker_status = dimension
            elif dimension in family_tier_keys:
                premium.family_tier = dimension
            elif dimension.isdigit():
                premium.age = int(dimension)
            elif age_bands:
                tier = get_or_create(db.session, AgeBandedTier, plan=plan, low=age_bands[0], high=age_bands[1])
                premium.age_banded_tier = tier
            elif dimension.startswith('$'):
                premium.amount = Decimal(dimension[1:])
            elif dimension.endswith('%'):
                premium.rate = Decimal(dimension[:-1]) / 100
            else:
                raise Exception("Invalid premium matrix dimension value: .".format(dimension))
        db.session.add(premium)


def create_age_based_reductions(plan, data):
    lines = data.split('\n')
    for idx, line in enumerate(lines):
        lines[idx] = line.split(',')

    for line in lines:
        abr = AgeBasedReduction(plan=plan, age=line[0], percentage=Decimal(line[1]))
        db.session.add(abr)


def import_ltd_plans(xls, sheet_name, klass):
    print 'importing {} plans'.format(klass.__name__)
    SALARY_PERCENTAGE, MAX_MONTHLY_BENEFIT = range(10, 12)
    converters = {n: strip for n in range(MAX_MONTHLY_BENEFIT)}
    converters.update({0: str, 3: str})
    sheet = xls.parse(sheet_name, converters=converters, keep_default_na=False)
    for row in sheet.itertuples():
        plan = klass()
        get_common(row, plan)
        plan.percentage_of_salary_paid = Decimal(row[SALARY_PERCENTAGE]) / 100
        plan.max_monthly_benefit = Decimal(row[MAX_MONTHLY_BENEFIT])
        db.session.add(plan)
        get_premium_related(row, plan)
        print plan.name


def import_std_plans(xls, sheet_name, klass):
    print 'importing {} plans'.format(klass.__name__)
    SALARY_PERCENTAGE, MAX_WEEKLY_BENEFIT = range(10, 12)
    converters = {n: strip for n in range(MAX_WEEKLY_BENEFIT)}
    converters.update({0: str, 3: str})
    sheet = xls.parse(sheet_name, converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = klass()
        get_common(row, plan)
        plan.max_weekly_benefit = Decimal(row[MAX_WEEKLY_BENEFIT])
        plan.percentage_of_salary_paid = Decimal(row[SALARY_PERCENTAGE]) / 100
        db.session.add(plan)
        get_premium_related(row, plan)
        print plan.name


def import_fsa_plan(xls, sheet_name, klass):
    print 'importing {} plans'.format(klass.__name__)
    MIN_CONTRIBUTION = 10
    converters = {n: strip for n in range(MIN_CONTRIBUTION)}
    converters.update({0: str, 3: str})
    sheet = xls.parse(sheet_name, converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = klass()
        get_common(row, plan)
        db.session.add(plan)
        get_premium_related(row, plan)
        plan.min_contribution = Decimal(row[MIN_CONTRIBUTION])
        print plan.name


def import_hsa_plan(xls, sheet_name, klass):
    print 'importing {} plans'.format(klass.__name__)
    MIN_CONTRIBUTION = 10
    converters = {n: strip for n in range(MIN_CONTRIBUTION)}
    converters.update({0: str, 3: str})
    sheet = xls.parse(sheet_name, converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = klass()
        get_common(row, plan)
        db.session.add(plan)
        get_premium_related(row, plan)
        plan.min_contribution = Decimal(row[MIN_CONTRIBUTION])
        print plan.name


def import_employee_401k_plans(xls):
    print 'importing 401k plans'
    EMPLOYER_PERCENT_MATCH, EMPLOYER_MAX_CONTRIB, MIN_CONTRIBUTION = range(10, 13)
    converters = {n: strip for n in range(MIN_CONTRIBUTION)}
    converters.update({0: str, 3: str})
    sheet = xls.parse('401K Plans', converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = Employee401KPlan()
        get_common(row, plan)
        db.session.add(plan)
        get_premium_related(row, plan)
        plan.employer_percent_matched = int(row[EMPLOYER_PERCENT_MATCH]) / 100
        plan.min_contribution = Decimal(row[EMPLOYER_MAX_CONTRIB])
        plan.min_contribution = Decimal(row[MIN_CONTRIBUTION])
        print plan.name


def import_eap_plans(xls):
    print 'importing eap plans'
    converters = {n: strip for n in range(9)}
    converters.update({0: str, 3: str})
    sheet = xls.parse('EAP Plans', converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = EAPPlan()
        get_common(row, plan)
        db.session.add(plan)
        get_premium_related(row, plan)
        print plan.name


def import_supplemental_plans(xls, sheet_name, klass):
    print 'importing {} plans'.format(klass.__name__)
    converters = {n: strip for n in range(9)}
    converters.update({0: str, 3: str})
    sheet = xls.parse(sheet_name, converters=converters, keep_default_na=False)

    for row in sheet.itertuples():
        plan = klass()
        get_common(row, plan)
        db.session.add(plan)
        get_premium_related(row, plan)
        print plan.name

enrollment_cache = {}


def get_enrollment(year, employee_number):
    key = '{}-{}'.format(year, employee_number)
    enr = enrollment_cache.get(key, None)
    if enr:
        return enr
    emp = Employee.query.filter_by(employee_number=employee_number).one()
    period = EnrollmentPeriod.query.filter(EnrollmentPeriod.year == year).one_or_none()
    if not period:
        period = EnrollmentPeriod(year=year)
        db.session.add(period)
        enr = Enrollment()
        enr.enrollment_period = period
        enr.employee = emp
        enr.enrollment_period = period
        db.session.add(enr)
        enrollment_cache[key] = enr
        return enr
    enr = Enrollment.query.filter_by(enrollment_period=period, employee=emp).one_or_none()
    if not enr:
        enr = Enrollment(enrollment_period=period, employee=emp)
        db.session.add(enr)
        enrollment_cache[key] = enr
        return enr


def create_tiered_election(code, premium, amount):
    election = Election()
    plan = Plan.query.filter_by(code=code).one()
    election.plan = plan
    election.premium = premium
    if amount:
        election.amount = int(amount)
    return election


# def import_enrollments(xls):
#    print 'importing enrollments'
#    (ENROLLMENT_YEAR, EMPLOYEE_NUMBER, PLAN_CODE, EMPLOYEE_ONLY, EMPLOYEE_SPOUSE, EMPLOYEE_CHILDREN,
#     EMPLOYEE_FAMILY, EMPLOYEE_PLUS_1, EMPLOYEE_PLUS_2, EMPLOYEE_PLUS_3, BENEFIT_AMOUNT,
#     BENEFICIARY_SSN) = range(1, 13)
#
#    converters = {n: strip for n in range(EMPLOYEE_ONLY)}
#    converters.update({EMPLOYEE_NUMBER - 1: str, BENEFICIARY_SSN - 1: str})
#    enrollments_sheet = xls.parse('Enrollments', converters=converters, keep_default_na=False)
#
#    for row in enrollments_sheet.itertuples():
#        print row
#        enr = get_enrollment(row[ENROLLMENT_YEAR], row[EMPLOYEE_NUMBER])
#        tiered_premium = get_tiered_premium(row[PLAN_CODE], row[EMPLOYEE_ONLY], row[EMPLOYEE_SPOUSE],
#        row[EMPLOYEE_CHILDREN],
#                                   row[EMPLOYEE_FAMILY], row[EMPLOYEE_PLUS_1], row[EMPLOYEE_PLUS_2],
#                                   row[EMPLOYEE_PLUS_3])
#        election = create_tiered_election(row[PLAN_CODE], tiered_premium, row[BENEFIT_AMOUNT])
#        enr.elections.append(election)
#        db.session.add(enr)


def strip(txt):
    try:
        return txt.strip()
    except AttributeError:
        return txt


def zero_if_blank(val):
    if val == '':
        return 0
    else:
        return val
