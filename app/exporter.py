# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from datetime import date


class Exporter(object):

    def __init__(self, employee):
        self.employee = employee

    def all(self):
        return ''

    def demographics(self):
        dct = {}
        employee = self.employee
        dct['trans_date'] = date.today()
        dct['group_id'] = employee.group_id
        dct['relationship_code'] = 'M'
        dct['employee_id'] = employee.employee_number
        dct['last_name'] = employee.last_name
        dct['first_name'] = employee.first_name
        dct['gender_code'] = employee.gender
        dct['date_of_birth'] = employee.dob.strftime('%Y%m%d')
        dct['street_1'] = employee.address.street_1
        dct['street_2'] = employee.address.street_2
        dct['city'] = employee.address.city
        dct['state'] = employee.address.state
        dct['zip_code'] = employee.address.zip_code
        dct['date_of_hire'] = employee.hire_date.strftime('%Y%m%d')
        dct['employee_effective_date'] = (employee.effective_date
                                          .strftime("%Y%m%d"))

        template = (
            '{trans_date:8}{group_id:8}{relationship_code:1}{employee_id:9}'
            '{last_name:35}{first_name:15}{gender_code:1}{date_of_birth:8}'
            '{street_1:30}{street_2:30}{city:19}{state:2}{zip_code:11}'
            '{date_of_hire:8}{employee_effective_date:8}'
                    )
        return template.format(dct)

    def bill_group(self):
        dct = {}
        employee = self.employee
        dct['sub_group_effective_date'] = (employee.sub_group_effective_date
                                           .strftime("%Y%m%d"))
        dct['sub_group_id'] = employee.sub_group_id
        template = '{sub_group_effective_date:8}{sub_group_id:4}'

        return template.format(dct)

    def employment(self):
        dct = {}
        employee = self.employee
        dct['location_effective_date'] = employee.location_effective_date
        dct['location_id'] = employee.location_id
        dct['location_description'] = employee.location_description
        template = (
            '{location_effective_date:8}{location_id:8}'
            '{location_description:23}'
                    )
        return template.format(dct)

    def salary(self):
        dct = {}
        employee = self.employee
        dct['salary_effective_date'] = employee.salary_effective_date
        dct['salary_mode'] = employee.salary_mode
        dct['salary'] = employee.salary
        dct['additional_comp_1_effective_date'] = ''
        dct['additional_comp_1_salary_mode'] = ''
        dct['additional_comp_1_type'] = ''
        dct['additional_comp_2_effective_date'] = ''
        dct['additional_comp_2_salary_mode'] = ''
        dct['additional_comp_2_type'] = ''
        dct['additional_comp_3_effective_date'] = ''
        dct['additional_comp_3_salary_mode'] = ''
        dct['additional_comp_3_type'] = ''
        dct['additional_comp_4_effective_date'] = ''
        dct['additional_comp_4_salary_mode'] = ''
        dct['additional_comp_4_type'] = ''
        template = (
            '{salary_effective_date:8}{salary_mode:1}{salary:16}'
            '{additional_comp_1_effective_date:8}'
            '{additional_comp_1_salary_mode:1}{additional_comp_1_type:16}'
            '{additional_comp_2_effective_date:8}'
            '{additional_comp_2_salary_mode:1}{additional_comp_2_type:16}'
            '{additional_comp_3_effective_date:8}'
            '{additional_comp_3_salary_mode:1}{additional_comp_3_type:16}'
            '{additional_comp_4_effective_date:8}'
            '{additional_comp_4_salary_mode:1}{additional_comp_4_type:16}'
        )
        return template.format(dct)

    def klass(self):
        dct = {}
        employee = self.employee
        dct['class_effective_date'] = employee.location_effective_date
        dct['class_id'] = employee.location_id
        template = (
            '{location_effective_date:8}{location_id:8}'
            '{location_description:23}'
                    )
        return template.format(dct)

    def smoking(self):
        return ''

    def dental(self):
        return ''

    def basic_life(self):
        return ''

    def basic_ad_and_d(self):
        return ''

    def basic_std(self):
        return ''

    def basic_ltd(self):
        return ''

    def voluntary_term_life_coverage_employee(self):
        return ''

    def voluntary_term_life_coverage_spouse(self):
        return ''

    def voluntary_term_life_coverage_dependent(self):
        return ''

    def voluntary_ad_and_d_coverage_employee(self):
        return ''

    def voluntary_ad_and_d_coverage_spouse(self):
        return ''

    def voluntary_ad_and_d_coverage_dependent(self):
        return ''

    def voluntary_std(self):
        return ''

    def voluntary_ltd(self):
        return ''

    def voluntary_employee_children_critical_illness(self):
        return ''

    def voluntary_spouse_critical_illness(self):
        return ''

    def voluntary_eployee_critical_illness_flat_amount(self):
        return ''

    def basic_dependent_life(self):
        return ''

    def special_risk_voluntary_ad_and_d_employee(self):
        return ''

    def eap_ltd_flat(self):
        return ''

    def basic_accident(self):
        return ''

    def voluntary_accident(self):
        return ''
