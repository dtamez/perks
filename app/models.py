# -*- coding: utf-8 -*-
# vie:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from datetime import date
from decimal import Decimal
import inflection
import locale

#  from flask_user import SQLAlchemyAdapter, UserManager, UserMixin
from flask_login import UserMixin, AnonymousUserMixin
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
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import widgets

from . import db, login_manager


@as_declarative()
class Base(object):
    """Base class for all models to create a default table name based on the
    class name and an id field.
    """

    @declared_attr
    def __tablename__(cls):
        return inflection.underscore(cls.__name__)

Base.query = db.session.query_property()


# CHOICES
GENDER_TYPES = [
    ('M', 'Male'),
    ('F', 'Female'),
]


MARITAL_STATUS_TYPES = [
    ('single', 'Single'),
    ('married', 'Married'),
    ('divorced', 'Divorced'),
    ('widowed', 'Widowed'),
]


SMOKER_TYPES = [
    ('SM', 'Smoker'),
    ('NS', 'Non Smoker'),
]


BENEFICIARY_TYPES = [
    ('', '----'),
    ('primary', 'Primary'),
    ('contingent', 'Contingent'),
]

DEPENDENT_TYPES = [
    ('husband', 'Husband'),
    ('wife', 'Wife'),
    ('son', 'Son'),
    ('daughter', 'Daughter'),
    ('incapacitated', 'Incapacitated'),
    ('charity', 'Charity'),
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
    ('EO', 'Employee Only'),
    ('ES', 'Employee and Spouse'),
    ('EC', 'Employee and Children'),
    ('EF', 'Employee and Family'),
    ('E1', 'Employee Plus 1'),
    ('E2', 'Employee Plus 2'),
    ('E3', 'Employee Plus 3'),
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
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
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
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    username = db.Column(db.String(50), nullable=False, unique=True, info={'label': 'Username'}, index=True)
    #  password = db.Column(db.String(255), nullable=False, unique=False, info={'label': 'Password'})
    password_hash = db.Column(db.String(128))
    email = db.Column(EmailType, info={'label': 'Email'}, index=True)
    confirmed_at = db.Column(db.DateTime)
    reset_password_token = db.Column(db.String(100), nullable=True, server_default='')
    active = db.Column('is_active', db.Boolean, nullable=False, server_default='0', info={'label': 'May Log In?'})
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)
    label = db.Column(db.Unicode(255), server_default=u'')


class UserRoles(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', ondelete='CASCADE'))


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Dependent(PersonMixin, Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    dependent_type = db.Column(ChoiceType(DEPENDENT_TYPES), info={'label': 'Dependent Type'})
    full_time_student = db.Column(db.Boolean, server_default='0', info={'label': 'Full Time Student?'})
    disabled = db.Column(db.Boolean, server_default='0', info={'label': 'Disabled?'})
    disability_date = db.Column(db.Date, info={'label': 'Disability Date'})
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    address_id = db.Column(db.ForeignKey('address.id'))
    address = db.relationship('Address', uselist=False)


class Beneficiary(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    beneficiary_type = db.Column(ChoiceType(BENEFICIARY_TYPES))
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), index=True)
    plan = db.relationship('Plan')
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    percentage = db.Column(db.Integer, server_default='0')
    btype = db.Column(db.String(50))

    def get_relation(self):
        return ''

    __mapper_args__ = {
        'polymorphic_identity': 'beneficiary',
        'polymorphic_on': btype
    }

    def __repr__(self):
        class_name = type(self).__name__
        return '<{class_name}-{id}, {beneficiary_type}, plan-{plan_id}, employee-{employee_id}, {percentage}%>'.format(
            id=self.id, beneficiary_type=self.beneficiary_type, employee_id=self.employee_id,
            percentage=self.percentage, plan_id=self.plan_id, class_name=class_name)


class DependentBeneficiary(Beneficiary):
    id = db.Column(None, db.ForeignKey('beneficiary.id'), primary_key=True, info={'widget': widgets.HiddenInput()})
    dependent_id = db.Column(db.Integer, db.ForeignKey('dependent.id'))
    dependent = db.relationship('Dependent')

    def get_name(self):
        return '{} {}'.format(self.dependent.first_name, self.dependent.last_name)

    def get_relation(self):
        return self.dependent.dependent_type.value

    __mapper_args__ = {
        'polymorphic_identity': 'dependent',
    }

    def __repr__(self):
        return super(DependentBeneficiary, self).__repr__() + ' dependent-{dependent_id}'.format(
            dependent_id=self.dependent_id)


class EstateBeneficiary(Beneficiary):
    id = db.Column(None, db.ForeignKey('beneficiary.id'), primary_key=True, info={'widget': widgets.HiddenInput()})

    def get_name(self):
        return 'Estate'

    __mapper_args__ = {
        'polymorphic_identity': 'estate',
    }


class SuccessionOfHeirsBeneficiary(Beneficiary):
    id = db.Column(None, db.ForeignKey('beneficiary.id'), primary_key=True, info={'widget': widgets.HiddenInput()})

    def get_name(self):
        return 'Succession of Heirs'

    __mapper_args__ = {
        'polymorphic_identity': 'succession',
    }


class Location(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    code = db.Column(db.String(12), info={'label': 'Code'}, nullable=False)
    description = db.Column(db.String(60), info={'label': 'Description'}, nullable=False)
    effective_date = db.Column(db.Date, nullable=False, info={'label': 'Effective Date'})

    __mapper_args__ = {
        'order_by': code
    }


class Employee(PersonMixin, Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
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

    def get_monthly_salary(self):
        return self.get_annual_salary() / 12

    def get_annual_salary(self):
        if self.salary_mode == 'hourly':
            return self.salary * 40 * 52
        elif self.salary_mode == 'weekly':
            return self.salary * 52
        elif self.salary_mode == 'bi-weekly':
            return self.salary * 26
        elif self.salary_mode == 'semi-monthly':
            return self.salary * 24
        elif self.salary_mode == 'monthly':
            return self.salary * 12
        elif self.salary_mode == 'annually':
            return self.salary


class Carrier(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
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


class GroupMixin(object):
    pass


class SupplementalMixin(object):
    pass


class EmployerContributionMixin(object):
    er_flat_amount_contributed = db.Column(db.Numeric(9, 2), server_default='0',
                                           info={'label': 'Flat Amount Contributed by Employer'})
    er_percentage_contributed = db.Column(db.Numeric(3, 2), server_default='0',
                                          info={'label': 'Percentage Contributed by Employer'})
    er_max_contribution = db.Column(db.Numeric(9, 2), server_default='0',
                                    info={'label': 'Maximum Employer Contribution'})


class PlanPremiumMetaValuesMixin(object):
    salary_chunk_size = db.Column(
        db.Integer, info={'label': 'Premium is based on this portion of salary'})
    coverage_chunk_size = db.Column(
        db.Integer, info={'label': 'Premium is based on this portion of elected coverage'})


class AmountSuppliedElectionMixin(object):

    def get_election_form(self):
            from .forms import AmountInputElectionForm
            return AmountInputElectionForm

    def get_premium_choices(self, chosen_value, employee):
        # TODO: This is a hack, need a better way
        if chosen_value == '|':
            chosen_value = None
        else:
            chosen_value = int(chosen_value)

        min_election, max_election = self.get_min_max_elections()
        if chosen_value:
            chosen_value = int(chosen_value)
        total, er, ee = self.get_monthly_costs(chosen_value)
        return [(min_election, max_election, chosen_value, total, er, ee)]

    def populate_election(self, selection, election, employee):
        if selection == 'DE':
            election.elected = False
            election.premium_id = None
            election.premium = None
            election.amount = 0
            election.total_cost = 0
            election.employee_cost = 0
            election.employer_cost = 0
        else:
            election.elected = False  # only True for BooleanElection types
            election.premium_id = None
            election.premium = None
            election.amount = int(selection)
            total, er, ee = self.get_monthly_costs(election.amount)
            election.total_cost = total
            election.employer_cost = er
            election.employee_cost = ee

    def get_monthly_costs(self, amount):
        total = amount / 12 if amount else 0
        er = self.er_flat_amount_contributed or (total * self.er_percentage_contributed)
        ee = total - er
        return total, er, ee


class PremiumsMixin(object):
    @declared_attr
    def premiums(cls):
        return db.relationship('Premium', cascade="all, delete-orphan", passive_deletes=True)
    premium_matrix = db.Column(db.String(5000), info={'label': "Premium Matrix", 'widget': widgets.TextArea()})


class AmountChosenElectionMixin(PremiumsMixin):

    def get_election_form(self):
            from .forms import AmountChosenElectionForm
            return AmountChosenElectionForm

    def get_premium_choices(self, chosen_value, employee):
        #  TODO: Do we stil need to call this method when we already have the premium id?
        amt, premium_id = chosen_value.split('|') if chosen_value and chosen_value != 'DE' else ('', '')
        choices = []
        filters = [Premium.plan_id == self.id]
        today = date.today()
        born = self._get_dob(employee)
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

        if prem.age_band_low or prem.age_band_high:
            q = q.filter(and_(Premium.age_band_low <= age, Premium.age_band_high >= age))

        if prem.payout_amount:
            prems = q.all()
            selected = False
            for prem in prems:
                total, er, ee = self.get_monthly_costs(prem.amount, prem.payout_amount)
                choices.append(('{}|{}'.format(prem.payout_amount, prem.id),
                                prem.payout_amount, selected,
                                locale.currency(total, grouping=True),
                                locale.currency(er, grouping=True),
                                locale.currency(ee, grouping=True)))
            choices.append(('DE', 'Decline', chosen_value is None, '', '', ''))
            return choices
        else:
            # now get the one premium that applies to our employee
            prem = q.one()
            selected = False
            for coverage in range(self.min_election, self.max_election + 1, self.increments):
                total, er, ee = self.get_monthly_costs(prem.rate, coverage)
                choices.append(('{}|{}'.format(coverage, prem.id),
                                coverage, selected,
                                locale.currency(total, grouping=True),
                                locale.currency(er, grouping=True),
                                locale.currency(ee, grouping=True)))
            choices.append(('DE', 'Decline', chosen_value is None, '', '', ''))
            return choices

    def populate_election(self, selection, election, employee):
        if selection == 'DE':
            election.elected = False
            election.premium_id = None
            election.premium = None
            election.amount = 0
            election.total_cost = 0
            election.employee_cost = 0
            election.employer_cost = 0
        else:
            election.elected = False  # only True for BooleanElection types
            amt, premium_id = selection.split('|')
            election.premium_id = int(premium_id)
            election.premium = Premium.query.get(election.premium_id)
            election.amount = Decimal(amt)
            if election.premium.payout_amount:
                total, er, ee = self.get_monthly_costs(election.premium.amount, election.amount)
            else:
                total, er, ee = self.get_monthly_costs(election.premium.rate, election.amount)
            election.total_cost = total
            election.employer_cost = er
            election.employee_cost = ee


class TieredElectionMixin(PremiumsMixin):

    def get_election_form(self):
            from .forms import TieredElectionForm
            return TieredElectionForm

    def get_premium_choices(self, chosen_value, employee):
        tier, premium_id = chosen_value.split('|') if (chosen_value and chosen_value != 'DE' and
                                                       chosen_value != 'None') else ('', '')
        if premium_id:
            premium_id = int(premium_id)
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

        if prem.age_band_low:
            q = q.filter(and_(Premium.age_band_low <= age, Premium.age_band_high >= age))

        # Narrow it down to just the tiers that apply
        choices = []
        for premium in q.all():
            total, er, ee = self.get_monthly_costs(premium.amount)
            choices.append(('{}|{}'.format(premium.family_tier.code, premium.id),
                            premium.family_tier.value, premium.id == premium_id,
                            locale.currency(total, grouping=True),
                            locale.currency(er, grouping=True),
                            locale.currency(ee, grouping=True)))
        choices.append(('DE', 'Decline', chosen_value is None, '', '', ''))
        return choices

    def populate_election(self, selection, election, employee):
        if selection == 'DE':
            election.elected = False
            election.premium_id = None
            election.premium = None
            election.amount = 0
            election.total_cost = 0
            election.employee_cost = 0
            election.employer_cost = 0
        else:
            election.elected = False  # only True for BooleanElection types
            tier, premium_id = selection.split('|')
            election.premium_id = int(premium_id)
            election.premium = Premium.query.get(election.premium_id)
            election.amount = 0
            total, er, ee = self.get_monthly_costs(election.premium.amount)
            election.total_cost = total
            election.employer_cost = er
            election.employee_cost = ee

    def get_monthly_costs(self, amount):
        total = amount
        er = self.er_flat_amount_contributed or (total * self.er_percentage_contributed)
        ee = total - er
        return total, er, ee


class BooleanElectionMixin(PremiumsMixin):

    def get_premium_choices(self, chosen_value, employee):
        choices = []
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

        if prem.age_band_low or prem.age_band_high:
            q = q.filter(and_(Premium.age_band_low <= age, Premium.age_band_high >= age))
        # now get the one premium that applies to our employee
        prem = q.one()
        total, er, ee = self.get_monthly_costs(prem, employee)
        selected = chosen_value  # should be True or False (election.elected)
        choices.append((prem.id, 'Enroll', selected,
                        locale.currency(total, grouping=True),
                        locale.currency(er, grouping=True),
                        locale.currency(ee, grouping=True)))
        choices.append(('DE', 'Decline', not selected, '', '', ''))
        return choices

    def populate_election(self, selection, election, employee):
        if selection == 'DE':
            election.elected = False
            election.premium_id = None
            election.premium = None
            election.amount = 0
            election.total_cost = 0
            election.employee_cost = 0
            election.employer_cost = 0
        else:
            election.elected = True
            election.premium_id = int(selection)
            election.premium = Premium.query.get(election.premium_id)
            election.amount = 0
            total, er, ee = self.get_monthly_costs(election.premium, employee)
            election.total_cost = total
            election.employer_cost = er
            election.employee_cost = ee

    def get_election_form(self):
        from .forms import BooleanElectionForm
        return BooleanElectionForm


class IRSLimits(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    max_fsa_medical_contribution = db.Column(db.Numeric(9, 2))
    max_fsa_dependent_care_contribution = db.Column(db.Numeric(9, 2))
    max_hsa_individual_contribution = db.Column(db.Numeric(9, 2))
    max_hsa_family_contribution = db.Column(db.Numeric(9, 2))
    max_hsa_family_over_55_contribution = db.Column(db.Numeric(9, 2))
    max_401k_salary_deferal = db.Column(db.Numeric(9, 2))
    max_401k_salary_deferal_over_50 = db.Column(db.Numeric(9, 2))


class Plan(Base, EmployerContributionMixin, PlanPremiumMetaValuesMixin):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    plantype = db.Column(db.String(50), info={'label': 'Plan Type'})
    code = db.Column(db.String(10), info={'label': 'Code'})
    name = db.Column(db.Unicode(70), nullable=False, info={'label': 'Name'})
    description = db.Column(db.String(250), nullable=False, info={'label': ''})
    special_instructions = db.Column(db.String(250), info={'label': ''})
    active = db.Column('is_active', db.Boolean, nullable=False, index=True, server_default='1',
                       info={'label': 'Plan is active?'})
    carrier_id = db.Column(db.ForeignKey('carrier.id'))
    carrier = db.relationship('Carrier', uselist=False, info={'label': 'Caarrier'})
    website = db.Column(URLType, info={'label': 'Website'})
    cust_service_phone = db.Column(PhoneNumberType, info={'label': 'Customer Service Phone'})
    required_plan_id = db.Column(db.ForeignKey('plan.id'))
    required_plan = db.relationship('Plan', remote_side=[id], info={'label': 'Required plan'})

    __mapper_args__ = {
        'polymorphic_on': plantype,
        'order_by': name
    }


# Core plans
class MedicalPlan(Plan, CoreMixin, PreOrPostTaxMixin, TieredElectionMixin):
    __tablename__ = 'medical_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True, info={'widget': widgets.HiddenInput()})

    __mapper_args__ = {
        'polymorphic_identity': 'medical',
        'inherit_condition': (id == Plan.id),
    }


class DentalPlan(Plan, CoreMixin, PreOrPostTaxMixin, TieredElectionMixin):
    __tablename__ = 'dental_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'dental',
        'inherit_condition': (id == Plan.id),
    }


class VisionPlan(Plan, CoreMixin, PreOrPostTaxMixin, TieredElectionMixin):
    __tablename__ = 'vision_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'vision',
        'inherit_condition': (id == Plan.id),
    }


class MedicalDentalBundlePlan(Plan, CoreMixin, PreOrPostTaxMixin, TieredElectionMixin):
    __tablename__ = 'medical_dental_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'medical_dental',
        'inherit_condition': (id == Plan.id),
    }


class MedicalVisionBundlePlan(Plan, CoreMixin, PreOrPostTaxMixin, TieredElectionMixin):
    __tablename__ = 'medical_vision_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'medical_vision',
        'inherit_condition': (id == Plan.id),
    }


class MedicalDentalVisionBundlePlan(Plan, CoreMixin, PreOrPostTaxMixin, TieredElectionMixin):
    __tablename__ = 'medical_dental_vision_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'medical_dental_vision',
        'inherit_condition': (id == Plan.id),
    }


class DentalVisionBundlePlan(Plan, CoreMixin, PreOrPostTaxMixin, TieredElectionMixin):
    __tablename__ = 'dental_vision_bundle_plan'
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'dental_vision',
        'inherit_condition': (id == Plan.id),
    }


# Group Plans
# Life
class LifeMixin(object):

    @declared_attr
    def beneficiaries(cls):
        return db.relationship('Beneficiary', uselist=True, single_parent=True,
                               back_populates='plan', cascade="all, delete-orphan")


class AgeBasedMixin(object):
    age_based_reduction_matrix = db.Column(db.String(5000),
                                           info={'label': "Age Based Reduction Matrix", 'widget': widgets.TextArea()})


class BasicLifePlan(Plan, GroupMixin, PostTaxMixin, BooleanElectionMixin, LifeMixin, AgeBasedMixin):
    # has a composite premium, 100% employer paid
    # but the cost is figured as rate * (salary / 1000) per month
    __tablename__ = 'life_add_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    # benefits
    multiple_of_salary_paid = db.Column(db.Numeric(4, 2), info={'label': 'Multiple of Salary Paid'})
    min_benefit = db.Column(db.Numeric(9, 2), info={'label': 'Minimum Benefit'})
    max_benefit = db.Column(db.Numeric(9, 2), info={'label': 'Maximum Benefit'})
    spouse_benefit = db.Column(db.Numeric(9, 2), info={'label': 'Spouse Benefit'})
    child_benefit = db.Column(db.Numeric(9, 2), info={'label': 'Child Benefit'})
    guarantee_issue = db.Column(db.Numeric(9, 2), info={'label': 'Guarantee Issue'})
    age_based_reductions = db.relationship('AgeBasedReduction', back_populates="plan")
    addl_salary_multiple_accidental_death = db.Column(
        db.Numeric(4, 2), info={'label': 'Additional Multiple of Salary Paid for Accidental Death'})
    addl_salary_multiple_accidental_dismemberment = db.Column(
        db.Numeric(4, 2), info={'label': 'Additional Multiple of Salary Paid for Accidental Dismemberment'})

    def get_monthly_costs(self, premium, employee):
        total = (premium.rate * (employee.get_annual_salary() / 1000))
        er = self.er_flat_amount_contributed or (total * self.er_percentage_contributed)
        ee = total - er
        return total, er, ee

    __mapper_args__ = {
        'polymorphic_identity': 'life_add',
        'inherit_condition': (id == Plan.id),
    }


class VoluntaryLifePlan(Plan, GroupMixin, PostTaxMixin, AmountChosenElectionMixin, LifeMixin):
    __tablename__ = 'voluntary_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    increments = db.Column(db.Integer, info={'label': 'Election Amount Increments'})
    min_election = db.Column(db.Numeric(9, 2), info={'label': 'Minimum Election'})
    max_election = db.Column(db.Numeric(9, 2), info={'label': 'Maximum Election'})
    # benefits
    age_based_reductions = db.relationship('AgeBasedReduction', back_populates="plan")
    guarantee_issue = db.Column(db.Numeric(9, 2), info={'label': 'Guarantee Issue'})
    # optional ADD
    addl_salary_multiple_accidental_death = db.Column(
        db.Numeric(4, 2), info={'label': 'Additional Multiple of Salary Paid for Accidental Death'})
    addl_salary_multiple_accidental_dismemberment = db.Column(
        db.Numeric(4, 2), info={'label': 'Additional Multiple of Salary Paid for Accidental Dismemberment'})
    age_based_reductions = db.relationship('AgeBasedReduction', back_populates="plan")

    def sort_value(self):
        return 1

    def get_monthly_costs(self, rate, amount):
        total = (rate * (amount / 1000))
        er = (self.er_flat_amount_contributed or (total * self.er_percentage_contributed))
        ee = total - er
        return total, er, ee

    __mapper_args__ = {
        'polymorphic_identity': 'voluntary_life',
        'inherit_condition': (id == Plan.id),
    }

    def _get_dob(self, employee):
        return employee.dob


class SpouseVoluntaryLifePlan(VoluntaryLifePlan):
    __tablename__ = 'spouse_voluntary_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    use_employee_age_for_spouse = db.Column(db.Boolean, info={'label': "Use Employee's Age for Spouse's Age"})

    def sort_value(self):
        return 2

    __mapper_args__ = {
        'polymorphic_identity': 'spouse_voluntary_life',
        'inherit_condition': (id == Plan.id),
    }

    def _get_dob(self, employee):
        return employee.dob if self.use_employee_age_for_spouse else employee.spouse_dob


class ChildVoluntaryLifePlan(VoluntaryLifePlan):
    __tablename__ = 'child_voluntary_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    def sort_value(self):
        return 3

    __mapper_args__ = {
        'polymorphic_identity': 'child_voluntary_life',
        'inherit_condition': (id == Plan.id),
    }


class StandaloneADDPlan(Plan, GroupMixin, PostTaxMixin, AmountChosenElectionMixin, LifeMixin):
    __tablename__ = 'standalone_add_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    increments = db.Column(db.Integer, info={'label': 'Election Amount Increments'})
    min_election = db.Column(db.Numeric(9, 2), info={'label': 'Minimum Election'})
    max_election = db.Column(db.Numeric(9, 2), info={'label': 'Maximum Election'})
    # benefits

    def _get_dob(self, employee):
        return employee.dob

    def get_monthly_costs(self, rate, amount):
        total = (rate * (amount / 1000))
        er = (self.er_flat_amount_contributed or (total * self.er_percentage_contributed))
        ee = total - er
        return total, er, ee

    def sort_value(self):
        return 1

    __mapper_args__ = {
        'polymorphic_identity': 'standalone_add',
        'inherit_condition': (id == Plan.id),
    }


class SpouseStandaloneADDPlan(StandaloneADDPlan):
    __tablename__ = 'spouse_standalone_add_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    def sort_value(self):
        return 2

    __mapper_args__ = {
        'polymorphic_identity': 'spouse_standalone_add',
        'inherit_condition': (id == Plan.id),
    }


class ChildStandaloneADDPlan(StandaloneADDPlan):
    __tablename__ = 'child_standalone_add_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    def sort_value(self):
        return 3

    __mapper_args__ = {
        'polymorphic_identity': 'child_standalone_add',
        'inherit_condition': (id == Plan.id),
    }


class WholeLifePlan(Plan, GroupMixin, PostTaxMixin, AmountChosenElectionMixin, LifeMixin, AgeBasedMixin):
    __tablename__ = 'whole_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    # benefits
    spouse_benefit = db.Column(db.Numeric(9, 2), info={'label': 'Spouse Benefit'})
    child_benefit = db.Column(db.Numeric(9, 2), info={'label': 'Child Benefit'})

    def get_monthly_costs(self, amount, payout_amount):
        total = amount
        er = (self.er_flat_amount_contributed or (total * self.er_percentage_contributed))
        ee = total - er
        return total, er, ee

    def _get_dob(self, employee):
        return employee.dob

    def sort_value(self):
        return 1

    __mapper_args__ = {
        'polymorphic_identity': 'whole_life',
        'inherit_condition': (id == Plan.id),
    }


class SpouseWholeLifePlan(WholeLifePlan):
    __tablename__ = 'spouse_whole_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    def sort_value(self):
        return 2

    __mapper_args__ = {
        'polymorphic_identity': 'spouse_whole_life',
        'inherit_condition': (id == Plan.id),
    }


class ChildWholeLifePlan(WholeLifePlan):
    __tablename__ = 'child_whole_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    def sort_value(self):
        return 3

    __mapper_args__ = {
        'polymorphic_identity': 'child_whole_life',
        'inherit_condition': (id == Plan.id),
    }


class UniversalLifePlan(Plan, GroupMixin, PostTaxMixin, AmountChosenElectionMixin, LifeMixin, AgeBasedMixin):
    __tablename__ = 'universal_life_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    # rates
    # benefits
    spouse_benefit = db.Column(db.Numeric(9, 2), info={'label': 'Spouse Benefit'})
    child_benefit = db.Column(db.Numeric(9, 2), info={'label': 'Child Benefit'})

    def get_monthly_costs(self, rate, amount):
        total = (rate * (amount / 1000))
        er = (self.er_flat_amount_contributed or (total * self.er_percentage_contributed))
        ee = total - er
        return total, er, ee

    __mapper_args__ = {
        'polymorphic_identity': 'universal_life',
        'inherit_condition': (id == Plan.id),
    }


# LTD
class LTDPlan(Plan, GroupMixin, PreOrPostTaxMixin, BooleanElectionMixin):
    __tablename__ = 'ltd_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    # has fixed premium based on some formula from the carrier across all employees
    # monthly benefit is some percent of one month's salary
    # but the cost is figured as rate * (monthly_benefit / 1000) per month
    max_monthly_benefit = db.Column(db.Numeric(9, 2), nullable=False, info={'label': 'Maximum Monthly Benefit'})
    percentage_of_salary_paid = db.Column(db.Numeric(3, 2), nullable=False, info={'label': 'Benefit Percentage'})

    def get_monthly_costs(self, premium, employee):
        total = (premium.rate * self.percentage_of_salary_paid * (employee.get_monthly_salary() / 1000))
        er = self.er_flat_amount_contributed or (total * self.er_percentage_contributed)
        ee = total - er
        return total, er, ee

    __mapper_args__ = {
        'polymorphic_identity': 'ltd',
        'inherit_condition': (id == Plan.id),
    }


class LTDVoluntaryPlan(LTDPlan):
    # has age banded rates (e.g. 25 - 34 = 0.05, 35 - 39 = 0.06)
    # so monthly premium for age 37 at $70,000 = 0.06 * 70 or $4.20/month
    # rate * (amount_chosen / 1000) per month
    __tablename__ = 'ltd_voluntary_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'ltd_voluntary',
        'inherit_condition': (id == Plan.id),
    }


# STD
class STDPlan(Plan, GroupMixin, PostTaxMixin, BooleanElectionMixin):
    # composite rate * (weekly_benefit / $10)
    __tablename__ = 'std_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    max_weekly_benefit = db.Column(db.Numeric(9, 2), nullable=False, info={'label': 'Maximum Weekly Benefit'})
    percentage_of_salary_paid = db.Column(db.Numeric(3, 2), nullable=False, info={'label': 'Benefit Percentage'})

    def get_monthly_costs(self, premium, employee):
        total = (premium.rate * self.percentage_of_salary_paid * (employee.get_monthly_salary() / 2000))
        er = self.er_flat_amount_contributed or (total * self.er_percentage_contributed)
        ee = total - er
        return total, er, ee

    __mapper_args__ = {
        'polymorphic_identity': 'std',
        'inherit_condition': (id == Plan.id),
    }


class STDVoluntaryPlan(Plan, GroupMixin, PostTaxMixin, BooleanElectionMixin):
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

    def get_monthly_costs(self, premium, employee):
        total = (premium.rate * self.percentage_of_salary_paid * (employee.get_monthly_salary() / 2000))
        er = self.er_flat_amount_contributed or (total * self.er_percentage_contributed)
        ee = total - er
        return total, er, ee

    __mapper_args__ = {
        'polymorphic_identity': 'std_voluntary',
        'inherit_condition': (id == Plan.id),
    }


# Savings Plans
class FSAMedicalPlan(Plan, GroupMixin, PreTaxMixin, AmountSuppliedElectionMixin):
    __tablename__ = 'fsa_medical_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    min_contribution = db.Column(db.Numeric(9, 2), nullable=False, info={'label': 'Minimum Contribution'})

    def get_min_max_elections(self):
        limits = IRSLimits.query.first()
        return self.min_contribution, limits.max_fsa_medical_contribution

    __mapper_args__ = {
        'polymorphic_identity': 'fsa_medical',
        'inherit_condition': (id == Plan.id),
    }


class FSADependentCarePlan(FSAMedicalPlan):
    __tablename__ = 'fsa_dependent_care_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    def get_min_max_elections(self):
        limits = IRSLimits.query.first()
        return self.min_contribution, limits.max_fsa_dependent_care_contribution

    __mapper_args__ = {
        'polymorphic_identity': 'fsa_dependent_care',
        'inherit_condition': (id == Plan.id),
    }


class HSAPlan(Plan, GroupMixin, PreTaxMixin, AmountSuppliedElectionMixin):
    __tablename__ = 'hsa_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    min_contribution = db.Column(db.Numeric(9, 2), nullable=False, info={'label': 'Minimum Contribution'})

    def get_min_max_elections(self):
        limits = IRSLimits.query.first()
        # TODO: Where do family and individual contributions come into play?
        return self.min_contribution, limits.max_hsa_individual_contribution

    __mapper_args__ = {
        'polymorphic_identity': 'hsa',
        'inherit_condition': (id == Plan.id),
    }


class HRAPlan(Plan, GroupMixin, PreTaxMixin, BooleanElectionMixin):
    __tablename__ = 'hra_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    def get_monthly_costs(self, premium, employee):
        total = premium.amount
        er = self.er_flat_amount_contributed or (total * self.er_percentage_contributed)
        ee = total - er
        return total, er, ee

    __mapper_args__ = {
        'polymorphic_identity': 'hra',
        'inherit_condition': (id == Plan.id),
    }


class Employee401KPlan(Plan, GroupMixin, PreTaxMixin, AmountSuppliedElectionMixin):
    __tablename__ = 'employee_401k_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)
    employer_percent_matched = db.Column(db.Numeric(3, 2), nullable=False,
                                         info={'label': 'Employer Percent Match'})
    employer_max_contribution = db.Column(db.Numeric(9, 2), nullable=False,
                                          info={'label': 'Employer Maximum Contribution'})
    min_contribution = db.Column(db.Numeric(9, 2), nullable=False,
                                 info={'label': 'Minimum Contribution'})

    def get_min_max_elections(self):
        limits = IRSLimits.query.first()
        return self.min_contribution, limits.max_401k_salary_deferal

    __mapper_args__ = {
        'polymorphic_identity': '401k',
        'inherit_condition': (id == Plan.id),
    }


# Misc. Group
class EAPPlan(Plan, GroupMixin, PostTaxMixin, BooleanElectionMixin):
    # one price per month
    __tablename__ = 'eap_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    def get_monthly_costs(self, premium, employee):
        total = premium.amount
        er = self.er_flat_amount_contributed or (total * self.er_percentage_contributed)
        ee = total - er
        return total, er, ee

    __mapper_args__ = {
        'polymorphic_identity': 'eap',
        'inherit_condition': (id == Plan.id),
    }


class LongTermCarePlan(Plan, GroupMixin, PreOrPostTaxMixin, TieredElectionMixin):
    __tablename__ = 'long_term_care_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'long_term_care',
        'inherit_condition': (id == Plan.id),
    }


# Supplemental Plans
class CriticalIllnessPlan(Plan, SupplementalMixin, PostTaxMixin, TieredElectionMixin):
    __tablename__ = 'cricial_illness_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    payout_amount = db.Column(db.Numeric(9, 2), info={'label': 'Payout Amount'})

    def _get_dob(self, employee):
        return employee.dob

    __mapper_args__ = {
        'polymorphic_identity': 'critical_illness',
        'inherit_condition': (id == Plan.id),
    }


class CancerPlan(Plan, SupplementalMixin, PostTaxMixin, TieredElectionMixin):
    __tablename__ = 'cancer_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'cancer',
        'inherit_condition': (id == Plan.id),
    }


class AccidentPlan(Plan, SupplementalMixin, PostTaxMixin, TieredElectionMixin):
    __tablename__ = 'accident_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'accident',
        'inherit_condition': (id == Plan.id),
    }


class HospitalConfinementPlan(Plan, SupplementalMixin, PostTaxMixin, TieredElectionMixin):
    __tablename__ = 'hospital_confinement_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'confinement',
        'inherit_condition': (id == Plan.id),
    }


class ParkingTransitPlan(Plan, SupplementalMixin, PreTaxMixin, BooleanElectionMixin):
    # one price per month
    __tablename__ = 'parking_transit_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    def get_monthly_costs(self, premium, employee):
        total = premium.amount
        er = self.er_flat_amount_contributed or (total * self.er_percentage_contributed)
        ee = total - er
        return total, er, ee

    __mapper_args__ = {
        'polymorphic_identity': 'parking_transit',
        'inherit_condition': (id == Plan.id),
    }


class IdentityTheftPlan(Plan, SupplementalMixin, PostTaxMixin, TieredElectionMixin):
    __tablename__ = 'identity_theft_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'identity_theft',
        'inherit_condition': (id == Plan.id),
    }


class OtherPlan(Plan, SupplementalMixin, PostTaxMixin, TieredElectionMixin):
    __tablename__ = 'other_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'other',
        'inherit_condition': (id == Plan.id),
    }


# Plan Premiums
class Premium(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id', ondelete='CASCADE'), index=True)
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
    # tiered on age_bands
    age_band_low = db.Column(db.Integer)
    age_band_high = db.Column(db.Integer)
    # not null if the premium is tiered on family members
    family_tier = db.Column(ChoiceType(FAMILY_TIER_TYPES), info={'label': 'Family Tier'})
    # for term life
    payout_amount = db.Column(db.Integer)


class AgeBasedReduction(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id', ondelete='CASCADE'), index=True)
    plan = db.relationship('Plan')

    age = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Integer, nullable=False)


# Eligibility
class EmployeeEligibility(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    full_time_only = db.Column(db.Boolean, default=False)
    minimum_days_employed = db.Column(db.Integer, default=0)


class DependentEligibility(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    eligible = db.Column(db.Boolean, default=False)


class DomesticPartnerEligibility(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    eligible = db.Column(db.Boolean, default=False)


class EnrollmentPeriod(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    year = db.Column(db.Integer)


class Enrollment(Base):
    """A collection of choices an employee makes during enrollment"""
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), index=True)
    employee = db.relationship('Employee', uselist=False)
    life_event = db.Column(ChoiceType(LIFE_EVENT_TYPES), info={'label': 'Life Event'})
    elections = db.relationship('Election', backref=backref('enrollment', single_parent=True,
                                                            cascade="all, delete-orphan"))
    enrollment_period_id = db.Column(db.Integer, db.ForeignKey('enrollment_period.id'))
    enrollment_period = db.relationship('EnrollmentPeriod')


class Election(Base):
    id = db.Column(db.Integer, primary_key=True, info={'widget': widgets.HiddenInput()})
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollment.id'))
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), index=True)
    plan = db.relationship('Plan')
    premium_id = db.Column(db.Integer, db.ForeignKey('premium.id'))
    premium = db.relationship('Premium')
    amount = db.Column(db.Integer)
    elected = db.Column(db.Boolean)
    total_cost = db.Column(db.Numeric(6, 2))
    employer_cost = db.Column(db.Numeric(6, 2))
    employee_cost = db.Column(db.Numeric(6, 2))
