# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from flask_user.forms import RegisterForm
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    FileField,
    IntegerField,
    RadioField,
    SelectField,
    StringField,
    TextAreaField,
    SubmitField,
    validators,
)
from wtforms.fields import FieldList
from wtforms.widgets import HiddenInput
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms_alchemy import ModelForm, ModelFormField

from perks import models


# Adds first and last name to RegisterForm's required fields.
class RegistrationForm(RegisterForm):
    first_name = StringField('First name', validators=[validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[validators.DataRequired('Last name is required')])


class UserProfileForm(FlaskForm):
    first_name = StringField('First name', validators=[validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[validators.DataRequired('Last name is required')])
    submit = SubmitField('Save')


# Enrollment steps
class LifeEventsForm(ModelForm):
    class Meta:
        model = models.Enrollment
        include = ['id']
    id = IntegerField(widget=HiddenInput())
    employee_id = IntegerField(widget=HiddenInput())


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
    id = IntegerField(widget=HiddenInput())


class BooleanElectionForm(FlaskForm):
    id = IntegerField(widget=HiddenInput())
    plan_id = IntegerField(widget=HiddenInput())
    employee_id = IntegerField(widget=HiddenInput())
    enrollment_id = IntegerField(widget=HiddenInput())
    selection = RadioField('Election')

    def populate_election(self, election):
        election.elected = self.selection.data == 'Enroll'


class AmountChosenElectionForm(FlaskForm):
    id = IntegerField(widget=HiddenInput())
    plan_id = IntegerField(widget=HiddenInput())
    employee_id = IntegerField(widget=HiddenInput())
    enrollment_id = IntegerField(widget=HiddenInput())
    selection = RadioField('Election')
    amount = IntegerField(widget=HiddenInput())

    def populate_election(self, election):
        election.amount = int(self.selection.data)
        election.premium_id = None   # not sure if this is needed


class AmountInputElectionForm(FlaskForm):
    id = IntegerField(widget=HiddenInput())
    plan_id = IntegerField(widget=HiddenInput())
    employee_id = IntegerField(widget=HiddenInput())
    enrollment_id = IntegerField(widget=HiddenInput())
    selection = IntegerField(widget=HiddenInput())
    elected_amount = IntegerField(widget=HiddenInput())

    def populate_election(self, election):
        election.amount = int(self.selection.data)
        election.premium_id = None   # not sure if this is needed


class TieredElectionForm(FlaskForm):
    id = IntegerField(widget=HiddenInput())
    plan_id = IntegerField(widget=HiddenInput())
    employee_id = IntegerField(widget=HiddenInput())
    enrollment_id = IntegerField(widget=HiddenInput())
    selection = RadioField('Election')
    premium_id = IntegerField(widget=HiddenInput())  # used if a tier is selected

    def populate_election(self, election):
        premium = models.Premium.query.filter(
            models.Premium.family_tier == self.selection.data,
            models.Premium.plan_id == self.plan_id.data).first()
        election.premium = premium


# Admin
class UserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'user'})
        super(UserForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.User
        include = ['id']
    id = IntegerField(widget=HiddenInput())


class AddressForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'address'})
        super(AddressForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Address
        include = ['id']
    id = IntegerField(widget=HiddenInput())


class LocationForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'location'})
        super(LocationForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Location
        date_format = '%Y-%m-%d'
        include = ['id']
    id = IntegerField([validators.optional()], widget=HiddenInput())


def locations():
    return models.Location.query.all()


class EmployeeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'employee'})
        super(EmployeeForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Employee
        date_format = '%Y-%m-%d'
        include = ['id']
    id = IntegerField(widget=HiddenInput())
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
    id = IntegerField(widget=HiddenInput())


class DependentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'dependent'})
        super(DependentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Dependent
        date_format = '%Y-%m-%d'
        include = ['id']
    id = IntegerField(widget=HiddenInput())
    employee_id = IntegerField(widget=HiddenInput())
    address = ModelFormField(AddressForm)


class MiniDependentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'dependent'})
        super(MiniDependentForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Dependent
        only = ['id', 'first_name', 'last_name', 'dependent_type']


class DependentBeneficiaryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(DependentBeneficiaryForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.DependentBeneficiary
        include = ['id']
    id = IntegerField(widget=HiddenInput())
    dependent = ModelFormField(MiniDependentForm)
    dependent_id = IntegerField(widget=HiddenInput())


class EstateBeneficiaryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'estate_beneficiary'})
        super(EstateBeneficiaryForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.EstateBeneficiary
        include = ['id']
    id = IntegerField(widget=HiddenInput())
    employee_id = IntegerField(widget=HiddenInput())


class SuccessionOfHeirsBeneficiaryForm(ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'heirs_beneficiary'})
        super(SuccessionOfHeirsBeneficiaryForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.SuccessionOfHeirsBeneficiary
        include = ['id']
    id = IntegerField(widget=HiddenInput())
    employee_id = IntegerField(widget=HiddenInput())


class BeneficiariesForm(FlaskForm):
    dependent_beneficiaries = FieldList(ModelFormField(DependentBeneficiaryForm))
    estate_beneficiary = ModelFormField(EstateBeneficiaryForm)
    succession_of_heirs_beneficiary = ModelFormField(SuccessionOfHeirsBeneficiaryForm)


def carriers():
    return models.Carrier.query.all()


def plans():
    return models.Plan.query.filter_by(active=True)


class AdminPlanForm(ModelForm):
    active = BooleanField('Active?')
    id = IntegerField(widget=HiddenInput())
    premium_matrix = TextAreaField()
    description = TextAreaField()
    carrier = QuerySelectField('Carrier', query_factory=carriers, get_label='name')
    required_plan = QuerySelectField('Must First Be Enrolled In', query_factory=plans, get_label='name', allow_blank=True)


class MedicalPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'medical_plan'})
        super(MedicalPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.MedicalPlan
        date_format = '%Y-%m-%d'
        include = ['id']


def bundle_plans():
    return models.Plan.query.all()


class DentalPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'dental_plan'})
        super(DentalPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.DentalPlan
        date_format = '%Y-%m-%d'
        include = ['id']
    carrier = QuerySelectField('Carrier', query_factory=carriers, get_label='name')


class VisionPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'vision_plan'})
        super(VisionPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.VisionPlan
        date_format = '%Y-%m-%d'
        include = ['id']
    carrier = QuerySelectField('Carrier', query_factory=carriers, get_label='name')


class MedicalDentalVisionPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'medical_dental_vision_plan'})
        super(MedicalDentalVisionPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.MedicalDentalVisionBundlePlan
        date_format = '%Y-%m-%d'
        include = ['id']


class MedicalDentalPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'medical_dental_plan'})
        super(MedicalDentalPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.MedicalDentalBundlePlan
        date_format = '%Y-%m-%d'
        include = ['id']


class MedicalVisionPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'medical_vision_plan'})
        super(MedicalVisionPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.MedicalVisionBundlePlan
        date_format = '%Y-%m-%d'
        include = ['id']


class DentalVisionPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'dental_vision_plan'})
        super(DentalVisionPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.DentalVisionBundlePlan
        date_format = '%Y-%m-%d'
        include = ['id']


class EAPPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'eap_plan'})
        super(EAPPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.EAPPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class LTDPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'ltd_plan'})
        super(LTDPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.LTDPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class LTDVoluntaryPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'ltd_voluntary_plan'})
        super(LTDVoluntaryPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.LTDVoluntaryPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class STDPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'std_plan'})
        super(STDPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.STDPlan
        date_format = '%Y-%m-%d'
        include = ['id']
    payout_interval = IntegerField('Payout Interval')
    max_weekly_benefit = StringField('Maximum Weekly Benefit')
    max_monthly_benefit = StringField('Maximum Monthly Benefit')
    benefit_percentage = StringField('Benefit Percentage')


class BasicLifePlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'basic_life_plan'})
        super(BasicLifePlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.BasicLifePlan
        date_format = '%Y-%m-%d'
        include = ['id']
    age_based_reduction_matrix = TextAreaField()


class VoluntaryLifePlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'voluntary_life_plan'})
        super(VoluntaryLifePlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.VoluntaryLifePlan
        date_format = '%Y-%m-%d'
        include = ['id']
    age_based_reduction_matrix = TextAreaField()


class SpouseVoluntaryLifePlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'spouse_voluntary_life_plan'})
        super(SpouseVoluntaryLifePlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.SpouseVoluntaryLifePlan
        date_format = '%Y-%m-%d'
        include = ['id']
    age_based_reduction_matrix = TextAreaField()


class ChildVoluntaryLifePlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'child_voluntary_life_plan'})
        super(ChildVoluntaryLifePlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.ChildVoluntaryLifePlan
        date_format = '%Y-%m-%d'
        include = ['id']
    age_based_reduction_matrix = TextAreaField()


class StandaloneADDPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'standalone_add_plan'})
        super(StandaloneADDPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.StandaloneADDPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class SpouseStandaloneADDPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'spouse_standalone_add_plan'})
        super(SpouseStandaloneADDPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.SpouseStandaloneADDPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class ChildStandaloneADDPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'child_standalone_add_plan'})
        super(ChildStandaloneADDPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.ChildStandaloneADDPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class FSAMedicalPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'fsa_plan'})
        super(FSAMedicalPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.FSAMedicalPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class FSADependentCarePlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'fsa_dependent_care_plan'})
        super(FSADependentCarePlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.FSADependentCarePlan
        date_format = '%Y-%m-%d'
        include = ['id']


# Supplemental
class ParkingTransitPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'parking_transit_plan'})
        super(ParkingTransitPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.ParkingTransitPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class HRAPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'hra_plan'})
        super(HRAPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.HRAPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class HSAPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'hsa_plan'})
        super(HSAPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.HSAPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class Employee401KPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'e401k_plan'})
        super(Employee401KPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.Employee401KPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class LongTermCarePlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'ltc_plan'})
        super(LongTermCarePlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.LongTermCarePlan
        date_format = '%Y-%m-%d'
        include = ['id']


class CancerPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'cancer_plan'})
        super(CancerPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.CancerPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class CriticalIllnessPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'critical_illness_plan'})
        super(CriticalIllnessPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.CriticalIllnessPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class AccidentPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'accident_plan'})
        super(AccidentPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.AccidentPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class HospitalConfinementPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'hospital_plan'})
        super(HospitalConfinementPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.HospitalConfinementPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class IdentityTheftPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'identity_theft_plan'})
        super(IdentityTheftPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.IdentityTheftPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class OtherPlanForm(AdminPlanForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'other_plan'})
        super(OtherPlanForm, self).__init__(*args, **kwargs)

    class Meta:
        model = models.OtherPlan
        date_format = '%Y-%m-%d'
        include = ['id']


class PremiumForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        kwargs.update({'prefix': 'premium'})
        super(PremiumForm, self).__init__(*args, **kwargs)
    id = IntegerField(widget=HiddenInput())
    plan_id = IntegerField(widget=HiddenInput())
    tier_type = SelectField('Tier', choices=models.FAMILY_TIER_TYPES)
    premium = DecimalField('Premium')
    employer_portion = DecimalField('Employer Portion')
    employee_portion = DecimalField('Employee Portion')
    flat_amount = DecimalField('Flat Amount')
    percentage = DecimalField('Percentage')


# Eligibility
class EmployeeEligibility(FlaskForm):
    id = IntegerField(widget=HiddenInput())
    full_time_only = BooleanField('Full Time Only?')
    minimum_days_employed = IntegerField('Minimum Days Employed')


class DependentEligibility(FlaskForm):
    id = IntegerField(widget=HiddenInput())
    eligible = BooleanField('Eligible?')


class DomesticPartnerEligibility(FlaskForm):
    id = IntegerField(widget=HiddenInput())
    eligible = BooleanField('Eligible?')


# File import
class UploadForm(FlaskForm):
    xl = FileField(u'Excel File', [validators.regexp(u'^[^/\\]\.xls[x]?$')])
