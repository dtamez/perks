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
import factory.fuzzy
from faker import Faker
from faker.providers import BaseProvider
from random import choice
from sqlalchemy_utils.types.choice import Choice

from app import models


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


class UserRoleFactory(factory.Factory):
    class Meta:
        model = models.UserRoles

    user_id = factory.SubFactory(UserFactory)
    role_id = factory.SubFactory(RoleFactory)


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

    code = fake.word()
    description = fake.sentence()
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
    salary_mode = Choice('annually', 'Annually')
    phone = fake.phone()
    alternate_phone = fake.phone()
    emergency_contact_phone = fake.phone()
    emergency_contact_name = fake.name()
    emergency_contact_relationship = choice(['spouse', 'son', 'daughter'])

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


class BeneficiaryFactory(factory.Factory):
    class Meta:
        model = models.Beneficiary

    beneficiary_type = Choice(*choice(models.BENEFICIARY_TYPES))
    #  plan = factory.SubFactory(PlanFactory)


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


#  class Plan(factory.Factory):
    #  code = factory.Faker('word')
    #  name = factory.Sequence(lambda n: 'plan%s' % n)
    #  cust_service_phone = fake.phone()
    #  website = factory.Faker('url')
    #  not_available_in = []


#  class Core(factory.Factory):
    #  group_number = '33387-01'
    #  original_effective_date = factory.Faker('date')
    #  renewal_date = factory.Faker('date')
    #  existing = True
    #  list_billed = True
    #  doctor_selection_required = False
    #  account_rep_name = factory.Faker('name')
    #  cobra_eligible = True
    #  pre_tax = True


#  class Group(factory.Factory):
    #  minimum_benefit = 50000
    #  maximum_benefit = 100000


#  class Supplemental(factory.Factory):
    #  pass


#  class MedicalPlanFactory(Plan, Core):
    #  class Meta:
        #  model = models.MedicalPlan

    #  self_funded = False


#  class DentalPlanFactory(Plan, Core):
    #  class Meta:
        #  model = models.DentalPlan


#  class VisionPlanFactory(Plan, Core):
    #  class Meta:
        #  model = models.VisionPlan


#  class EAPPlanFactory(Plan, Group):
    #  class Meta:
        #  model = models.EAPPlan


#  class LTDPlanFactory(Plan, Group):
    #  class Meta:
        #  model = models.LTDPlan


#  class LifeADDPlanFactory(Plan, Group):
    #  class Meta:
        #  model = models.LTDPlan


#  class STDPlanFactory(Plan, Group):
    #  class Meta:
        #  model = models.STDPlan

    #  payout_interval = Choice(*choice(models.PAYOUT_INTERVAL_TYPES))
    #  max_weekly_benefit = 10000
    #  max_monthly_benefit = 4000
    #  benefit_percentage = 10
    #  mandatory_in_states = None


#  class FSAMedicalPlanFactory(Plan, Supplemental):
    #  class Meta:
        #  model = models.FSAMedicalPlan


#  class ParkingTransitPlanFactory(Plan, Supplemental):
    #  class Meta:
        #  model = models.ParkingTransitPlan


#  class HSAPlanFactory(Plan, Supplemental):
    #  class Meta:
        #  model = models.HSAPlan


#  class Employee401KPlanFactory(Plan, Supplemental):
    #  class Meta:
        #  model = models.HSAPlan


#  class SupplumentalInsurancePlanFactory(Plan, Supplemental):
    #  class Meta:
        #  model = models.SupplumentalInsurancePlan


#  class LongTermCarePlanFactory(Plan, Supplemental):
    #  class Meta:
        #  model = models.LongTermCarePlan


#  class OtherPlanFactory(Plan, Supplemental):
    #  class Meta:
        #  model = models.OtherPlan


#  class CancerPlanFactory(Plan, Supplemental):
    #  class Meta:
        #  model = models.CancerPlan


#  class CriticalIllnessPlanFactory(Plan, Supplemental):
    #  class Meta:
        #  model = models.CriticalIllnessPlan

    #  payout_amount = 100000


#  class TieredPremiumFactory(factory.Factory):
    #  class Meta:
        #  model = models.TieredPremium
        #  abstract = True

    #  tier_type = Choice(*choice(models.FAMILY_TIER_TYPES))
    #  premium = 200
    #  employer_portion = 150
    #  employee_portion = 50
    #  flat_amount = 75
    #  percentage = 2.50


#  class MedicalTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(MedicalPlanFactory)


#  class DentalTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(DentalPlanFactory)


#  class VisionTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(VisionPlanFactory)


#  class EAPTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(EAPPlanFactory)


#  class LTDTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(LTDPlanFactory)


#  class LifeADDTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(LifeADDPlanFactory)


#  class STDTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(STDPlanFactory)


#  class FSATieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(FSAPlanFactory)


#  class ParkingTransitTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(ParkingTransitPlanFactory)


#  class HSATieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(HSAPlanFactory)


#  class Employee401KTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(Employee401KPlanFactory)


#  class SupllementalInsuranceTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(SupplumentalInsurancePlanFactory)


#  class LongTermCareTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(LongTermCarePlanFactory)


#  class OtherTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(OtherPlanFactory)


#  class CancerTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(CancerPlanFactory)


#  class CriticalIllnessTieredPremiumFactory(TieredPremiumFactory):

    #  plan = factory.SubFactory(CriticalIllnessPlanFactory)


# Premiums
#  class AgeBandedPremiumFactory(factory.Factory):
    #  class Meta:
        #  model = models.AgeBandedPremium

    #  low = 40
    #  high = 55
    #  premium = 100000
    #  plan = factory.SubFactory(SupplumentalInsurancePlanFactory)
