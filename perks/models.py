# -*- coding: utf-8 -*-
# vie:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from flask_user import SQLAlchemyAdapter, UserManager, UserMixin
import inflection
from sqlalchemy.orm import backref
from sqlalchemy_utils import (
    ChoiceType,
    EmailType,
    PhoneNumberType,
    ScalarListType,
    URLType,
)
from sqlalchemy.ext.declarative import (
    as_declarative,
    declared_attr,
)
from wtforms import widgets

from . import app, db


@as_declarative()
class Base(object):
    """Base class for all models to create a default table name based on the
    class name and an id field.
    """

    @declared_attr
    def __tablename__(cls):
        return inflection.underscore(cls.__name__)

    id = db.Column(db.Integer(), primary_key=True, info={'widget': widgets.HiddenInput()})

Base.query = db.session.query_property()


# CHOICES
GENDER_TYPES = [
    ('M', 'Male'),
    ('F', 'Female'),
]


MARITAL_STATUSES = [
    ('S', 'Single'),
    ('M', 'Married'),
    ('D', 'Divorced'),
    ('W', 'Widowed'),
]


SMOKER_TYPES = [
    ('N', 'Neither Employee nor Spouse'),
    ('B', 'Both Employee and Spouse'),
    ('P', 'Spouse Only'),
    ('S', 'Employee Only'),
]


BENEFICIARY_TYPES = [
    ('P', 'PRIMARY'),
    ('C', 'CONTINGENT'),
]

DEPENDENT_TYPES = [
    ('H', 'Husband'),
    ('W', 'Wife'),
    ('S', 'Son'),
    ('D', 'Daughter'),
    ('I', 'Incapacitated'),
]

SALARY_MODE_TYPES = [
    ('H', 'Hourly'),
    ('W', 'Weekly'),
    ('B', 'Bi-weekly'),
    ('S', 'Semi-monthly'),
    ('M', 'Monthly'),
    ('A', 'Annual'),
]


PLAN_TYPES = [
    ('hmo', 'HMO'),
    ('ppo', 'PPO'),
    ('pos', 'POS'),
    ('ind', 'Indemnity'),
    ('other', 'Other'),
]


TIER_TYPES = [
    ('EO', 'Employee Only'),
    ('ES', 'Employee and Spouse'),
    ('EC', 'Employee and Children'),
    ('EF', 'Employee and Family'),
    ('E1', 'Employee Plus 1'),
    ('E2', 'Employee Plus 2'),
    ('E3', 'Employee Plus 3'),
]


PAYOUT_TYPES = [
    ('salary_percentage', 'Percentage of Salary'),
    ('lump_sum', 'Lump Sum'),
]


PLAN_TERMINATION_TIMING_TYPES = [
    ('same_day', 'Same Day'),
    ('first_of_month', 'First Day of the Month'),
    ('last_of_month', 'Last Day of the Month'),
]


PAYROLL_CYCLE_TYPES = [
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
    ('bi_weekly', 'Bi-weekly'),
    ('semi_monthly', 'Semi-monthly'),
    ('custom', 'Custom'),
]


LIFE_EVENT_TYPES = [
    ('NEW_HIRE', 'New Hire'),
    ('REHIRE', 'Rehire'),
    ('CHANGE_STATUS', 'Change to Eligible Status - Enroll in Benefits'),
    ('MARRIAGE', 'Marriage'),
    ('DIVORCE', 'Divorce, Legal Separation'),
    ('BIRTH', 'Birth, Adoption, Legal Guardianship'),
    ('DEPENDENT', 'Dependent Changes '
     '(Eligibility Change, Court Order, Death)'),
    ('LOSS', 'Loss of Other Coverage'),
    ('SPOUSE_EMPLOYMENT', 'Spouse Employment Status Change'),
    ('BENEFICIARY', 'Beneficiary Change'),
    ('MEDICARE', 'Medicare Eligible'),
]


PAYOUT_INTERVAL_TYPES = [
    ('weekly', 'Weekly'),
    ('monthly', 'Monthly'),
]


STATES = [
    ('AL', 'Alabama'),
    ('AK', 'Alaska'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DE', 'Delaware'),
    ('DC', 'District_Of_Columbia'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('IA', 'Iowa'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('ME', 'Maine'),
    ('MD', 'Maryland'),
    ('MA', 'Massachusetts'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MS', 'Mississippi'),
    ('MO', 'Missouri'),
    ('MT', 'Montana'),
    ('NE', 'Nebraska'),
    ('NV', 'Nevada'),
    ('NH', 'New_Hampshire'),
    ('NJ', 'New_Jersey'),
    ('NM', 'New_Mexico'),
    ('NY', 'New_York'),
    ('NC', 'North_Carolina'),
    ('ND', 'North_Dakota'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('RI', 'Rhode_Island'),
    ('SC', 'South_Carolina'),
    ('SD', 'South_Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('WA', 'Washington'),
    ('WV', 'West_Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming'),
]


class Address(Base):
    street_1 = db.Column(db.Unicode(100), nullable=False, info={'label': 'Street'})
    street_2 = db.Column(db.Unicode(100), info={'label': 'Suite or Apt. Number'})
    city = db.Column(db.Unicode(100), nullable=False, info={'label': 'City'})
    state = db.Column(ChoiceType(STATES), nullable=False, info={'label': 'State'})
    zip_code = db.Column(db.Unicode(10), nullable=False, info={'label': 'Zip Code'})


# Models
# PEOPLE
class PersonMixin(object):
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'', info={'label': 'First Name'})
    middle_name = db.Column(db.Unicode(50), server_default=u'', info={'label': 'Middle Name'})
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'', info={'label': 'Last Name'})
    ssn = db.Column(db.Unicode(11), nullable=False, info={'label': 'Social Security Number'})
    dob = db.Column(db.Date(), nullable=False, info={'label': 'Date of Birth'})
    gender = db.Column(ChoiceType(GENDER_TYPES), info={'label': 'Gender'})
    marital_status = db.Column(ChoiceType(MARITAL_STATUSES), info={'label': 'Marital Status'})
    smoker_type = db.Column(ChoiceType(SMOKER_TYPES), info={'label': 'Smoker Type'})

    @declared_attr
    def address_id(cls):
        return db.Column(db.Integer, db.ForeignKey(
            'address.id'))

    __mapper_args__ = {
        'order_by': ['last_name', 'first_name']
    }


class User(UserMixin, Base):
    username = db.Column(db.String(50), nullable=False, unique=True, info={'label': 'Username'}, index=True)
    password = db.Column(db.String(255), nullable=False, unique=False, info={'label': 'Password'})
    email = db.Column(EmailType(), info={'label': 'Email'}, index=True)
    confirmed_at = db.Column(db.DateTime())
    reset_password_token = db.Column(db.String(100), nullable=True, server_default='')
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0', info={'label': 'May Log In?'})
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))


class Role(Base):
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)
    label = db.Column(db.Unicode(255), server_default=u'')


class UserRoles(Base):
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)


class Dependent(PersonMixin, Base):
    dependent_type = db.Column(ChoiceType(DEPENDENT_TYPES), info={'label': 'Dependent Type'})
    full_time_student = db.Column(db.Boolean(), server_default='0', info={'label': 'Full Time Student?'})
    disabled = db.Column(db.Boolean(), server_default='0', info={'label': 'Disabled?'})
    disability_date = db.Column(db.Date(), info={'label': 'Disability Date'})
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    address_id = db.Column(db.ForeignKey('address.id'))
    address = db.relationship('Address', uselist=False)


class Beneficiary(PersonMixin, Base):
    beneficiary_type = db.Column(ChoiceType(BENEFICIARY_TYPES))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))


class Location(Base):
    code = db.Column(db.String(12), info={'label': 'Code'}, nullable=False)
    description = db.Column(db.String(60), info={'label': 'Description'}, nullable=False)
    effective_date = db.Column(db.Date(), nullable=False, info={'label': 'Effective Date'})

    __mapper_args__ = {
        'order_by': code
    }


class Employee(PersonMixin, Base):
    user = db.relationship('User', uselist=False, single_parent=True, cascade="all, delete-orphan", lazy='joined')
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)
    hire_date = db.Column(db.Date(), nullable=False, info={'label': 'Hire Date'})
    effective_date = db.Column(db.Date(), nullable=False, info={'label': 'Effective Date'})
    termination_date = db.Column(db.Date(), info={'label': 'Termination Date'})
    employee_number = db.Column(db.Unicode(25), info={'label': 'Employee Number'})
    beneficiaries = db.relationship('Beneficiary', uselist=True, single_parent=True, backref='employee',
                                    cascade="all, delete-orphan")
    dependents = db.relationship('Dependent', uselist=True, single_parent=True, backref='employee',
                                 cascade="all, delete-orphan")
    group_id = db.Column(db.String(50), nullable=False, info={'label': 'Group Id'})
    sub_group_id = db.Column(db.String(50), nullable=False, info={'label': 'Sub Group Id'})
    sub_group_effective_date = db.Column(db.Date(), nullable=False, info={'label': 'Sub Group Effective Date'})
    salary_mode = db.Column(ChoiceType(SALARY_MODE_TYPES), info={'label': 'Salary Mode'})
    salary_effective_date = db.Column(db.Date(), nullable=False, info={'label': 'Salary Effective Date'})
    salary = db.Column(db.Numeric(9, 2), nullable=False, info={'label': 'Salary'})
    phone = db.Column(PhoneNumberType(), info={'label': 'Phone'})
    alternate_phone = db.Column(PhoneNumberType(), info={'label': 'Alternate Phone'})
    emergency_contact_phone = db.Column(PhoneNumberType(), info={'label': 'Emergency Contact Phone'})
    emergency_contact_name = db.Column(db.String(), info={'label': 'Emergency Contact Name'})
    emergency_contact_relationship = db.Column(db.String(), info={'label': 'Emergency Contact Relationship'})
    location_id = db.Column(db.ForeignKey('location.id'))
    location = db.relationship('Location', uselist=False)
    address_id = db.Column(db.ForeignKey('address.id'))
    address = db.relationship('Address', uselist=False)


class Carrier(Base):
    name = db.Column(db.Unicode(50), nullable=False, info={'label': 'Name'})
    phone = db.Column(PhoneNumberType(), info={'label': 'Phone'})
    api_endpoint = db.Column(db.Unicode(200), nullable=False, info={'label': 'API Endpoint'})

    __mapper_args__ = {
        'order_by': name
    }


# PLANS
class CoreMixin(object):

    @declared_attr
    def plan_termination_timing_type_id(cls):
        return db.Column(ChoiceType(PLAN_TERMINATION_TIMING_TYPES), info={'label': 'Plan Termination Type'})

    @declared_attr
    def plan_teir_premiums(cls):
        return db.relationship('PlanTierPremium')

    group_number = db.Column(db.Unicode(24), nullable=False, info={'label': 'Group Number'})
    original_effective_date = db.Column(db.Date(), info={'label': 'Original Effective Date'})
    renewal_date = db.Column(db.Date(), info={'label': 'Renewal Date'})
    existing = db.Column(db.Boolean(), nullable=False, default=False, info={'label': 'Existing?'})
    list_billed = db.Column(db.Boolean(), info={'label': 'List Billed?'})
    doctor_selection_required = db.Column(db.Boolean(), info={'label': 'Doctor Selection Required?'})
    account_rep_name = db.Column(db.Unicode(40), info={'label': 'Account Rep. Name'})
    cobra_eligible = db.Column(db.Boolean(), nullable=False, default=False, info={'label': 'Cobra Eligible?'})
    pre_tax = db.Column(db.Boolean(), nullable=False, default=False, info={'label': 'Pre tax?'})


class GroupMixin(object):
    minimum_benefit = db.Column(db.Numeric(10, 2), nullable=False, info={'label': 'Minimum Benefit'})
    maximum_benefit = db.Column(db.Numeric(10, 2), nullable=False, info={'label': 'Maximum Benefit'})


class SupplementalMixin(object):
    pass


class Plan(Base):
    not_available_choices = [(v, n, False) for v, n in STATES]
    plantype = db.Column(db.String(50), info={'label': 'Plan Type'})
    code = db.Column(db.String(10), info={'label': 'Code'})
    name = db.Column(db.Unicode(70), info={'label': 'Name'})
    cust_service_phone = db.Column(PhoneNumberType(), info={'label': 'Customer Service Phone'})
    website = db.Column(URLType, info={'label': 'Website'})
    not_available_in = db.Column(ScalarListType(), info={'label': 'Not Available In'})
    active = db.Column('is_active', db.Boolean(), nullable=False, index=True, server_default='1',
                       info={'label': 'Plan is active?'})
    description = db.Column(db.String(250), info={'label': ''})
    special_instructions = db.Column(db.String(250), info={'label': ''})
    plan_tier_premiums = db.relationship('PlanTierPremium', back_populates="plan")
    age_banded_premiums = db.relationship('AgeBandedPremium', back_populates="plan")

    def premium_is_tiered(self):
        return False

    def premium_is_age_banded(self):
        return False

    def requires_amount_from_user(self):
        return False

    def has_coverage_amount_choices(self):
        return False

    __mapper_args__ = {
        'polymorphic_on': plantype,
        'order_by': name
    }


class MedicalPlan(Plan, CoreMixin):
    __tablename__ = 'medical_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True, info={'widget': widgets.HiddenInput()})
    self_funded = db.Column(db.Boolean(), nullable=False, info={'label': 'Self Funded?'})
    carrier_id = db.Column(db.ForeignKey('carrier.id'))
    carrier = db.relationship('Carrier', uselist=False, info={'label': 'Caarrier'})

    def premium_is_tiered(self):
        return True

    __mapper_args__ = {
        'polymorphic_identity': 'medical',
        'inherit_condition': (id == Plan.id),
    }


class DentalPlan(Plan, CoreMixin):
    __tablename__ = 'dental_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    carrier_id = db.Column(db.ForeignKey('carrier.id'))
    carrier = db.relationship('Carrier', uselist=False)

    def premium_is_tiered(self):
        return True

    __mapper_args__ = {
        'polymorphic_identity': 'dental',
        'inherit_condition': (id == Plan.id),
    }


class VisionPlan(Plan, CoreMixin):
    __tablename__ = 'vision_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    carrier_id = db.Column(db.ForeignKey('carrier.id'))
    carrier = db.relationship('Carrier', uselist=False)

    def premium_is_tiered(self):
        return True

    __mapper_args__ = {
        'polymorphic_identity': 'vision',
        'inherit_condition': (id == Plan.id),
    }


class MedicalDentalBundlePlan(Plan, CoreMixin):
    __tablename__ = 'medical_dental_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    self_funded = db.Column(db.Boolean(), nullable=False, info={'label': 'Self Funded?'})
    carrier_id = db.Column(db.ForeignKey('carrier.id'))
    carrier = db.relationship('Carrier', uselist=False, info={'label': 'Caarrier'})

    def premium_is_tiered(self):
        return True

    __mapper_args__ = {
        'polymorphic_identity': 'medical_dental',
        'inherit_condition': (id == Plan.id),
    }


class MedicalVisionBundlePlan(Plan, CoreMixin):
    __tablename__ = 'medical_vision_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    self_funded = db.Column(db.Boolean(), nullable=False, info={'label': 'Self Funded?'})
    carrier_id = db.Column(db.ForeignKey('carrier.id'))
    carrier = db.relationship('Carrier', uselist=False, info={'label': 'Caarrier'})

    def premium_is_tiered(self):
        return True

    __mapper_args__ = {
        'polymorphic_identity': 'medical_vision',
        'inherit_condition': (id == Plan.id),
    }


class MedicalDentalVisionBundlePlan(Plan, CoreMixin):
    __tablename__ = 'medical_dental_vision_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    self_funded = db.Column(db.Boolean(), nullable=False, info={'label': 'Self Funded?'})
    carrier_id = db.Column(db.ForeignKey('carrier.id'))
    carrier = db.relationship('Carrier', uselist=False, info={'label': 'Caarrier'})

    def premium_is_tiered(self):
        return True

    __mapper_args__ = {
        'polymorphic_identity': 'medical_detnal_vision',
        'inherit_condition': (id == Plan.id),
    }


class DentalVisionBundlePlan(Plan, CoreMixin):
    __tablename__ = 'dental_vision_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    carrier_id = db.Column(db.ForeignKey('carrier.id'))
    carrier = db.relationship('Carrier', uselist=False, info={'label': 'Caarrier'})

    def premium_is_tiered(self):
        return True

    __mapper_args__ = {
        'polymorphic_identity': 'detnal_vision',
        'inherit_condition': (id == Plan.id),
    }


class EAPPlan(Plan, GroupMixin):
    __tablename__ = 'eap_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    def premium_is_variable(self):
        return True

    __mapper_args__ = {
        'polymorphic_identity': 'eap',
        'inherit_condition': (id == Plan.id),
    }


class LTDPlan(Plan, GroupMixin):
    __tablename__ = 'ltd_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    max_weekly_benefit = db.Column(db.Numeric(6, 2), nullable=False, info={'label': 'Maximum Weekly Benefit'})
    max_monthly_benefit = db.Column(db.Numeric(6, 2), nullable=False, info={'label': 'Maximum Monthly Benefit'})
    benefit_percentage = db.Column(db.Numeric(6, 2), nullable=False, info={'label': 'Benefit Percentage'})

    __mapper_args__ = {
        'polymorphic_identity': 'ltd',
        'inherit_condition': (id == Plan.id),
    }


class STDPlan(Plan, GroupMixin):
    __tablename__ = 'std_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    max_weekly_benefit = db.Column(db.Numeric(6, 2), nullable=False, info={'label': 'Maximum Weekly Benefit'})
    max_monthly_benefit = db.Column(db.Numeric(6, 2), nullable=False, info={'label': 'Maximum Monthly Benefit'})
    benefit_percentage = db.Column(db.Numeric(6, 2), nullable=False, info={'label': 'Benefit Percentage'})
    mandatory_in_states = db.Column(ScalarListType(), info={'label': 'Mandatory In'})

    __mapper_args__ = {
        'polymorphic_identity': 'std',
        'inherit_condition': (id == Plan.id),
    }


class LifeADDPlan(Plan, GroupMixin):
    __tablename__ = 'life_add_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'life_add',
        'inherit_condition': (id == Plan.id),
    }


class LifeADDDependentPlan(Plan, GroupMixin):
    __tablename__ = 'life_add_dependent_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'life_add_dependent',
        'inherit_condition': (id == Plan.id),
    }


class FSAPlan(Plan, SupplementalMixin):
    __tablename__ = 'fsa_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    minimum_contribution = db.Column(db.Numeric(10, 2), nullable=False, info={'label': 'Minimum Contribution'})
    maximum_contribution = db.Column(db.Numeric(10, 2), nullable=False, info={'label': 'Maximum Contribution'})

    __mapper_args__ = {
        'polymorphic_identity': 'fsa',
        'inherit_condition': (id == Plan.id),
    }


class ParkingTransitPlan(Plan, SupplementalMixin):
    __tablename__ = 'parking_transit_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'parking_transit',
        'inherit_condition': (id == Plan.id),
    }


class HSAPlan(Plan, SupplementalMixin):
    __tablename__ = 'hsa_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'hsa',
        'inherit_condition': (id == Plan.id),
    }


class Employee401KPlan(Plan, SupplementalMixin):
    __tablename__ = 'employee_401k_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': '401k',
        'inherit_condition': (id == Plan.id),
    }


class SupplumentalInsurancePlan(Plan, SupplementalMixin):
    __tablename__ = 'supplemental_insurance_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'supplemental_insurance',
        'inherit_condition': (id == Plan.id),
    }


class LongTermCarePlan(Plan, SupplementalMixin):
    __tablename__ = 'long_term_care_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'long_term_care',
        'inherit_condition': (id == Plan.id),
    }


class OtherPlan(Plan, SupplementalMixin):
    __tablename__ = 'other_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'other',
        'inherit_condition': (id == Plan.id),
    }


class CancerPlan(Plan, SupplementalMixin):
    __tablename__ = 'cancer_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'cancer',
        'inherit_condition': (id == Plan.id),
    }


class CriticalIllnessPlan(Plan, SupplementalMixin):
    __tablename__ = 'cricial_illness_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    payout_amount = db.Column(db.Numeric(6, 2))

    __mapper_args__ = {
        'polymorphic_identity': 'critical_illness',
        'inherit_condition': (id == Plan.id),
    }


# Plan Premiums
class PlanPremium(Base):
    premium = db.Column(db.Numeric(6, 2), nullable=False, info={'label': 'Premium'}, server_default='0')
    employer_portion = db.Column(db.Numeric(6, 2), nullable=False, info={'label': 'Employer Portion'},
                                 server_default='0')
    employee_portion = db.Column(db.Numeric(6, 2), nullable=False, info={'label': 'Employee Portion'},
                                 server_default='0')
    premiumtype = db.Column(db.String(50), info={'label': 'Premium Type'})
    flat_amount = db.Column(db.Numeric(6, 2), info={'label': 'Flat Amount'}, server_default='0')
    percentage = db.Column(db.Numeric(3, 2), info={'label': 'Percentage'}, server_default='0')

    __mapper_args__ = {
        'polymorphic_on': premiumtype,
    }


class AgeBandedPremium(PlanPremium):
    __tablename__ = 'age_banded_premium'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan_premium.id'), primary_key=True, info={'widget': widgets.HiddenInput()})
    plan_id = db.Column(None, db.ForeignKey('plan.id'), index=True)
    plan = db.relationship('Plan', foreign_keys=[plan_id], back_populates='age_banded_premiums')
    low = db.Column(db.Integer(), nullable=False)
    high = db.Column(db.Integer(), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'age_banded',
        'inherit_condition': (id == PlanPremium.id),
    }


class PlanTierPremium(PlanPremium):
    """Prices for all tiered plans."""
    __tablename__ = 'plan_tier_premium'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan_premium.id'), primary_key=True, info={'widget': widgets.HiddenInput()})
    plan_id = db.Column(None, db.ForeignKey('plan.id'), index=True)
    plan = db.relationship('Plan', foreign_keys=[plan_id], back_populates='plan_tier_premiums')
    tier_type = db.Column(ChoiceType(TIER_TYPES), info={'label': 'Tier'})

    __mapper_args__ = {
        'polymorphic_identity': 'tiered',
        'inherit_condition': (id == PlanPremium.id),
    }


# Eligibility
class EmployeeEligibility(Base):
    full_time_only = db.Column(db.Boolean(), default=False)
    minimum_days_employed = db.Column(db.Integer(), default=0)


class DependentEligibility(Base):
    eligible = db.Column(db.Boolean(), default=False)


class DomesticPartnerEligibility(Base):
    eligible = db.Column(db.Boolean(), default=False)


class EnrollmentPeriod(Base):
    year = db.Column(db.Integer())


class Enrollment(Base):
    """A collection of choices an employee makes during enrollment"""
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), index=True)
    employee = db.relationship('Employee', uselist=False)
    life_event = db.Column(ChoiceType(LIFE_EVENT_TYPES), info={'label': 'Life Event'})
    elections = db.relationship('Election', backref=backref('enrollment', single_parent=True,
                                                            cascade="all, delete-orphan"))
    enrollment_period_id = db.Column(db.Integer, db.ForeignKey('enrollment_period.id'))
    enrollment_period = db.relationship('EnrollmentPeriod')


class Election(Base):
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollment.id'))
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), index=True)
    plan = db.relationship('Plan')
    electiontype = db.Column(db.String(50), info={'label': 'Election Type'})

    __mapper_args__ = {
        'polymorphic_on': electiontype,
    }


class TieredPriceElection(Election):
    __tablename__ = 'tiered_price_election'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('election.id'), primary_key=True, info={'widget': widgets.HiddenInput()})
    plan_tier_premium_id = db.Column(db.Integer, db.ForeignKey('plan_tier_premium.id'))
    plan_tier_premium = db.relationship('PlanTierPremium')

    __mapper_args__ = {
        'polymorphic_identity': 'tiered',
        'inherit_condition': (id == Election.id),
    }


class SelfPricedElection(Election):
    __tablename__ = 'self_price_election'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('election.id'), primary_key=True, info={'widget': widgets.HiddenInput()})
    amount = db.Column(db.Numeric(11, 2))

    __mapper_args__ = {
        'polymorphic_identity': 'self_priced',
        'inherit_condition': (id == Election.id),
    }


class AgeBandedPriceElection(Election):
    __tablename__ = 'age_banded_price_election'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('election.id'), primary_key=True, info={'widget': widgets.HiddenInput()})
    __mapper_args__ = {
        'polymorphic_identity': 'age_banded',
        'inherit_condition': (id == Election.id),
    }
