# -*- coding: utf-8 -*-
from flask_user.forms import RegisterForm
from flask_wtf import Form
from wtforms import (
    BooleanField,
    DecimalField,
    HiddenField,
    IntegerField,
    RadioField,
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
    first_name = StringField('First name', validators=[validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[validators.DataRequired('Last name is required')])


class UserProfileForm(Form):
    first_name = StringField('First name', validators=[validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[validators.DataRequired('Last name is required')])
    submit = SubmitField('Save')


# Enrollment steps
class LifeEventsForm(ModelForm):
    class Meta:
        model = models.Enrollment
        include = ['id']
    id = HiddenField()
    employee_id = HiddenField()


class EmployeeInfoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'info'})
        super(EmployeeInfoForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Employee
        include = ['id']
        exclude = [
            'hire_date', 'effective_date', 'termination_date',
            'employee_number', 'group_id', 'sub_group_id',
            'sub_group_effective_date', 'salary', 'salary_mode',
            'salary_effective_date', ]
    id = HiddenField()


class ElectionForm(Form):
    id = HiddenField()
    employee_id = HiddenField()
    enrollment_id = HiddenField()
    selection = RadioField('Election')
    plan_tier_premium_id = HiddenField()
    plan_id = HiddenField()


# Admin
class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'user'})
        super(UserForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.User
        include = ['id']
    id = HiddenField()


class AddressForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'address'})
        super(AddressForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Address
        include = ['id']
    id = HiddenField()


class LocationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'location'})
        super(LocationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Location
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()


def locations():
    return models.Location.query.all()


class EmployeeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'employee'})
        super(EmployeeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Employee
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    user = ModelFormField(UserForm)
    address = ModelFormField(AddressForm)
    location = QuerySelectField('Location', query_factory=locations, get_label='code')
    salary = StringField()


class CarrierForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'carrier'})
        super(CarrierForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Carrier
        include = ['id']
    id = HiddenField()


class DependentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'dependent'})
        super(DependentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Dependent
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    employee_id = HiddenField()
    address = ModelFormField(AddressForm)


def carriers():
    return models.Carrier.query.all()


class MedicalPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'medical_plan'})
        super(MedicalPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.MedicalPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)
    carrier = QuerySelectField('Carrier', query_factory=carriers, get_label='name')


def bundle_plans():
    return models.Plan.query.all()


class DentalPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'dental_plan'})
        super(DentalPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.DentalPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)
    bundled_with_medical = BooleanField('Bundled With Medical?')
    bundled_with_vision = BooleanField('Bundled With Vision?')
    bundled_with_plan = QuerySelectField('Bundled With Plan', query_factory=bundle_plans, allow_blank=True,
                                         get_label='name')
    carrier = QuerySelectField('Carrier', query_factory=carriers, get_label='name')


class VisionPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'vision_plan'})
        super(VisionPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.VisionPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)
    bundled_with_medical = BooleanField('Bundled With Medical?')
    bundled_with_dental = BooleanField('Bundled Wth Dental?')
    bundled_with_plan = QuerySelectField('Bundled With Plan', query_factory=bundle_plans, allow_blank=True,
                                         get_label='name')
    carrier = QuerySelectField('Carrier', query_factory=carriers, get_label='name')


class EAPPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'eap_plan'})
        super(EAPPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.EAPPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)
    minimum_benefit = StringField()
    maximum_benefit = StringField()


class LTDPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'ltd_plan'})
        super(LTDPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.LTDPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)
    minimum_benefit = StringField()
    maximum_benefit = StringField()


class STDPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'std_plan'})
        super(STDPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.STDPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)
    payout_interval = IntegerField('Payout Interval')
    max_weekly_benefit = StringField('Maximum Weekly Benefit')
    max_monthly_benefit = StringField('Maximum Monthly Benefit')
    benefit_percentage = StringField('Benefit Percentage')
    mandatory_in_states = SelectMultipleField('Mandatory in States', choices=models.STATES)


class LifeADDPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'add_plan'})
        super(LifeADDPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.LifeADDPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)
    minimum_benefit = StringField()
    maximum_benefit = StringField()


class LifeADDDependentPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'addd_plan'})
        super(LifeADDDependentPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.LifeADDDependentPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)
    minimum_benefit = StringField()
    maximum_benefit = StringField()


class FSAPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'fsa_plan'})
        super(FSAPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.FSAPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)


# Supplemental
class ParkingTransitPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'parking_transit_plan'})
        super(ParkingTransitPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.ParkingTransitPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)


class HSAPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'hsa_plan'})
        super(HSAPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.HSAPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)


class Employee401KPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'e401k_plan'})
        super(Employee401KPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Employee401KPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)


class SupplementalInsurancePlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'supp_life_plan'})
        super(SupplementalInsurancePlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.SupplumentalInsurancePlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)


class LongTermCarePlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'ltc_plan'})
        super(LongTermCarePlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.LongTermCarePlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)


class OtherPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'other_plan'})
        super(OtherPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.OtherPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)


class CancerPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'cancer_plan'})
        super(CancerPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.CancerPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)


class CriticalIllnessPlanForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'critical_illness_plan'})
        super(CriticalIllnessPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.CriticalIllnessPlan
        date_format = '%m/%d/%Y'
        include = ['id']
    id = HiddenField()
    not_available_in = SelectMultipleField('Not available in', choices=models.STATES)


class AgeBandedPremiumForm(Form):
    id = HiddenField()
    low = IntegerField('Low')
    high = IntegerField('High')
    premium = DecimalField('Premium')
    plan_id = SelectField('Plan', [(p.id, p.name) for p in models.Plan.query.all()])


class PlanTierPremiumForm(Form):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'plan_tier_premium'})
        super(PlanTierPremiumForm, self).__init__(*args, **kwargs)
    id = HiddenField()
    plan_id = HiddenField()
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
