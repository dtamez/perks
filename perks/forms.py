# -*- coding: utf-8 -*-
from flask_user.forms import RegisterForm
from flask_wtf import Form
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    HiddenField,
    IntegerField,
    SelectField,
    SelectMultipleField,
    StringField,
    SubmitField,
    validators,
)
from perks import models
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms_alchemy import ModelForm, ModelFormField


# Adds first and last name to RegisterForm's required fields.
class RegistrationForm(RegisterForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])


class UserProfileForm(Form):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])
    submit = SubmitField('Save')


# Enrollment steps
class LifeEventsForm(Form):
    id = HiddenField()
    life_event = StringField(
        'Choose a qualifying life event.',
        validators=[validators.Required('Life event is required')])


class UserForm(ModelForm):
    class Meta:
        model = models.User
        include = ['id']
    id = HiddenField()


class AddressForm(ModelForm):
    class Meta:
        model = models.Address
    id = HiddenField()


class LocationForm(ModelForm):
    class Meta:
        model = models.Location
        date_format = '%m/%d/%Y'
    id = HiddenField()


def locations():
    return models.Location.query.all()


class EmployeeForm(ModelForm):
    class Meta:
        model = models.Employee
        date_format = '%m/%d/%Y'
    id = HiddenField()
    user = ModelFormField(UserForm)
    address = ModelFormField(AddressForm)
    location = QuerySelectField('Location', query_factory=locations,
                                get_label='code')


class CarrierForm(ModelForm):
    class Meta:
        model = models.Carrier
        include = ['id']
    id = HiddenField()


class DependentForm(ModelForm):
    class Meta:
        model = models.Dependent
        date_format = '%m/%d/%Y'
    id = HiddenField()
    employee_id = HiddenField()
    address = ModelFormField(AddressForm)


class CoreForm(Form):
    life_event = SelectField('Life Event', choices=models.LIFE_EVENT_TYPES)
    group_number = StringField('Group Number')
    original_effective_date = DateField('Original Effective Date')
    renewal_date = DateField('Renewal Date')
    existing = BooleanField('Existing?')
    list_billed = BooleanField('List Billed?')
    doctor_selection_required = BooleanField('Doctor Selection Required?')
    account_rep_name = StringField('Account Rep Name')
    cobra_eligible = BooleanField('Cobra Eligible?')
    pre_tax = BooleanField('Pre-tax?')
    pricing_type_id = SelectField('Pricing Type', choices=models.PRICING_TYPES)


class GroupForm(object):
    minimum_benefit = DecimalField('Minimum Benefit')
    maximum_benefit = DecimalField('Maximum Benefit')


class SupplementalForm(object):
    pass


def carriers():
    return models.Carrier.query.all()


class PlanForm(Form):
    code = StringField('Code')
    name = StringField('Name')
    public_name = StringField('Public Name')
    cust_service_phone = StringField('Customer Service Phone')
    website = StringField('Website')
    not_available_in = SelectMultipleField('Not available in',
                                           choices=models.STATES)
    carrier = QuerySelectField('Carrier', query_factory=carriers,
                               get_label='name')


class MedicalPlanForm(PlanForm, CoreForm):
    class Meta:
        model = models.MedicalPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()
    self_funded = BooleanField('Self Funded?')


def bundle_plans():
    return models.Plan.query.all()


class DentalPlanForm(PlanForm, CoreForm):
    class Meta:
        model = models.DentalPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()
    bundled_with_medical = BooleanField('Bundled With Medical?')
    bundled_with_vision = BooleanField('Bundled With Vision?')
    bundled_with = QuerySelectField('Bundled With Plan',
                                    query_factory=bundle_plans,
                                    get_label='name')


class VisionPlanForm(PlanForm, CoreForm):
    class Meta:
        model = models.VisionPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()
    bundled_with_medical = BooleanField('Bundled With Medical?')
    bundled_with_dental = BooleanField('Bundled Wth Dental?')
    bundled_with = QuerySelectField('Bundled With Plan',
                                    query_factory=bundle_plans,
                                    get_label='name')


class EAPPlanForm(PlanForm, GroupForm):
    class Meta:
        model = models.EAPPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class LTDPlanForm(PlanForm, GroupForm):
    class Meta:
        model = models.LTDPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class STDPlanForm(PlanForm, GroupForm):
    class Meta:
        model = models.STDPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()
    payout_interval = IntegerField('Payout Interval')
    max_weekly_benefit = DecimalField('Maximum Weekly Benefit')
    max_monthly_benefit = DecimalField('Maximum Monthly Benefit')
    benefit_percentage = DecimalField('Benefit Percentage')
    mandatory_in_states = SelectMultipleField('Mandatory in States',
                                              choices=models.STATES)


class LifeADDPlanForm(PlanForm, GroupForm):
    class Meta:
        model = models.LifeADDPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class LifeADDDependentPlanForm(PlanForm, GroupForm):
    class Meta:
        model = models.LifeADDDependentPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class FSAPlanForm(PlanForm, SupplementalForm):
    class Meta:
        model = models.FSAPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class ParkingTransitPlanForm(PlanForm, SupplementalForm):
    class Meta:
        model = models.ParkingTransitPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class HSAPlanForm(PlanForm, SupplementalForm):
    class Meta:
        model = models.HSAPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class Employee401KPlanForm(PlanForm, SupplementalForm):
    class Meta:
        model = models.Employee401KPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class SupplementalInsurancePlanForm(PlanForm, SupplementalForm):
    class Meta:
        model = models.SupplumentalInsurancePlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class LongTermCarePlanForm(PlanForm, SupplementalForm):
    class Meta:
        model = models.LongTermCarePlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class OtherPlanForm(PlanForm, SupplementalForm):
    class Meta:
        model = models.OtherPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class CancerPlanForm(PlanForm, SupplementalForm):
    class Meta:
        model = models.CancerPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class CriticalIllnessPlanForm(PlanForm, SupplementalForm):
    class Meta:
        model = models.CriticalIllnessPlan
        date_format = '%m/%d/%Y'
    id = HiddenField()


class AgeBandedPremiumForm(Form):
    id = HiddenField()
    low = IntegerField('Low')
    high = IntegerField('High')
    premium = DecimalField('Premium')
    plan_id = SelectField('Plan', [(p.id, p.public_name)
                                   for p in models.Plan.query.all()])


class PlanTierPremiumForm(Form):
    id = HiddenField()
    plan_id = SelectField('Plan', [(p.id, p.public_name)
                                   for p in models.Plan.query.all()])
    tier_type = SelectField('Tier', choices=models.TIER_TYPES)
    premium = DecimalField('Premium')
    employer_portion = DecimalField('Employer Portion')
    employee_portion = DecimalField('Employee Portion')
    flat_amount = DecimalField('Flat Amount')
    multiplier = DecimalField('Multiplier')


# Eligibility
class EmployeeEligibility(Form):
    id = HiddenField()
    full_time_only = BooleanField('Full Time Only?')
    minimum_days_employed = IntegerField('Minimum Days Employed')


class DependentEligibility(Form):
    id = HiddenField()
    eligible = BooleanField('Eligible?')


class DomesticPartnerEligibility(Form):
    id = HiddenField()
    eligible = BooleanField('Eligible?')
