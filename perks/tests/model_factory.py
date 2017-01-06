# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Factory for unittest fixtures.
"""
import datetime
import factory
from faker import Faker
from faker.providers import BaseProvider

from perks import models


fake = Faker()


class PhoneProvider(BaseProvider):
    formats = ('###-###-####', )

    def phone(self):
        return self.numerify(self.random_element(self.formats))

fake.add_provider(PhoneProvider)


class RoleFactory(factory.Factory):
    class Meta:
        model = models.Role

    name = factory.Sequence(lambda n: 'role_name%s' % n)
    label = factory.Sequence(lambda n: 'role_label%s' % n)


class UserFactory(factory.Factory):
    class Meta:
        model = models.User

    username = factory.Faker('user_name')
    password = 'password'
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)
    confirmed_at = factory.LazyFunction(datetime.datetime.now)
    active = True
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')


class UserRoleFactory(factory.Factory):
    class Meta:
        model = models.UserRoles

    user_id = factory.SubFactory(UserFactory)
    role_id = factory.SubFactory(RoleFactory)


class PersonFactory(factory.Factory):
    first_name = factory.Faker('first_name')
    middle_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    ssn = factory.Faker('ssn')
    dob = factory.Faker('date')
    gender = factory.Iterator(models.GENDER_TYPES)
    marital_status = factory.Iterator(models.MARITAL_STATUSES)
    smoker_type = factory.Iterator(models.SMOKER_TYPES)


class DependentFactory(PersonFactory):
    class Meta:
        model = models.Dependent

    dependent_type = factory.Iterator(models.DEPENDENT_TYPES)
    full_time_student = factory.Iterator([True, False])
    disabled = False
    disability_date = None


class BeneficiaryFactory(PersonFactory):
    class Meta:
        model = models.Beneficiary

    beneficiary_type = factory.Iterator(models.BENEFICIARY_TYPES)


class EmployeeFactory(PersonFactory):
    class Meta:
        model = models.Employee

    user = factory.SubFactory(UserFactory)
    hire_date = factory.Faker('date')
    effective_date = factory.LazyAttribute(lambda o: o.hire_date)
    termination_date = None
    employee_number = factory.Faker('ean13')
    group_id = 'e'
    sub_group_id = 'se'
    sub_group_effective_date = factory.Faker('date')
    #  location_id = factory.Sequence(lambda n: 'location%s' % n)
    #  location_description = factory.Sequence(
        #  lambda n: 'location description%s' % n)
    #  location_effective_date = factory.Faker('date')
    salary_mode = factory.Iterator(models.SALARY_MODE_TYPES)
    salary_effective_date = factory.Faker('date')
    salary = 50000
    phone = fake.phone()
    alternate_phone = fake.phone()
    emergency_contact_phone = fake.phone()
    emergency_contact_name = factory.Faker('name')
    emergency_contact_relationship = factory.Iterator(
        ['spouse', 'son', 'daughter'])

    @factory.post_generation
    def dependents(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for dependent in extracted:
                self.dependents.append(dependent)

    @factory.post_generation
    def beneficiaries(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for beneficiary in extracted:
                self.beneficiaries.append(beneficiary)


class CarrierFactory(factory.Factory):
    class Meta:
        model = models.Carrier

    name = factory.Faker('company')
    api_endpoint = factory.LazyAttribute(
        lambda o: 'http://api.%s.com' % o.name)


class Plan(factory.Factory):
    code = factory.Faker('word')
    name = factory.Sequence(lambda n: 'plan%s' % n)
    cust_service_phone = fake.phone()
    website = factory.Faker('url')
    not_available_in = []
    pricing_type_id = factory.Iterator(models.PRICING_TYPES)


class Core(factory.Factory):
    group_number = '33387-01'
    original_effective_date = factory.Faker('date')
    renewal_date = factory.Faker('date')
    existing = True
    list_billed = True
    doctor_selection_required = False
    account_rep_name = factory.Faker('name')
    cobra_eligible = True
    pre_tax = True


class Group(factory.Factory):
    minimum_benefit = 50000
    maximum_benefit = 100000


class Supplemental(factory.Factory):
    pass


class MedicalPlanFactory(Plan, Core):
    class Meta:
        model = models.MedicalPlan

    self_funded = False


class DentalPlanFactory(Plan, Core):
    class Meta:
        model = models.DentalPlan

    bundled_with_medical = False
    bundled_with_vision = False
    bundled_with_plan = None


class VisionPlanFactory(Plan, Core):
    class Meta:
        model = models.VisionPlan

    bundled_with_medical = False
    bundled_with_dental = False
    bundled_with_plan = None


class EAPPlanFactory(Plan, Group):
    class Meta:
        model = models.EAPPlan


class LTDPlanFactory(Plan, Group):
    class Meta:
        model = models.LTDPlan


class LifeADDPlanFactory(Plan, Group):
    class Meta:
        model = models.LTDPlan


class LifeADDDependentPlanFactory(Plan, Group):
    class Meta:
        model = models.LifeADDDependentPlan


class STDPlanFactory(Plan, Group):
    class Meta:
        model = models.STDPlan

    payout_interval = factory.Iterator(models.PAYOUT_INTERVAL_TYPES)
    max_weekly_benefit = 10000
    max_monthly_benefit = 4000
    benefit_percentage = 10
    mandatory_in_states = None


class FSAPlanFactory(Plan, Supplemental):
    class Meta:
        model = models.LifeADDDependentPlan


class ParkingTransitPlanFactory(Plan, Supplemental):
    class Meta:
        model = models.ParkingTransitPlan


class HSAPlanFactory(Plan, Supplemental):
    class Meta:
        model = models.HSAPlan


class Employee401KPlanFactory(Plan, Supplemental):
    class Meta:
        model = models.HSAPlan


class SupplumentalInsurancePlanFactory(Plan, Supplemental):
    class Meta:
        model = models.SupplumentalInsurancePlan


class LongTermCarePlanFactory(Plan, Supplemental):
    class Meta:
        model = models.LongTermCarePlan


class OtherPlanFactory(Plan, Supplemental):
    class Meta:
        model = models.OtherPlan


class CancerPlanFactory(Plan, Supplemental):
    class Meta:
        model = models.CancerPlan


class CriticalIllnessPlanFactory(Plan, Supplemental):
    class Meta:
        model = models.CriticalIllnessPlan

    payout_amount = 100000


class PlanTierPremiumFactory(factory.Factory):
    class Meta:
        model = models.PlanTierPremium
        abstract = True

    tier_type = factory.Iterator(models.TIER_TYPES)
    premium = 200
    employer_portion = 150
    employee_portion = 50
    flat_amount = 75
    multiplier = 2.50


class MedicalPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(MedicalPlanFactory)


class DentalPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(DentalPlanFactory)


class VisionPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(VisionPlanFactory)


class EAPPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(EAPPlanFactory)


class LTDPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(LTDPlanFactory)


class LifeADDPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(LifeADDPlanFactory)


class LifeADDDepenentPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(LifeADDDependentPlanFactory)


class STDPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(STDPlanFactory)


class FSAPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(FSAPlanFactory)


class ParkingTransitPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(ParkingTransitPlanFactory)


class HSAPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(HSAPlanFactory)


class Employee401KPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(Employee401KPlanFactory)


class SupllementalInsurancePlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(SupplumentalInsurancePlanFactory)


class LongTermCarePlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(LongTermCarePlanFactory)


class OtherPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(OtherPlanFactory)


class CancerPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(CancerPlanFactory)


class CriticalIllnessPlanTierPremiumFactory(PlanTierPremiumFactory):

    plan = factory.SubFactory(CriticalIllnessPlanFactory)


# Premiums
class AgeBandedPremiumFactory(factory.Factory):
    class Meta:
        model = models.AgeBandedPremium

    low = 40
    high = 55
    premium = 100000
    plan = factory.SubFactory(SupplumentalInsurancePlanFactory)
