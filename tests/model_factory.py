# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Factory for unittest fixtures.
"""
from __future__ import unicode_literals

from datetime import timedelta
from faker import Faker
from faker.providers import BaseProvider
from random import choice
from sqlalchemy_utils.types.choice import Choice
import factory
import factory.fuzzy

from app import models


fake = Faker()


class PhoneProvider(BaseProvider):
    formats = ('###-###-####', )

    def phone(self):
        return self.numerify(self.random_element(self.formats))

fake.add_provider(PhoneProvider)


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    password = 'password'
    email = fake.email()
    is_admin = False


class AddressFactory(factory.Factory):
    class Meta:
        model = models.Address

    street_1 = fake.street_name()
    street_2 = ''
    city = fake.city()
    state = Choice(*choice(models.STATES))
    zip_code = fake.postalcode()


class PersonFactory(factory.Factory):
    first_name = fake.first_name()
    middle_name = fake.first_name()
    last_name = fake.last_name()
    ssn = fake.ssn()
    dob = fake.past_date()
    gender = Choice(*choice(models.GENDER_TYPES))
    marital_status = Choice(*choice(models.MARITAL_STATUS_TYPES))
    smoker_type = Choice(*choice(models.SMOKER_TYPES))
    address = factory.SubFactory(AddressFactory)


class LocationFactory(factory.Factory):
    class Meta:
        model = models.Location

    code = fake.pystr(max_chars=10)
    description = fake.text(max_nb_chars=60)
    effective_date = fake.past_date()


class EmployeeFactory(PersonFactory):
    class Meta:
        model = models.Employee

    user = factory.SubFactory(UserFactory)
    hire_date = fake.past_date()
    effective_date = factory.LazyAttribute(lambda o: o.hire_date)
    termination_date = None
    employee_number = fake.numerify('#####')
    group_id = factory.Sequence(lambda n: 'G%s' % n)
    sub_group_id = factory.Sequence(lambda n: 'SG%s' % n)
    sub_group_effective_date = fake.past_date()
    salary_mode = Choice(*choice(models.SALARY_MODE_TYPES))
    salary_effective_date = fake.past_date()
    salary = fake.pydecimal(left_digits=5, right_digits=2, positive=True)
    salary_mode = Choice(u'annually', 'Annually')
    phone = fake.phone()
    alternate_phone = fake.phone()
    emergency_contact_phone = fake.phone()
    emergency_contact_name = fake.name()
    emergency_contact_relationship = choice(['spouse', 'son', 'daughter'])
    spouse_dob = factory.LazyAttribute(lambda o: o.dob - timedelta(365 * 2))
    location = factory.SubFactory(LocationFactory)

    @factory.post_generation
    def dependents(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for dependent in extracted:
                self.dependents.append(dependent)


class BeneficiaryFactory(factory.Factory):
    class Meta:
        model = models.Beneficiary

    beneficiary_type = Choice(*choice(models.BENEFICIARY_TYPES))


class CarrierFactory(factory.Factory):
    class Meta:
        model = models.Carrier

    name = fake.company()
    phone = fake.phone()
    api_endpoint = factory.LazyAttribute(
        lambda o: 'http://api.%s.com' % o.name)


class DependentFactory(PersonFactory):
    class Meta:
        model = models.Dependent

    dependent_type = Choice(*choice(models.DEPENDENT_TYPES))
    full_time_student = factory.Iterator([True, False])
    disabled = False
    disability_date = None


class DependentBeneficiaryFactory(BeneficiaryFactory):
    class Meta:
        model = models.DependentBeneficiary

    dependent = factory.SubFactory(DependentFactory)


class EstateBeneficiaryFactory(BeneficiaryFactory):
    class Meta:
        model = models.EstateBeneficiary


class SuccessionOfHeirsBeneficiaryFactory(BeneficiaryFactory):
    class Meta:
        model = models.SuccessionOfHeirsBeneficiary


# Plans and Plan Mixins
class BooleanElectionMixinFactory(factory.Factory):
    class Meta:
        abstract = True


class TieredElectionMixinFactory(factory.Factory):
    class Meta:
        abstract = True


class AmountChosenElectionMixinFactory(factory.Factory):
    class Meta:
        abstract = True


class AmountSuppliedElectionMixinFactory(factory.Factory):
    class Meta:
        abstract = True


class PremiumFactory(factory.Factory):
    class Meta:
        model = models.Premium
    plan = None  # just pass it in
    amount = None
    rate = None
    gender = None
    smoker_status = None
    age = None
    age_band_low = None
    age_band_high = None
    family_tier = None
    payout_amount = None


class AgeBandedPremiumFactory:

    def __init__(self, plan, matrix):
        self.plan = plan
        self.matrix = matrix

    def get_premiums(self):
        premiums = []
        for lo, hi, rate in self.matrix:
            premiums.append(PremiumFactory(
                plan=self.plan,
                age_band_low=lo,
                age_band_high=hi,
                rate=rate,
            ))
        return premiums


class TieredPremiumFactory:

    def __init__(self, plan, matrix):
        self.plan = plan
        self.matrix = matrix

    def get_premiums(self):
        premiums = []
        for tier, amt in self.matrix:
            premiums.append(PremiumFactory(
                plan=self.plan,
                family_tier=unicode(tier),
                amount=amt,
            ))
        return premiums


class AgeBandedPremiumSmokingGenderFactory:

    def __init__(self, plan, matrix):
        self.plan = plan
        self.matrix = matrix

    def get_premiums(self):
        premiums = []
        for lo, hi, smoker_status, gender, rate in self.matrix:
            premiums.append(PremiumFactory(
                plan=self.plan,
                age_band_low=lo,
                age_band_high=hi,
                gender=unicode(gender),
                smoker_status=unicode(smoker_status),
                rate=rate,
            ))
        return premiums


class AgeBandedPremiumSmokingTieredFactory:

    def __init__(self, plan, matrix):
        self.plan = plan
        self.matrix = matrix

    def get_premiums(self):
        premiums = []
        for smoker_status, lo, hi, tier, amt in self.matrix:
            premiums.append(PremiumFactory(
                plan=self.plan,
                age_band_low=lo,
                age_band_high=hi,
                family_tier=unicode(tier),
                smoker_status=unicode(smoker_status),
                amount=amt,
            ))
        return premiums


class AgeBandedPremiumSmokingGenderTieredFactory:

    def __init__(self, plan, matrix):
        self.plan = plan
        self.matrix = matrix

    def get_premiums(self):
        premiums = []
        for gender, smoker_status, lo, hi, tier, amt in self.matrix:
            premiums.append(PremiumFactory(
                plan=self.plan,
                gender=unicode(gender),
                age_band_low=lo,
                age_band_high=hi,
                family_tier=unicode(tier),
                smoker_status=unicode(smoker_status),
                amount=amt,
            ))
        return premiums


class AgeBandedSmokingPayoutPremiumFactory:

    def __init__(self, plan, matrix):
        self.plan = plan
        self.matrix = matrix

    def get_premiums(self):
        premiums = []
        for lo, hi, smoker_status, payout, amt in self.matrix:
            premiums.append(PremiumFactory(
                plan=self.plan,
                age_band_low=lo,
                age_band_high=hi,
                smoker_status=unicode(smoker_status),
                payout_amount=payout,
                amount=amt,
            ))
        return premiums


class AgeSmokingPayoutPremiumFactory:

    def __init__(self, plan, matrix):
        self.plan = plan
        self.matrix = matrix

    def get_premiums(self):
        premiums = []
        for age, smoker_status, payout, amt in self.matrix:
            premiums.append(PremiumFactory(
                plan=self.plan,
                age=age,
                smoker_status=unicode(smoker_status),
                payout_amount=payout,
                amount=amt,
            ))
        return premiums


class EmployerContributionMixinFactory(factory.Factory):
    class Meta:
        abstract = True
    er_flat_amount_contributed = 0
    er_percentage_contributed = 0
    er_max_contribution = 5000


class PlanPremiumMetaValuesMixinFactory(factory.Factory):
    class Meta:
        abstract = True
    salary_chunk_size = 10000
    coverage_chunk_size = 10000


class CoreMixinFactory(factory.Factory):
    class Meta:
        abstract = True
    group_number = fake.numerify('#######')
    original_effective_date = fake.past_date()
    renewal_date = fake.past_date()
    list_billed = True
    doctor_selection_required = True
    cobra_eligible = True


class PreOrPostTaxMixinFactory(factory.Factory):
    class Meta:
        abstract = True
    pre_tax = True


class PlanFactory(EmployerContributionMixinFactory, PlanPremiumMetaValuesMixinFactory):
    class Meta:
        abstract = True
    #  code = fake.pystr(max_chars=10)
    code = factory.Faker('pystr', max_chars=10)
    name = factory.Sequence(lambda n: u'plan%s' % n)
    description = fake.words(8)
    special_instructions = fake.words(8)
    active = True
    carrier = factory.SubFactory(CarrierFactory)
    website = factory.Faker('url')
    cust_service_phone = fake.phone()
    required_plan = None


class MedicalPlanFactory(PlanFactory, CoreMixinFactory, PreOrPostTaxMixinFactory, TieredElectionMixinFactory):
    class Meta:
        model = models.MedicalPlan
    name = factory.sequence(lambda n: u'Medical Plan%s' % n)


class DentalPlanFactory(PlanFactory, CoreMixinFactory, PreOrPostTaxMixinFactory, TieredElectionMixinFactory):
    class Meta:
        model = models.DentalPlan
    name = factory.sequence(lambda n: u'Dental Plan%s' % n)


class VisionPlanFactory(PlanFactory, CoreMixinFactory, PreOrPostTaxMixinFactory, TieredElectionMixinFactory):
    class Meta:
        model = models.VisionPlan

    name = factory.sequence(lambda n: u'Vision Plan%s' % n)


class MedicalDentalBundlePlanFactory(PlanFactory, CoreMixinFactory, PreOrPostTaxMixinFactory,
                                     TieredElectionMixinFactory):
    class Meta:
        model = models.MedicalDentalBundlePlan

    name = factory.sequence(lambda n: u'Medical Dental Bundle Plan%s' % n)


class MedicalVisionBundlePlanFactory(PlanFactory, CoreMixinFactory, PreOrPostTaxMixinFactory,
                                     TieredElectionMixinFactory):
    class Meta:
        model = models.MedicalVisionBundlePlan

    name = factory.sequence(lambda n: u'Medical Vision Bundle Plan%s' % n)


class MedicalDentalVisionBundlePlanFactory(PlanFactory, CoreMixinFactory, PreOrPostTaxMixinFactory,
                                           TieredElectionMixinFactory):
    class Meta:
        model = models.MedicalDentalVisionBundlePlan

    name = factory.sequence(lambda n: u'Medical Dental Vision Bundle Plan%s' % n)


class DentalVisionBundlePlanFactory(PlanFactory, CoreMixinFactory, PreOrPostTaxMixinFactory,
                                    TieredElectionMixinFactory):
    class Meta:
        model = models.DentalVisionBundlePlan

    name = factory.sequence(lambda n: u'Dental Vision Bundle Plan%s' % n)


class AgeBasedMixinFactory(factory.Factory):
    class Meta:
        abstract = True


class AgeBasedReductionFactory(factory.Factory):
    class Meta:
        model = models.AgeBasedReduction

    age = factory.fuzzy.FuzzyInteger(50, 70)
    percentage = factory.fuzzy.FuzzyInteger(70)


class LifeMixinFactory(factory.Factory):
    class Meta:
        abstract = True

    @factory.post_generation
    def beneficiaries(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for beneficiary in extracted:
                self.beneficiaries.append(beneficiary)


class BasicLifePlanFactory(PlanFactory, AgeBasedMixinFactory, LifeMixinFactory, BooleanElectionMixinFactory):
    class Meta:
        model = models.BasicLifePlan

    multiple_of_salary_paid = factory.fuzzy.FuzzyInteger(1, 3)
    min_benefit = factory.fuzzy.FuzzyInteger(5000, 50000, step=5000)
    max_benefit = factory.fuzzy.FuzzyInteger(50000, 250000, step=10000)
    spouse_benefit = factory.fuzzy.FuzzyInteger(25000, 50000, step=5000)
    child_benefit = factory.fuzzy.FuzzyInteger(12500, 25000, step=500)
    guarantee_issue = factory.fuzzy.FuzzyInteger(10000, 50000, step=10000)
    addl_salary_multiple_accidental_death = factory.fuzzy.FuzzyChoice([0, 1])
    addl_salary_multiple_accidental_dismemberment = factory.fuzzy.FuzzyChoice([0, 1])

    @factory.post_generation
    def age_based_reductions(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for abr in extracted:
                self.age_based_reductions.append(abr)


class VoluntaryLifePlanFactory(PlanFactory, AmountChosenElectionMixinFactory, LifeMixinFactory):
    class Meta:
        model = models.VoluntaryLifePlan

    increments = factory.fuzzy.FuzzyChoice([5000, 10000])
    min_election = 5000
    max_election = 50000
    guarantee_issue = 25000
    addl_salary_multiple_accidental_death = 1
    addl_salary_multiple_accidental_dismemberment = 1

    @factory.post_generation
    def age_based_reductions(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for abr in extracted:
                self.age_based_reductions.append(abr)


class SpouseVoluntaryLifePlanFactory(VoluntaryLifePlanFactory):
    class Meta:
        model = models.SpouseVoluntaryLifePlan

    use_employee_age_for_spouse = True


class ChildVoluntaryLifePlanFactory(VoluntaryLifePlanFactory):
    class Meta:
        model = models.ChildVoluntaryLifePlan


class StandaloneADDPlanFactory(PlanFactory, AmountChosenElectionMixinFactory, LifeMixinFactory):
    class Meta:
        model = models.StandaloneADDPlan

    increments = factory.fuzzy.FuzzyChoice([5000, 10000])
    min_election = factory.fuzzy.FuzzyChoice([10000, 20000, 30000])
    max_election = factory.LazyAttribute(lambda o: o.min_election * 10)


class SpouseStandaloneADDPlanFactory(StandaloneADDPlanFactory):
    class Meta:
        model = models.SpouseStandaloneADDPlan


class ChildStandaloneADDPlanFactory(StandaloneADDPlanFactory):
    class Meta:
        model = models.ChildStandaloneADDPlan


class WholeLifePlanFactory(PlanFactory, AmountChosenElectionMixinFactory, LifeMixinFactory, AgeBasedMixinFactory):
    class Meta:
        model = models.WholeLifePlan

    spouse_benefit = factory.fuzzy.FuzzyChoice(range(5000, 55000, 5000))
    child_benefit = factory.LazyAttribute(lambda o: o.spouse_benefit / 2)


class SpouseWholeLife(WholeLifePlanFactory):
    class Meta:
        model = models.SpouseWholeLifePlan


class ChildWholeLife(WholeLifePlanFactory):
    class Meta:
        model = models.ChildWholeLifePlan


class UniversalLifePlanFactory(PlanFactory, AmountChosenElectionMixinFactory, LifeMixinFactory, AgeBasedMixinFactory):
    class Meta:
        model = models.UniversalLifePlan
    spouse_benefit = factory.fuzzy.FuzzyChoice(range(5000, 55000, 5000))
    child_benefit = factory.LazyAttribute(lambda o: o.spouse_benefit / 2)


class LTDPlanFactory(PlanFactory, PreOrPostTaxMixinFactory, BooleanElectionMixinFactory):
    class Meta:
        model = models.LTDPlan

    max_monthly_benefit = factory.fuzzy.FuzzyChoice(range(1000, 11000, 1000))
    percentage_of_salary_paid = factory.fuzzy.FuzzyChoice([.5, .6, .7, .8])


class STDPlanFactory(PlanFactory, BooleanElectionMixinFactory):
    class Meta:
        model = models.STDPlan

    max_weekly_benefit = factory.fuzzy.FuzzyChoice(range(250, 2000, 250))
    percentage_of_salary_paid = factory.fuzzy.FuzzyChoice([.5, .6, .7, .8])
    premium_based_on_benefit = False


class FSAMedicalPlanFactory(PlanFactory, AmountSuppliedElectionMixinFactory):
    class Meta:
        model = models.FSAMedicalPlan

    min_contribution = factory.fuzzy.FuzzyChoice(range(250, 2000, 250))


class FSADependentCarePlanFactory(FSAMedicalPlanFactory):
    class Meta:
        model = models.FSAMedicalPlan


class HSAPlanFactory(PlanFactory, AmountSuppliedElectionMixinFactory):
    class Meta:
        model = models.HSAPlan

    min_contribution = factory.fuzzy.FuzzyChoice(range(250, 2000, 250))


class HRAPlanFactory(PlanFactory, BooleanElectionMixinFactory):
    class Meta:
        model = models.HRAPlan


class Employee401KPlanFactory(PlanFactory, AmountSuppliedElectionMixinFactory):
    class Meta:
        model = models.Employee401KPlan

    employer_percent_matched = factory.fuzzy.FuzzyChoice([.5, .6, .7, .8])
    employer_max_contribution = factory.fuzzy.FuzzyInteger(2000, 10000)
    min_contribution = factory.fuzzy.FuzzyChoice(range(250, 2000, 250))


class EAPPlanFactory(PlanFactory, BooleanElectionMixinFactory):
    class Meta:
        model = models.EAPPlan


class LongTermCarePlanFactory(PlanFactory, PreOrPostTaxMixinFactory, TieredElectionMixinFactory):
    class Meta:
        model = models.LongTermCarePlan


class CriticalIllnessPlanFactory(PlanFactory, TieredElectionMixinFactory):
    class Meta:
        model = models.CriticalIllnessPlan


class CancerPlanFactory(PlanFactory, TieredElectionMixinFactory):
    class Meta:
        model = models.CancerPlan


class AccidentPlanFactory(PlanFactory, TieredElectionMixinFactory):
    class Meta:
        model = models.AccidentPlan


class HospitalConfinementPlanFactory(PlanFactory, TieredElectionMixinFactory):
    class Meta:
        model = models.HospitalConfinementPlan


class ParkingTransitPlanFactory(PlanFactory, TieredElectionMixinFactory):
    class Meta:
        model = models.ParkingTransitPlan


class IdentityTheftPlanFactory(PlanFactory, TieredElectionMixinFactory):
    class Meta:
        model = models.IdentityTheftPlan


class OtherPlanFactory(PlanFactory, TieredElectionMixinFactory):
    class Meta:
        model = models.OtherPlan


class IRSLimitsFactory(factory.Factory):
    class Meta:
        model = models.IRSLimits
    max_fsa_medical_contribution = 1200
    max_fsa_dependent_care_contribution = 1000
    max_hsa_individual_contribution = 800
    max_hsa_family_contribution = 1200
    max_hsa_family_over_55_contribution = 1500
    max_401k_salary_deferal = 5000
    max_401k_salary_deferal_over_50 = 8000


class ElectionFactory(factory.Factory):
    class Meta:
        model = models.Election
    plan = None
    premium = None
    amount = None
    elected = None
    total_cost = None
    employer_cost = None
    employee_cost = None


class EnrollmentPeriodFactory(factory.Factory):
    class Meta:
        model = models.EnrollmentPeriod

    year = 2017


class EnrollmentFactory(factory.Factory):
    class Meta:
        model = models.Enrollment

    employee = factory.SubFactory(EmployeeFactory)
    life_event = Choice(*choice(models.LIFE_EVENT_TYPES))
    enrollment_period = factory.SubFactory(EnrollmentPeriodFactory)

    @factory.post_generation
    def elections(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for election in extracted:
                self.elections.append(election)
