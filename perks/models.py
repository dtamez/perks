# -*- cgneding: utf-8 -*-
from flask_user import SQLAlchemyAdapter, UserManager, UserMixin
import inflection
from sqlalchemy_utils import (
    ChoiceType,
    EmailType,
    #  PasswordType,
    PhoneNumberType,
    ScalarListType,
    URLType,
)
from sqlalchemy.ext.declarative import (
    as_declarative,
    declared_attr,
)

from . import app, db, db_session


@as_declarative()
class Base(object):
    """Base class for all models to create a default table name based on the
    class name and an id field.
    """

    @declared_attr
    def __tablename__(cls):
        return inflection.underscore(cls.__name__)

    id = db.Column(db.Integer(), primary_key=True)

Base.query = db_session.query_property()


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


PRICING_TYPES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
    ('stanard', 'Standard'),
    ('platinum', 'Platinum'),
]


TIER_TYPES = [
    ('EO', 'Employee Only'),
    ('EC', 'Employee and Children'),
    ('ES', 'Employee and Spouse'),
    ('EF', 'Employee and Family'),
    ('E1', 'Employee Plus 1'),
    ('E2', 'Employee Plus 2'),
    ('E3', 'Employee Plus 3'),
]


PAYOUT_TYPES = [
    ('flat_rate', 'Flat Rate'),
    ('benefit_multiplier', 'Benefit Multiplier'),
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
    street_1 = db.Column(db.Unicode(100), nullable=False)
    street_2 = db.Column(db.Unicode(100))
    city = db.Column(db.Unicode(100), nullable=False)
    state = db.Column(ChoiceType(STATES))
    zip_code = db.Column(db.Unicode(10), nullable=False)


# Models
# PEOPLE
class PersonMixin(object):
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    middle_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    ssn = db.Column(db.Unicode(11), nullable=False)
    dob = db.Column(db.Date(), nullable=False)
    gender = db.Column(ChoiceType(GENDER_TYPES))
    marital_status = db.Column(ChoiceType(MARITAL_STATUSES))
    smoker_type = db.Column(ChoiceType(SMOKER_TYPES))

    @declared_attr
    def address_id(cls):
        return db.Column(db.Integer, db.ForeignKey(
            'address.id'))


class User(UserMixin, Base):
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, unique=True)

    email = db.Column(EmailType())
    confirmed_at = db.Column(db.DateTime())
    reset_password_token = db.Column(db.String(100), nullable=False,
                                     server_default='')
    active = db.Column('is_active', db.Boolean(), nullable=False,
                       server_default='0')

    roles = db.relationship('Role', secondary='user_roles',
                            backref=db.backref('users', lazy='dynamic'))


class Role(Base):
    name = db.Column(db.String(50), nullable=False, server_default=u'',
                     unique=True)
    label = db.Column(db.Unicode(255), server_default=u'')


class UserRoles(Base):
    user_id = db.Column(db.Integer(),
                        db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(),
                        db.ForeignKey('role.id', ondelete='CASCADE'))


db_adapter = SQLAlchemyAdapter(db, User)
user_manager = UserManager(db_adapter, app)


class Dependent(PersonMixin, Base):
    dependent_type = db.Column(ChoiceType(DEPENDENT_TYPES))
    full_time_student = db.Column(db.Boolean(), server_default='0')
    disabled = db.Column(db.Boolean(), server_default='0')
    disability_date = db.Column(db.Date())
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    address_id = db.Column(db.ForeignKey('address.id'))
    address = db.relationship('Address', uselist=False)


class Beneficiary(PersonMixin, Base):
    beneficiary_type = db.Column(ChoiceType(BENEFICIARY_TYPES))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))


class Location(Base):
    code = db.Column(db.String(12))
    description = db.Column(db.String(60))
    effective_date = db.Column(db.Date(), nullable=False)


class Employee(PersonMixin, Base):
    user = db.relationship('User', uselist=False)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    hire_date = db.Column(db.Date(), nullable=False)
    effective_date = db.Column(db.Date(), nullable=False)
    termination_date = db.Column(db.Date())
    employee_number = db.Column(db.Unicode(25))
    beneficiaries = db.relationship('Beneficiary', uselist=True,
                                    backref='employee')
    dependents = db.relationship('Dependent', uselist=True, backref='employee')
    group_id = db.Column(db.String(50), nullable=False)
    sub_group_id = db.Column(db.String(50), nullable=False)
    sub_group_effective_date = db.Column(db.Date(), nullable=False)
    salary_mode = db.Column(ChoiceType(SALARY_MODE_TYPES))
    salary_effective_date = db.Column(db.Date(), nullable=False)
    salary = db.Column(db.Numeric(9, 2), nullable=False)
    phone = db.Column(PhoneNumberType())
    alternate_phone = db.Column(PhoneNumberType())
    emergency_contact_phone = db.Column(PhoneNumberType())
    emergency_contact_name = db.Column(db.String())
    emergency_contact_relationship = db.Column(db.String())
    location_id = db.Column(db.ForeignKey('location.id'))
    location = db.relationship('Location', uselist=False)
    address_id = db.Column(db.ForeignKey('address.id'))
    address = db.relationship('Address', uselist=False)


class Carrier(Base):
    name = db.Column(db.Unicode(50), nullable=False)
    phone = db.Column(PhoneNumberType())
    api_endpoint = db.Column(db.Unicode(200), nullable=False)

    __mapper_args__ = {
        "order_by": name
    }


# PLANS
class CoreMixin(object):

    @declared_attr
    def plan_termination_timing_type_id(cls):
        return db.Column(ChoiceType(PLAN_TERMINATION_TIMING_TYPES))

    group_number = db.Column(db.Unicode(24), nullable=False)
    original_effective_date = db.Column(db.Date())
    renewal_date = db.Column(db.Date())
    existing = db.Column(db.Boolean(), nullable=False)
    list_billed = db.Column(db.Boolean())
    doctor_selection_required = db.Column(db.Boolean())
    account_rep_name = db.Column(db.Unicode(40))
    cobra_eligible = db.Column(db.Boolean(), nullable=False)
    pre_tax = db.Column(db.Boolean(), nullable=False)


class GroupMixin(object):
    minimum_benefit = db.Column(db.Numeric(6, 2), nullable=False)
    maximum_benefit = db.Column(db.Numeric(6, 2), nullable=False)


class SupplementalMixin(object):
    pass


class Plan(Base):
    plantype = db.Column(db.String(50))
    code = db.Column(db.String(10))
    name = db.Column(db.Unicode(20))
    public_name = db.Column(db.Unicode(30))
    cust_service_phone = db.Column(PhoneNumberType())
    website = db.Column(URLType)
    not_available_in = db.Column(ScalarListType())

    @declared_attr
    def pricing_type_id(cls):
        return db.Column(ChoiceType(PRICING_TYPES))

    __mapper_args__ = {
        'polymorphic_on': plantype
    }


class MedicalPlan(Plan, CoreMixin):
    __tablename__ = 'medical_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    self_funded = db.Column(db.Boolean(), nullable=False)
    carrier_id = db.Column(db.ForeignKey('carrier.id'))
    carrier = db.relationship('Carrier', uselist=False)

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
    bundled_with_medical = db.Column(db.Boolean(), nullable=False,
                                     default=False)
    bundled_with_vision = db.Column(db.Boolean(), nullable=False,
                                    default=False)
    bundled_with_id = db.Column(db.ForeignKey('plan.id'))
    bundled_with_plan = db.relationship('Plan',
                                        foreign_keys=[bundled_with_id])
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
    bundled_with_medical = db.Column(db.Boolean(), nullable=False,
                                     default=False)
    bundled_with_dental = db.Column(db.Boolean(), nullable=False,
                                    default=False)
    bundled_with_id = db.Column(db.ForeignKey('plan.id'))
    bundled_with_plan = db.relationship('Plan',
                                        foreign_keys=[bundled_with_id])

    __mapper_args__ = {
        'polymorphic_identity': 'vision',
        'inherit_condition': (id == Plan.id),
    }


class EAPPlan(Plan, GroupMixin):
    __tablename__ = 'eap_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'eap',
        'inherit_condition': (id == Plan.id),
    }


class LTDPlan(Plan, GroupMixin):
    __tablename__ = 'ltd_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'ltd',
        'inherit_condition': (id == Plan.id),
    }


class STDPlan(Plan, GroupMixin):
    __tablename__ = 'std_plan'
    __table_args__ = {'extend_existing': True}
    id = db.Column(None, db.ForeignKey('plan.id'), primary_key=True)

    payout_interval = db.Column(ChoiceType(PAYOUT_TYPES))
    max_weekly_benefit = db.Column(db.Numeric(6, 2), nullable=False)
    max_monthly_benefit = db.Column(db.Numeric(6, 2), nullable=False)
    benefit_percentage = db.Column(db.Numeric(6, 2), nullable=False)
    mandatory_in_states = db.Column(ScalarListType())

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
    __tablename__ = 'employee_401k_plan'
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
class AgeBandedPremium(Base):
    low = db.Column(db.Integer(), nullable=False)
    high = db.Column(db.Integer(), nullable=False)
    premium = db.Column(db.Numeric(6, 2), nullable=False)
    plan_id = db.Column(db.ForeignKey('plan.id'))
    plan = db.relationship('Plan', foreign_keys=[plan_id])


class PlanTierPremium(Base):
    """Prices for all plans."""
    plan_id = db.Column(None, db.ForeignKey('plan.id'))
    plan = db.relationship('Plan', foreign_keys=[plan_id])
    tier_type = db.Column(ChoiceType(TIER_TYPES))
    premium = db.Column(db.Numeric(6, 2), nullable=False)
    employer_portion = db.Column(db.Numeric(6, 2), nullable=False)
    employee_portion = db.Column(db.Numeric(6, 2), nullable=False)
    flat_amount = db.Column(db.Numeric(6, 2))
    multiplier = db.Column(db.Numeric(3, 2))


# Eligibility
class EmployeeEligibility(Base):
    full_time_only = db.Column(db.Boolean(), default=False)
    minimum_days_employed = db.Column(db.Integer(), default=0)


class DependentEligibility(Base):
    eligible = db.Column(db.Boolean(), default=False)


class DomesticPartnerEligibility(Base):
    eligible = db.Column(db.Boolean(), default=False)


# Payroll
#  class WeeklyPayroll(Base):
    #  weekday = db.Column(ChoiceType(Weekday, impl=db.Integer()))
    #  payroll_id = db.Column(db.ForeignKey('payroll.id'))


#  class BiWeeklyPayroll(Base):
    #  weekday = db.Column(ChoiceType(Weekday, impl=db.Integer()))


#  class SemiMonthlyPayroll(Base):
    #  day_of_month_1 = db.Column(db.Integer, nullable=False)
    #  day_of_month_2 = db.Column(db.Integer, nullable=False)


#  class MonthlyPayroll(Base):
    #  day_of_month = db.Column(db.Integer, nullable=False)


#  class CustomPayrollDate(Base):
    #  pay_day = db.Column(db.Date(), nullable=False)
    #  custom_payroll_id = db.Column(db.ForeignKey('custom_payroll.id'))


#  class CustomPayroll(Base):
    #  name = db.Column(db.Unicode(40), nullable=False)
    #  dates = db.relationship('CustomPayrollDate', uselist=True)


#  class Payroll(Base):
    #  cycle_type = db.Column(ChoiceType(PayrollCycleType, impl=db.Integer()))
    #  employee_class_id = db.Column(db.Integer,
    #  db.ForeignKey('employee_class.id'))
    #  employee_class = db.relationship('EmployeeClass',
    #  foreign_keys=employee_class_id)


class Enrollment(Base):
    """A collection of choices an employee makes during enrollment"""
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    life_event = db.Column(ChoiceType(LIFE_EVENT_TYPES))
    choices = db.relationship('EnrollmentChoice')


class EnrollmentChoice(Base):
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollment.id'))
    plan_tier_premium_id = db.Column(db.Integer,
                                     db.ForeignKey('plan_tier_premium.id'))
