# -*- coding: utf-8 -*-
# vie:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from datetime import date
import inflection
import locale

from flask_user import SQLAlchemyAdapter, UserManager, UserMixin
from sqlalchemy import and_
from sqlalchemy.orm import backref
from sqlalchemy_utils import (
    ChoiceType,
    EmailType,
    PhoneNumberType,
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

    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})

Base.query = db.session.query_property()


# CHOICES
GENDER_TYPES = [
    ('male', 'Male'),
    ('female', 'Female'),
]


MARITAL_STATUS_TYPES = [
    ('single', 'Single'),
    ('married', 'Married'),
    ('divorced', 'Divorced'),
    ('widowed', 'Widowed'),
]


SMOKER_TYPES = [
    ('smoker', 'Smoker'),
    ('non-smoker', 'Non Smoker'),
]


BENEFICIARY_TYPES = [
    ('primary', 'PRIMARY'),
    ('contingent', 'CONTINGENT'),
]

DEPENDENT_TYPES = [
    ('husband', 'Husband'),
    ('wife', 'Wife'),
    ('son', 'Son'),
    ('daughter', 'Daughter'),
    ('incapacitated', 'Incapacitated'),
]

SALARY_MODE_TYPES = [
    ('hourly', 'Hourly'),
    ('weekly', 'Weekly'),
    ('bi-weekly', 'Bi-weekly'),
    ('semi-monthly', 'Semi-monthly'),
    ('monthly', 'Monthly'),
    ('annually', 'Annually'),
]


FAMILY_TIER_TYPES = [
    ('employee_only', 'Employee Only'),
    ('employee_and_spouse', 'Employee and Spouse'),
    ('employee_and_children', 'Employee and Children'),
    ('employee_and_family', 'Employee and Family'),
    ('employee_plus_1', 'Employee Plus 1'),
    ('employee_plus_2', 'Employee Plus 2'),
    ('employee_plus_3', 'Employee Plus 3'),
]


PAYOUT_TYPES = [
    ('percentage_of_salary', 'Percentage of Salary'),
    ('lump_sum', 'Lump Sum'),
]


PLAN_TERMINATION_TIMING_TYPES = [
    ('same_day', 'Same Day'),
    ('first_day_of_the_month', 'First Day of the Month'),
    ('last_day_of_the_month', 'Last Day of the Month'),
]


PAYROLL_CYCLE_TYPES = [
    ('weekly', 'Weekly'),
    ('bi-weekly', 'Bi-weekly'),
    ('semi-monthly', 'Semi-monthly'),
    ('monthly', 'Monthly'),
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

PREMIUM_FREQUENCY_TYPE = [
    ('weekly', 'Weekly'),
    ('bi-weekly', 'Bi-Weekly'),
    ('monthly', 'Monthly'),
    ('bi-monthly', 'Bi-Monthly'),
    ('quarterly', 'Quarterly'),
    ('semi-annually', 'Semi-Annually'),
    ('annually', 'Annually'),
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


# Models
# PEOPLE
class Address(Base):
    street_1 = db.Column(db.Unicode(100), nullable=False, info={'label': 'Street'})
    street_2 = db.Column(db.Unicode(100), info={'label': 'Suite or Apt. Number'})
    city = db.Column(db.Unicode(100), nullable=False, info={'label': 'City'})
    state = db.Column(ChoiceType(STATES), nullable=False, info={'label': 'State'})
    zip_code = db.Column(db.Unicode(10), nullable=False, info={'label': 'Zip Code'})


class PersonMixin(object):
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'', info={'label': 'First Name'})
    middle_name = db.Column(db.Unicode(50), server_default=u'', info={'label': 'Middle Name'})
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'', info={'label': 'Last Name'})
    ssn = db.Column(db.Unicode(11), nullable=False, info={'label': 'Social Security Number'})
    dob = db.Column(db.Date, nullable=False, info={'label': 'Date of Birth'})
    gender = db.Column(ChoiceType(GENDER_TYPES), info={'label': 'Gender'})
    marital_status = db.Column(ChoiceType(MARITAL_STATUS_TYPES), info={'label': 'Marital Status'})
    smoker_type = db.Column(ChoiceType(SMOKER_TYPES), info={'label': 'Smoker Status'})

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
    email = db.Column(EmailType, info={'label': 'Email'}, index=True)
    confirmed_at = db.Column(db.DateTime)
    reset_password_token = db.Column(db.String(100), nullable=True, server_default='')
    active = db.Column('is_active', db.Boolean, nullable=False, server_default='0', info={'label': 'May Log In?'})
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))


class Role(Base):
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)
    label = db.Column(db.Unicode(255), server_default=u'')


class UserRoles(Base):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))


db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)


class Dependent(PersonMixin, Base):
    dependent_type = db.Column(ChoiceType(DEPENDENT_TYPES), info={'label': 'Dependent Type'})
    full_time_student = db.Column(db.Boolean, server_default='0', info={'label': 'Full Time Student?'})
    disabled = db.Column(db.Boolean, server_default='0', info={'label': 'Disabled?'})
    disability_date = db.Column(db.Date, info={'label': 'Disability Date'})
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    address_id = db.Column(db.ForeignKey('address.id'))
    address = db.relationship('Address', uselist=False)


class Beneficiary(PersonMixin, Base):
    beneficiary_type = db.Column(ChoiceType(BENEFICIARY_TYPES))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))


class Location(Base):
    code = db.Column(db.String(12), info={'label': 'Code'}, nullable=False)
    description = db.Column(db.String(60), info={'label': 'Description'}, nullable=False)
    effective_date = db.Column(db.Date, nullable=False, info={'label': 'Effective Date'})

    __mapper_args__ = {
        'order_by': code
    }


class Employee(PersonMixin, Base):
    user = db.relationship('User', uselist=False, single_parent=True, cascade="all, delete-orphan", lazy='joined')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    hire_date = db.Column(db.Date, nullable=False, info={'label': 'Hire Date'})
    effective_date = db.Column(db.Date, nullable=False, info={'label': 'Effective Date'})
    termination_date = db.Column(db.Date, info={'label': 'Termination Date'})
    employee_number = db.Column(db.Unicode(25), info={'label': 'Employee Number'})
    beneficiaries = db.relationship('Beneficiary', uselist=True, single_parent=True, backref='employee',
                                    cascade="all, delete-orphan")
    dependents = db.relationship('Dependent', uselist=True, single_parent=True, backref='employee',
                                 cascade="all, delete-orphan")
    group_id = db.Column(db.String(50), nullable=False, info={'label': 'Group Id'})
    sub_group_id = db.Column(db.String(50), nullable=False, info={'label': 'Sub Group Id'})
    sub_group_effective_date = db.Column(db.Date, nullable=False, info={'label': 'Sub Group Effective Date'})
    salary_mode = db.Column(ChoiceType(SALARY_MODE_TYPES), info={'label': 'Salary Mode'})
    salary_effective_date = db.Column(db.Date, nullable=False, info={'label': 'Salary Effective Date'})
    salary = db.Column(db.Numeric(9, 2), nullable=False, info={'label': 'Salary'})
    phone = db.Column(PhoneNumberType, info={'label': 'Phone'})
    alternate_phone = db.Column(PhoneNumberType, info={'label': 'Alternate Phone'})
    emergency_contact_phone = db.Column(PhoneNumberType, info={'label': 'Emergency Contact Phone'})
    emergency_contact_name = db.Column(db.String, info={'label': 'Emergency Contact Name'})
    emergency_contact_relationship = db.Column(db.String, info={'label': 'Emergency Contact Relationship'})
    location_id = db.Column(db.ForeignKey('location.id'))
    location = db.relationship('Location', uselist=False)
    address_id = db.Column(db.ForeignKey('address.id'))
    address = db.relationship('Address', uselist=False)
    spouse_dob = db.Column(db.Date, nullable=False, info={'label': 'Spouse Date of Birth'})
    spouse_smoker_type = db.Column(ChoiceType(SMOKER_TYPES), info={'label': 'Spouse Smoker Status'})


class Carrier(Base):
    name = db.Column(db.Unicode(50), nullable=False, info={'label': 'Name'})
    phone = db.Column(PhoneNumberType, info={'label': 'Phone'})
    api_endpoint = db.Column(db.Unicode(200), nullable=False, info={'label': 'API Endpoint'})

    __mapper_args__ = {
        'order_by': name
    }


# PLANS
class PreTaxMixin(object):
    def is_pretax(self):
        return True


class PostTaxMixin(object):
    def is_pretax(self):
        return False


class PreOrPostTaxMixin(object):
    pre_tax = db.Column(db.Boolean, nullable=False, default=False, info={'label': 'Pre tax?'})

    def is_pretax(self):
        return self.pre_tax.value


class CoreMixin(object):
    @declared_attr
    def plan_termination_timing_type_id(cls):
        return db.Column(ChoiceType(PLAN_TERMINATION_TIMING_TYPES), info={'label': 'Plan Termination Type'})

    group_number = db.Column(db.Unicode(24), nullable=False, info={'label': 'Group Number'})
    original_effective_date = db.Column(db.Date, info={'label': 'Original Effective Date'})
    renewal_date = db.Column(db.Date, info={'label': 'Renewal Date'})
    list_billed = db.Column(db.Boolean, info={'label': 'List Billed?'})
    doctor_selection_required = db.Column(db.Boolean, info={'label': 'Doctor Selection Required?'})
    cobra_eligible = db.Column(db.Boolean, nullable=False, default=False, info={'label': 'Cobra Eligible?'})

    def get_premium_choices(self, chosen_value, employee):
        flat = self.er_flat_amount_contributed
        percent = self.er_percentage_contributed
        choices = []
        for premium in self.premiums:
            total = premium.amount
            if flat:
                er = flat
            else:
                er = total * (percent or 0)
            ee = total - er
            choices.append((premium.family_tier.code, premium.family_tier.value, premium.id == chosen_value,
                            locale.currency(total, grouping=True),
                            locale.currency(er, grouping=True),
                            locale.currency(ee, grouping=True)))
        choices.append(('DE', 'Decline', chosen_value is None, '', '', ''))
        return choices


class GroupMixin(object):
    pass


class SupplementalMixin(object):
    pass


class EmployerContributionMixin(object):
    er_flat_amount_contributed = db.Column(db.Numeric(9, 2), info={'label': 'Flat Amount Contributed by Employer'})
    er_percentage_contributed = db.Column(db.Numeric(3, 2), info={'label': 'Percentage Contributed by Employer'})
    er_max_contribution = db.Column(db.Numeric(9, 2), info={'label': 'Maximum Employer Contribution'})


class PlanPremiumMetaValuesMixin(object):
    salary_chunk_size = db.Column(
        db.Integer, info={'label': 'Premium is based on this portion of salary'})
    coverage_chunk_size = db.Column(
        db.Integer, info={'label': 'Premium is based on this portion of elected coverage'})


class IRSLimits(Base):
    min_fsa_medical_contribution = db.Column(db.Numeric(9, 2))
    max_fsa_medical_contribution = db.Column(db.Numeric(9, 2))
    max_fsa_dependent_care_contribution = db.Column(db.Numeric(9, 2))
    max_hsa_individual_contribution = db.Column(db.Numeric(9, 2))
    max_hsa_family_contribution = db.Column(db.Numeric(9, 2))
    max_hsa_family_over_55_contribution = db.Column(db.Numeric(9, 2))
    max_401k_salary_deferal = db.Column(db.Numeric(9, 2))
    max_401k_salary_deferal_over_50 = db.Column(db.Numeric(9, 2))


class Plan(Base, EmployerContributionMixin, PlanPremiumMetaValuesMixin):
    plantype = db.Column(db.String(50), info={'label': 'Plan Type'})
    code = db.Column(db.String(10), info={'label': 'Code'})
    name = db.Column(db.Unicode(70), info={'label': 'Name'})
    description = db.Column(db.String(250), info={'label': ''})
    special_instructions = db.Column(db.String(250), info={'label': ''})
    active = db.Column('is_active', db.Boolean, nullable=False, index=True, server_default='1',
                       info={'label': 'Plan is active?'})
    carrier_id = db.Column(db.ForeignKey('carrier.id'))
    carrier = db.relationship('Carrier', uselist=False, info={'label': 'Caarrier'})
    website = db.Column(URLType, info={'label': 'Website'})
    cust_service_phone = db.Column(PhoneNumberType, info={'label': 'Customer Service Phone'})
    premiums = db.relationship('Premium', back_populates="plan")

    def get_election_form(self):
        if self.premiums:
            prem = self.premiums[0]
            if prem.family_tier:
                from perks.forms import TieredElectionForm
                return TieredElectionForm
            elif prem.rate:
                from perks.forms import AmountNeededElectionForm
                return AmountNeededElectionForm
            else:
                from perks.forms import BooleanElectionForm
                return BooleanElectionForm

    __mapper_args__ = {
        'polymorphic_on': plantype,
        'order_by': name
    }


# Core plans
class MedicalPlan(Plan, CoreMixin, PreOrPostTaxMixin):
    __tablename__ = 'medical_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True, info={'widget': widgets.HiddenInput()})

    __mapper_args__ = {
        'polymorphic_identity': 'medical',
        'inherit_condition': (id == Plan.id),
    }


class DentalPlan(Plan, CoreMixin, PreOrPostTaxMixin):
    __tablename__ = 'dental_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'dental',
        'inherit_condition': (id == Plan.id),
    }


class VisionPlan(Plan, CoreMixin, PreOrPostTaxMixin):
    __tablename__ = 'vision_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'vision',
        'inherit_condition': (id == Plan.id),
    }


class MedicalDentalBundlePlan(Plan, CoreMixin, PreOrPostTaxMixin):
    __tablename__ = 'medical_dental_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'medical_dental',
        'inherit_condition': (id == Plan.id),
    }


class MedicalVisionBundlePlan(Plan, CoreMixin, PreOrPostTaxMixin):
    __tablename__ = 'medical_vision_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'medical_vision',
        'inherit_condition': (id == Plan.id),
    }


class MedicalDentalVisionBundlePlan(Plan, CoreMixin, PreOrPostTaxMixin):
    __tablename__ = 'medical_dental_vision_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'medical_detnal_vision',
        'inherit_condition': (id == Plan.id),
    }


class DentalVisionBundlePlan(Plan, CoreMixin, PreOrPostTaxMixin):
    __tablename__ = 'dental_vision_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'detnal_vision',
        'inherit_condition': (id == Plan.id),
    }


# Group Plans
# Life

class BasicLifePlan(Plan, PostTaxMixin):
    # has a composite premium, 100% employer paid
    __tablename__ = 'life_add_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    # benefits
    multiple_of_salary_paid = db.Column(db.Numeric(4, 2))
    min_benefit = db.Column(db.Numeric(9, 2))
    max_benefit = db.Column(db.Numeric(9, 2))
    spouse_benefit = db.Column(db.Numeric(9, 2))
    child_benefit = db.Column(db.Numeric(9, 2))
    guarantee_issue = db.Column(db.Numeric(9, 2))
    age_based_reductions = db.relationship('AgeBasedReduction', back_populates="plan")
    addl_salary_multiple_accidental_death = db.Column(db.Numeric(4, 2))
    addl_salary_multiple_accidental_dismemberment = db.Column(db.Numeric(4, 2))

    __mapper_args__ = {
        'polymorphic_identity': 'life_add',
        'inherit_condition': (id == Plan.id),
    }

    def _filter_premiums(self, employee):
        filters = [Premium.plan_id == self.id]
        today = date.today()
        born = employee.dob
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        q = Premium.query
        # just grab the first premium as it will have the same structure as all the others for this plan
        prem = self.premiums[0]
        if prem.age:
            filters.append(Premium.age == age)
        if prem.gender:
            filters.append(Premium.gender == employee.gender)
        if prem.smoker_status:
            filters.append(Premium.smoker_status == employee.smoker_type)

        q = q.filter(*filters)

        if prem.age_banded_tier:
            q = q.join(AgeBandedTier).filter(AgeBandedTier.plan_id == Premium.plan_id)
            q = q.filter(and_(AgeBandedTier.low <= age, AgeBandedTier.high >= age))
        # now get the one premium that applies to our employee
        return q.one()

    def get_premium_choices(self, chosen_value, employee):
        choices = []
        prem = self._filter_premiums(employee)
        selected = False
        flat = self.er_flat_amount_contributed
        percent = self.er_percentage_contributed
        for coverage in range(self.min_election, self.max_election + 1, self.increments):
            total = (coverage / 1000) * prem.rate
            if flat:
                er = flat
            else:
                er = total * (percent or 0)
            ee = total - er
            if chosen_value and chosen_value != 'DE':
                selected = int(chosen_value) == coverage
            choices.append((coverage, coverage, selected,
                            locale.currency(total, grouping=True),
                            locale.currency(er, grouping=True),
                            locale.currency(ee, grouping=True)))
        choices.append(('DE', 'Decline', chosen_value is None, '', '', ''))
        return choices


class VoluntaryLifePlan(Plan, PostTaxMixin):
    __tablename__ = 'voluntary_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    increments = db.Column(db.Integer)
    min_election = db.Column(db.Numeric(9, 2))
    max_election = db.Column(db.Numeric(9, 2))
    # benefits
    age_based_reductions = db.relationship('AgeBasedReduction', back_populates="plan")
    guarantee_issue = db.Column(db.Numeric(9, 2))
    # optional ADD
    addl_salary_multiple_accidental_dismemberment = db.Column(db.Numeric(4, 2))
    age_based_reductions = db.relationship('AgeBasedReduction', back_populates="plan")

    __mapper_args__ = {
        'polymorphic_identity': 'voluntary_life',
        'inherit_condition': (id == Plan.id),
    }

    def _filter_premiums(self, employee):
        filters = [Premium.plan_id == self.id]
        today = date.today()
        born = employee.dob
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        q = Premium.query
        # just grab the first premium as it will have the same structure as all the others for this plan
        prem = self.premiums[0]
        if prem.age:
            filters.append(Premium.age == age)
        if prem.gender:
            filters.append(Premium.gender == employee.gender)
        if prem.smoker_status:
            filters.append(Premium.smoker_status == employee.smoker_type)

        q = q.filter(*filters)

        if prem.age_banded_tier:
            q = q.join(AgeBandedTier).filter(AgeBandedTier.plan_id == Premium.plan_id)
            q = q.filter(and_(AgeBandedTier.low <= age, AgeBandedTier.high >= age))
        # now get the one premium that applies to our employee
        return q.one()

    def get_premium_choices(self, chosen_value, employee):
        choices = []
        prem = self._filter_premiums(employee)
        selected = False
        flat = self.er_flat_amount_contributed
        percent = self.er_percentage_contributed
        for coverage in range(self.min_election, self.max_election + 1, self.increments):
            total = (coverage / 1000) * prem.rate
            if flat:
                er = flat
            else:
                er = total * (percent or 0)
            ee = total - er
            if chosen_value and chosen_value != 'DE':
                selected = int(chosen_value) == coverage
            choices.append((coverage, coverage, selected,
                            locale.currency(total, grouping=True),
                            locale.currency(er, grouping=True),
                            locale.currency(ee, grouping=True)))
        choices.append(('DE', 'Decline', chosen_value is None, '', '', ''))
        return choices


class SpouseVoluntaryLifePlan(VoluntaryLifePlan):
    __tablename__ = 'spouse_voluntary_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    use_employee_age_for_spouse = db.Column(db.Boolean)
    __mapper_args__ = {
        'polymorphic_identity': 'spouse_voluntary_life',
        'inherit_condition': (id == Plan.id),
    }

    def _filter_premiums(self, employee):
        filters = [Premium.plan_id == self.id]
        today = date.today()
        born = employee.dob if self.use_employee_age_for_spouse else employee.spouse_dob
        age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        q = Premium.query
        # just grab the first premium as it will have the same structure as all the others for this plan
        prem = self.premiums[0]
        if prem.age:
            filters.append(Premium.age == age)
        if prem.gender:
            filters.append(Premium.gender == employee.gender)
        if prem.smoker_status:
            filters.append(Premium.smoker_status == employee.smoker_type)

        q = q.filter(*filters)

        if prem.age_banded_tier:
            q = q.join(AgeBandedTier).filter(AgeBandedTier.plan_id == Premium.plan_id)
            q = q.filter(and_(AgeBandedTier.low <= age, AgeBandedTier.high >= age))
        # now get the one premium that applies to our employee
        return q.one()


class ChildVoluntaryLifePlan(VoluntaryLifePlan):
    __tablename__ = 'child_voluntary_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'child_voluntary_life',
        'inherit_condition': (id == Plan.id),
    }


class StandaloneADDPlan(Plan, PostTaxMixin):
    __tablename__ = 'standalone_add_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    # benefits
    salary_multiple_accidental_death = db.Column(db.Numeric(4, 2))
    salary_multiple_accidental_dismemberment = db.Column(db.Numeric(4, 2))

    __mapper_args__ = {
        'polymorphic_identity': 'standalone_add',
        'inherit_condition': (id == Plan.id),
    }


class WholeLifePlan(Plan, PostTaxMixin):
    __tablename__ = 'whole_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    # benefits
    spouse_benefit = db.Column(db.Numeric(9, 2))
    child_benefit = db.Column(db.Numeric(9, 2))

    __mapper_args__ = {
        'polymorphic_identity': 'whole_life',
        'inherit_condition': (id == Plan.id),
    }


class UniversalLifePlan(Plan, PostTaxMixin):
    __tablename__ = 'universal_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    # benefits
    spouse_benefit = db.Column(db.Numeric(9, 2))
    child_benefit = db.Column(db.Numeric(9, 2))

    __mapper_args__ = {
        'polymorphic_identity': 'universal_life',
        'inherit_condition': (id == Plan.id),
    }


# LTD
class LTDPlan(Plan, GroupMixin, PreOrPostTaxMixin):
    __tablename__ = 'ltd_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    # has fixed premium based on some formula from the carrier across all employees
    max_monthly_benefit = db.Column(db.Numeric(9, 2), nullable=False, info={'label': 'Maximum Monthly Benefit'})
    percentage_of_salary_paid = db.Column(db.Numeric(3, 2), nullable=False, info={'label': 'Benefit Percentage'})

    __mapper_args__ = {
        'polymorphic_identity': 'ltd',
        'inherit_condition': (id == Plan.id),
    }


class LTDVoluntaryPlan(Plan, GroupMixin, PreOrPostTaxMixin):
    # has age banded rates (e.g. 25 - 34 = 0.05, 35 - 39 = 0.06)
    # has an elected coverage amount  (e.g. $80K or $90K in 10K intervals)
    # so monthly premium for age 37 at $70,000 = 0.06 * 70 or $4.20/month
    __tablename__ = 'ltd_voluntary_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    max_monthly_benefit = db.Column(db.Numeric(9, 2), nullable=False, info={'label': 'Maximum Monthly Benefit'})
    percentage_of_salary_paid = db.Column(db.Numeric(3, 2), nullable=False, info={'label': 'Benefit Percentage'})

    __mapper_args__ = {
        'polymorphic_identity': 'ltd_voluntary',
        'inherit_condition': (id == Plan.id),
    }


# STD
class STDPlan(Plan, GroupMixin, PostTaxMixin):
    __tablename__ = 'std_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    max_weekly_benefit = db.Column(db.Numeric(9, 2), nullable=False, info={'label': 'Maximum Weekly Benefit'})
    percentage_of_salary_paid = db.Column(db.Numeric(3, 2), nullable=False, info={'label': 'Benefit Percentage'})

    __mapper_args__ = {
        'polymorphic_identity': 'std',
        'inherit_condition': (id == Plan.id),
    }


class STDVoluntaryPlan(Plan, GroupMixin, PostTaxMixin):
    # has a weekly benefit not a monthly benefit -> = % of weekly salary usually 60% or so
    # premium = age banded rate (e.g. 0.29) * weekly benefit / $10)
    # weekly salary = $500 and age rate is 0.31 and plan pays 60% of salary THEN
    # weekly benefit = $500 * 60% = $300
    # so premium = .31 * ($300 / 10) = $9.30
    __tablename__ = 'std_voluntary_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    max_weekly_benefit = db.Column(db.Numeric(9, 2), nullable=False, info={'label': 'Maximum Weekly Benefit'})
    percentage_of_salary_paid = db.Column(db.Numeric(3, 2), nullable=False, info={'label': 'Benefit Percentage'})
    # voluntary - could have a composite premium but usually age banded rates

    __mapper_args__ = {
        'polymorphic_identity': 'std_voluntary',
        'inherit_condition': (id == Plan.id),
    }


# Savings Plans
class FSAMedicalPlan(Plan, GroupMixin, PreTaxMixin):
    __tablename__ = 'fsa_medical_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'fsa_medical',
        'inherit_condition': (id == Plan.id),
    }


class FSADependentCarePlan(Plan, GroupMixin, PreTaxMixin):
    __tablename__ = 'fsa_dependent_care_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'fsa_dependent_care',
        'inherit_condition': (id == Plan.id),
    }


class HSAPlan(Plan, GroupMixin, PreTaxMixin):
    __tablename__ = 'hsa_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'hsa',
        'inherit_condition': (id == Plan.id),
    }


class HRAPlan(Plan, GroupMixin, PreTaxMixin):
    __tablename__ = 'hra_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'hra',
        'inherit_condition': (id == Plan.id),
    }


class Employee401KPlan(Plan, GroupMixin, PreTaxMixin):
    __tablename__ = 'employee_401k_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': '401k',
        'inherit_condition': (id == Plan.id),
    }


# Misc. Group
class EAPPlan(Plan, GroupMixin, PostTaxMixin):
    __tablename__ = 'eap_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'eap',
        'inherit_condition': (id == Plan.id),
    }


class LongTermCarePlan(Plan, GroupMixin, PreOrPostTaxMixin):
    __tablename__ = 'long_term_care_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'long_term_care',
        'inherit_condition': (id == Plan.id),
    }


# Supplemental Plans
class CriticalIllnessPlan(Plan, SupplementalMixin, PostTaxMixin):
    __tablename__ = 'cricial_illness_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    payout_amount = db.Column(db.Numeric(9, 2))

    __mapper_args__ = {
        'polymorphic_identity': 'critical_illness',
        'inherit_condition': (id == Plan.id),
    }


class CancerPlan(Plan, SupplementalMixin, PostTaxMixin):
    __tablename__ = 'cancer_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'cancer',
        'inherit_condition': (id == Plan.id),
    }


class AccidentPlan(Plan, SupplementalMixin, PostTaxMixin):
    __tablename__ = 'accident_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'accident',
        'inherit_condition': (id == Plan.id),
    }


class HospitalConfinementPlan(Plan, SupplementalMixin, PostTaxMixin):
    __tablename__ = 'hospital_confinement_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'confinement',
        'inherit_condition': (id == Plan.id),
    }


class ParkingTransitPlan(Plan, SupplementalMixin, PreTaxMixin):
    __tablename__ = 'parking_transit_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'parking_transit',
        'inherit_condition': (id == Plan.id),
    }


class IdentityTheftPlan(Plan, SupplementalMixin, PostTaxMixin):
    __tablename__ = 'identity_theft_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'identity_theft',
        'inherit_condition': (id == Plan.id),
    }


# Plan Premiums
class Premium(Base):
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), index=True)
    plan = db.relationship('Plan')
    # total amount of the premium to be paid to the carrier, making this nullable as the actual
    # amount may not be known until a coverage amount is elected or it may vary with the employee's salary
    amount = db.Column(db.Numeric(9, 2), info={'label': 'Premium'})
    # rate to be multiplied by some part of elected coverage or salary
    rate = db.Column(db.Numeric(6, 2), info={'label': 'Rate'})
    # not null if the premium is tiered on gender
    gender = db.Column(ChoiceType(GENDER_TYPES), info={'label': 'Gender'})
    # not null if the premium is tiered on smoker status
    smoker_status = db.Column(ChoiceType(SMOKER_TYPES), info={'label': 'Smoker Status'})
    # not null if the premium is tiered on age
    age = db.Column(db.Integer, info={'label': 'Age'})
    # not null if the premium is tiered on age bands
    age_banded_tier_id = db.Column(db.ForeignKey('age_banded_tier.id'))
    age_banded_tier = db.relationship('AgeBandedTier', uselist=False)
    # not null if the premium is tiered on family members
    family_tier = db.Column(ChoiceType(FAMILY_TIER_TYPES), info={'label': 'Family Tier'})


class AgeBandedTier(Base):
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), index=True)
    plan = db.relationship('Plan')

    low = db.Column(db.Integer, nullable=False)
    high = db.Column(db.Integer, nullable=True)


class AgeBasedReduction(Base):
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), index=True)
    plan = db.relationship('Plan')

    age = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Integer, nullable=False)


# Eligibility
class EmployeeEligibility(Base):
    full_time_only = db.Column(db.Boolean, default=False)
    minimum_days_employed = db.Column(db.Integer, default=0)


class DependentEligibility(Base):
    eligible = db.Column(db.Boolean, default=False)


class DomesticPartnerEligibility(Base):
    eligible = db.Column(db.Boolean, default=False)


class EnrollmentPeriod(Base):
    year = db.Column(db.Integer)


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
    premium_id = db.Column(db.Integer, db.ForeignKey('premium.id'))
    premium = db.relationship('Premium')
    coverage_amount = db.Column(db.Integer)
