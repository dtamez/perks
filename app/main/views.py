# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from datetime import date
from decimal import Decimal
from operator import methodcaller
import json
import locale
import numpy as np

from flask import g, flash, request, render_template, redirect, url_for
from flask.views import MethodView
from flask_login import current_user, login_required
from jinja2 import Environment, PackageLoader
from logzero import logger
from werkzeug.datastructures import CombinedMultiDict
from werkzeug.datastructures import MultiDict

from . import main
from .. import db
from ..util import save_image_and_return_static_path
from ..forms import (
    AccidentPlanForm,
    AddressForm,
    BasicLifePlanForm,
    BeneficiariesForm,
    CancerPlanForm,
    CarrierForm,
    ChildStandaloneADDPlanForm,
    ChildVoluntaryLifePlanForm,
    ChildWholeLifePlanForm,
    CriticalIllnessPlanForm,
    ConfigurationForm,
    DentalPlanForm,
    DentalVisionPlanForm,
    DependentForm,
    EAPPlanForm,
    Employee401KPlanForm,
    EmployeeForm,
    EmployeeInfoForm,
    EnrollmentPeriodForm,
    EstateBeneficiaryForm,
    FSADependentCarePlanForm,
    FSAMedicalPlanForm,
    HRAPlanForm,
    HSAPlanForm,
    HospitalConfinementPlanForm,
    IdentityTheftPlanForm,
    LTDPlanForm,
    LifeEventsForm,
    LocationForm,
    LongTermCarePlanForm,
    MedicalDentalPlanForm,
    MedicalDentalVisionPlanForm,
    MedicalPlanForm,
    MedicalVisionPlanForm,
    OtherPlanForm,
    ParkingTransitPlanForm,
    PremiumForm,
    STDPlanForm,
    SpouseStandaloneADDPlanForm,
    SpouseVoluntaryLifePlanForm,
    SpouseWholeLifePlanForm,
    StandaloneADDPlanForm,
    SuccessionOfHeirsBeneficiaryForm,
    UniversalLifePlanForm,
    UploadForm,
    UserForm,
    VisionPlanForm,
    VoluntaryLifePlanForm,
    WholeLifePlanForm,
)
from ..importer import do_bulk_load
from ..models import (
    AccidentPlan,
    Address,
    AgeBasedReduction,
    BasicLifePlan,
    CancerPlan,
    Carrier,
    ChildStandaloneADDPlan,
    ChildVoluntaryLifePlan,
    ChildWholeLifePlan,
    CriticalIllnessPlan,
    Configuration,
    DentalPlan,
    DentalVisionBundlePlan,
    Dependent,
    DependentBeneficiary,
    EAPPlan,
    Election,
    Employee,
    Employee401KPlan,
    Enrollment,
    EnrollmentPeriod,
    EstateBeneficiary,
    FAMILY_TIER_TYPES,
    FSADependentCarePlan,
    FSAMedicalPlan,
    GENDER_TYPES,
    HRAPlan,
    HSAPlan,
    HospitalConfinementPlan,
    IdentityTheftPlan,
    LIFE_EVENT_TYPES,
    LTDPlan,
    LifeMixin,
    Location,
    LongTermCarePlan,
    MARITAL_STATUS_TYPES,
    MedicalDentalBundlePlan,
    MedicalDentalVisionBundlePlan,
    MedicalPlan,
    MedicalVisionBundlePlan,
    OtherPlan,
    ParkingTransitPlan,
    Plan,
    Premium,
    SMOKER_TYPES,
    STDPlan,
    SpouseStandaloneADDPlan,
    SpouseVoluntaryLifePlan,
    SpouseWholeLifePlan,
    StandaloneADDPlan,
    SuccessionOfHeirsBeneficiary,
    UniversalLifePlan,
    User,
    VisionPlan,
    VoluntaryLifePlan,
    WholeLifePlan,
)


env = Environment(loader=PackageLoader('app', 'templates'))
locale.setlocale(locale.LC_ALL, '')
gender_keys = [k for k, v in GENDER_TYPES]
smoker_keys = [k for k, v in SMOKER_TYPES]
family_tier_keys = [k for k, v in FAMILY_TIER_TYPES]


@main.before_request
def before_request():
    g.user = current_user


@main.context_processor
def inject_user():
    g.configuration = Configuration.query.get(1) or\
        type(
            'config',
            (object,),
            {
                'logo': 'static/images/logo.png',
                'company_text': 'Please update in admin configuration'})
    return dict(configuration=g.configuration)


@main.route('/')
@login_required
def index():
    g.active_tab = 'index'
    return render_template('index.html')


class AJAXCrudView(MethodView):

    def on_load(self, main):
        pass

    def on_save(self, main):
        pass

    def on_edit(self, main):
        pass

    def on_delete(self, main):
        pass

    def get(self, id):
        if id is None:
            return self.display_all()
        else:
            main = self.main['model'].query.get(id)
            self.on_load(main)
            template = env.get_template(self.main['template'])
            ctx = {self.main['single']: main, self.main['form_name']: self.main['form'](None, main)}
            for sub in self.subs:
                ctx[sub['form_name']] = sub['form'](None, getattr(main, sub['single']))

            return template.render(ctx)

    def post(self):
        forms = {}
        errors = []
        valid = True
        main = self.main['model']()
        form = self.main['form'](request.form)
        if not form.validate():
            logger.error(form.errors)
            valid = False
        forms[self.main['form_name']] = form
        form.populate_obj(main)
        main.id = None
        for sub in self.subs:
            obj = sub['model']()
            form = sub['form'](request.form)
            if not form.validate():
                logger.error(form.errors)
                valid = False
            forms[sub['form_name']] = form
            form.populate_obj(obj)
            if obj.id == '':
                obj.id = None
            db.session.add(obj)
            setattr(main, sub['single'], obj)

        template = env.get_template(self.main['template'])
        if not valid:
            return self.display_errors(main, forms, None)

        self.on_save(main)
        create_plan_premiums(main)

        try:
            db.session.add(main)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            errors.append(e.message)

        objects = self.main['model'].query.all()
        ctx = {self.main['plural']: objects, self.main['form_name']: self.main['form'](None)}
        for sub in self.subs:
            ctx[sub['form_name']] = sub['form'](None)
        ctx['errors'] = errors
        return template.render(ctx)

    def put(self, id):  # NOQA
        errors = []
        forms = {}
        valid = True
        main = self.main['model'].query.get(id)
        form = self.main['form'](request.form, obj=main)
        if hasattr(main, 'premium_matrix'):
            original_premium_matrix = main.premium_matrix
        if not form.validate():
            logger.error(form.errors)
            valid = False
        forms[self.main['form_name']] = form
        form.populate_obj(main)
        for sub in self.subs:
            obj = getattr(main, sub['single'])
            form = sub['form'](request.form, obj=obj)
            if not form.validate():
                logger.error(form.errors)
                valid = False
            forms[sub['form_name']] = form
            if not obj:
                obj = sub['model']()
                setattr(main, sub['single'], obj)
            form.populate_obj(obj)

        if not valid:
            return self.display_errors(main, forms, None)

        if hasattr(main, 'premium_matrix'):
            if main.premium_matrix != original_premium_matrix:
                # blow away existing premiumns
                main.premiums = []
                create_plan_premiums(main)

        self.on_edit(main)
        try:
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            errors.append(e.message)
            return self.display_errors(main, forms, errors)

        return self.display_all()

    def delete(self, id):
        obj = self.main['model'].query.get(id)
        self.on_delete(obj)
        db.session.delete(obj)
        db.session.commit()
        return self.display_all()

    def display_errors(self, main, forms, errors):
        ctx = {self.main['single']: main, 'errors': errors}
        ctx.update(forms)
        template = env.get_template(self.main['template'])
        return template.render(ctx)

    def display_all(self):
        if hasattr(self.main, 'plantype'):
            objects = self.main['model'].query.filter_by('plantype' == self.main['plantype']).all()
        else:
            objects = self.main['model'].query.all()
        template = env.get_template(self.main['template'])
        ctx = {self.main['plural']: objects, self.main['form_name']: self.main['form'](None)}
        for sub in self.subs:
            ctx[sub['form_name']] = sub['form'](None)
        return template.render(ctx)


def get_age_bands_from_matrix(s):
    s = s.replace(' ', '')
    if '-' in s:
        vals = s.split('-')
        if len(vals) == 2 and vals[0].strip().isdigit() and vals[1].strip().isdigit():
            return int(vals[0].strip()), int(vals[1].strip())
    elif '+' in s:
        vals = s.split('+')
        if len(vals) == 2 and vals[0].strip().isdigit():
            return int(vals[0].strip()), None

    return None


def create_plan_premiums(plan):  # NOQA
    if not hasattr(plan, 'premium_matrix'):
        return
    pr_matrix = plan.premium_matrix
    # single premium
    if isinstance(pr_matrix, np.int64):
        premium = Premium(plan=plan, amount=pr_matrix)
        db.session.add(premium)
        return
    # many premiums
    pr_matrix = pr_matrix.replace(' ', '')
    matrix = pr_matrix.split('\r\n')
    for idx, line in enumerate(matrix):
        matrix[idx] = line.split(',')
    # Gender, Age, Age bands, Smoker, Family Tier, rate%, $amount
    for line in matrix:
        premium = Premium(plan=plan)
        logger.debug('creating {} dimensional premium'.format(len(line)))
        for dimension in line:
            age_bands = get_age_bands_from_matrix(dimension)
            logger.debug('age_bands: {}'.format(age_bands))
            if dimension in gender_keys:
                premium.gender = unicode(dimension)
            elif dimension in smoker_keys:
                premium.smoker_status = unicode(dimension)
            elif dimension in family_tier_keys:
                premium.family_tier = unicode(dimension)
            elif dimension.endswith('K'):
                premium.payout_amount = int(dimension[:-1]) * 1000
            elif dimension.isdigit():
                premium.age = int(dimension)
            elif age_bands:
                #  tier = get_or_create(db.session, AgeBandedTier, premium=premium, low=age_bands[0], high=age_bands[1])
                premium.age_band_low = age_bands[0]
                premium.age_band_high = age_bands[1]
                #  premium.age_banded_tier = tier
            elif dimension.startswith('$'):
                premium.amount = Decimal(dimension[1:])
            elif dimension.endswith('%'):
                premium.rate = Decimal(dimension[:-1])
            else:
                raise Exception("Invalid premium matrix dimension value: .".format(dimension))
        db.session.add(premium)


def create_age_based_reductions(plan, data):
    lines = data.split('\n')
    for idx, line in enumerate(lines):
        lines[idx] = line.split(',')

    for line in lines:
        abr = AgeBasedReduction(plan=plan, age=line[0], percentage=Decimal(line[1]))
        db.session.add(abr)


# ENROLL
@main.route('/enroll')
@login_required
def enroll():
    employee = Employee.query.join(User).filter(
        User.id == g.user.id).first()
    if not employee:
        flash("You must be an employee in order to enroll.", 'error')
        return redirect(url_for('main.index'))
    enrollment = Enrollment.query.filter(
        Enrollment.employee_id == employee.id).first()
    if not enrollment:
        enrollment = Enrollment()
        enrollment.employee_id = employee.id
        db.session.add(enrollment)
        db.session.commit()

    return redirect(url_for('main.enroll_life_events'))


@main.route('/enroll/life_events', methods=['GET', 'POST'])
@login_required
def enroll_life_events():
    g.active_tab = 'enroll'
    g.active_step = 'life'

    employee = Employee.query.join(User).filter(User.id == g.user.id).first()
    enrollment = Enrollment.query.filter(Enrollment.employee_id == employee.id).first()

    return render_template('enroll/life_events.html', life_event=enrollment)


@main.route('/enroll/dependents', methods=['GET', 'POST'])
@login_required
def enroll_dependents():
    g.active_tab = 'enroll'
    g.active_step = 'dependents'
    employee = Employee.query.join(User).filter(
        User.id == g.user.id).first()
    dependents = employee.dependents
    dependents.sort(key=lambda d: d.dob)
    return render_template('enroll/dependents.html',
                           dependents=dependents,
                           dependent_form=DependentForm(),
                           address_form=AddressForm(),
                           employee=employee,
                           )


def get_selections(plans, enrollment):
    enrollment_id = enrollment.id
    selections = []
    for plan in plans:
        selection = {'plan_name': plan.name,
                     'plan_id': plan.id,
                     'available': True,
                     'election_label': 'No Coverage'}
        # if this plan has a required plan that is not chosen disable this plan
        available = True
        if plan.required_plan:
            for elec in enrollment.elections:
                if elec.plan.id == plan.required_plan.id and elec.premium:
                    break
            else:
                selection['election_label'] = 'Not available without enrolling in {}'.format(plan.required_plan.name)
                available = False
                selection['available'] = False
        selections.append(selection)
        if not available:
            continue
        election = Election.query.filter(
            Election.enrollment_id == enrollment_id,
            Election.plan_id == plan.id).first()
        if election:
            selection['amount'] = election.employee_cost
        if election and election.elected:
            selection['election_label'] = 'Enrolled'
        elif election and election.amount:
            selection['election_label'] = election.amount
        elif election and election.premium:
            selection['election_label'] = (election.premium.family_tier.value)
    return selections


@main.route('/enroll/core', methods=['GET'])
@login_required
def enroll_core():
    g.active_tab = 'enroll'
    g.active_step = 'core'
    employee = Employee.query.join(User).filter(
        User.id == g.user.id).first()
    # TODO: 2017-01-03 Eventually want to have an 'active' enrollment
    # or enrollment periods
    enrollment = Enrollment.query.filter(
        Enrollment.employee_id == employee.id).one()
    # get all medical plans that are available
    medical_plans = MedicalPlan.query.filter(Plan.active == True).all()
    medical_selections = get_selections(medical_plans, enrollment)
    dental_plans = DentalPlan.query.filter(Plan.active == True).all()
    dental_selections = get_selections(dental_plans, enrollment)
    vision_plans = VisionPlan.query.filter(Plan.active == True).all()
    vision_selections = get_selections(vision_plans, enrollment)
    medical_dental_plans = MedicalDentalBundlePlan.query.filter(Plan.active == True).all()
    medical_dental_selections = get_selections(medical_dental_plans, enrollment)
    medical_vision_plans = MedicalVisionBundlePlan.query.filter(Plan.active == True).all()
    medical_vision_selections = get_selections(medical_vision_plans, enrollment)
    medical_dental_vision_plans = MedicalDentalVisionBundlePlan.query.filter(Plan.active == True).all()
    medical_dental_vision_selections = get_selections(medical_dental_vision_plans, enrollment)
    dental_vision_plans = DentalVisionBundlePlan.query.filter(Plan.active == True).all()
    dental_vision_selections = get_selections(dental_vision_plans, enrollment)
    ctx = {'medical_selections': medical_selections,
           'dental_selections': dental_selections,
           'vision_selections': vision_selections,
           'medical_dental_selections': medical_dental_selections,
           'medical_vision_selections': medical_vision_selections,
           'medical_dental_vision_selections': medical_dental_vision_selections,
           'dental_vision_selections': dental_vision_selections,
           }
    return render_template('enroll/core.html', **ctx)


@main.route('/enroll/group', methods=['GET'])
@login_required
def enroll_group():
    g.active_tab = 'enroll'
    g.active_step = 'group'
    employee = Employee.query.join(User).filter(User.id == g.user.id).first()
    # TODO: 2017-01-03 Eventually want to have an 'active' enrollment
    # or enrollment periods
    enrollment = Enrollment.query.filter(Enrollment.employee_id == employee.id).one()
    # get all group plans that are available
    life_add_plans = BasicLifePlan.query.filter(Plan.active == True).all()
    life_add_selections = get_selections(life_add_plans, enrollment)
    voluntary_life_plans = VoluntaryLifePlan.query.filter(Plan.active == True).all()
    voluntary_life_plans.sort(key=methodcaller('sort_value'))
    voluntary_life_selections = get_selections(voluntary_life_plans, enrollment)
    spouse_voluntary_life_plans = SpouseVoluntaryLifePlan.query.filter(Plan.active == True).all()
    spouse_voluntary_life_selections = get_selections(spouse_voluntary_life_plans, enrollment)
    child_voluntary_life_plans = ChildVoluntaryLifePlan.query.filter(Plan.active == True).all()
    child_voluntary_life_selections = get_selections(child_voluntary_life_plans, enrollment)
    whole_life_plans = WholeLifePlan.query.filter(Plan.active == True).all()
    whole_life_plans.sort(key=methodcaller('sort_value'))
    whole_life_selections = get_selections(whole_life_plans, enrollment)
    universal_life_plans = UniversalLifePlan.query.filter(Plan.active == True).all()
    universal_life_selections = get_selections(universal_life_plans, enrollment)
    standalone_add_plans = StandaloneADDPlan.query.filter(Plan.active == True).all()
    standalone_add_plans.sort(key=methodcaller('sort_value'))
    standalone_add_selections = get_selections(standalone_add_plans, enrollment)

    ltd_plans = LTDPlan.query.filter(Plan.active == True).all()
    ltd_selections = get_selections(ltd_plans, enrollment)
    std_plans = STDPlan.query.filter(Plan.active == True).all()
    std_selections = get_selections(std_plans, enrollment)

    fsa_plans = FSAMedicalPlan.query.filter(Plan.active == True).all()
    fsa_selections = get_selections(fsa_plans, enrollment)

    hsa_plans = HSAPlan.query.filter(Plan.active == True).all()
    hsa_selections = get_selections(hsa_plans, enrollment)
    hra_plans = HRAPlan.query.filter(Plan.active == True).all()
    hra_selections = get_selections(hra_plans, enrollment)
    e401k_plans = Employee401KPlan.query.filter(Plan.active == True).all()
    e401k_selections = get_selections(e401k_plans, enrollment)

    ltc_plans = LongTermCarePlan.query.filter(Plan.active == True).all()
    ltc_selections = get_selections(ltc_plans, enrollment)
    eap_plans = EAPPlan.query.filter(Plan.active == True).all()
    eap_selections = get_selections(eap_plans, enrollment)
    ctx = {'life_add_selections': life_add_selections,
           'voluntary_life_selections': voluntary_life_selections,
           'spouse_voluntary_life_selections': spouse_voluntary_life_selections,
           'child_voluntary_life_selections': child_voluntary_life_selections,
           'whole_life_selections': whole_life_selections,
           'universal_life_selections': universal_life_selections,
           'standalone_add_selections': standalone_add_selections,

           'ltd_selections': ltd_selections,
           'std_selections': std_selections,

           'fsa_selections': fsa_selections,
           'hsa_selections': hsa_selections,
           'hra_selections': hra_selections,
           'e401k_selections': e401k_selections,

           'ltc_selections': ltc_selections,
           'eap_selections': eap_selections,
           }
    return render_template('enroll/group.html', **ctx)


@main.route('/enroll/supplemental', methods=['GET'])
@login_required
def enroll_supplemental():
    g.active_tab = 'enroll'
    g.active_step = 'supplemental'
    employee = Employee.query.join(User).filter(User.id == g.user.id).first()
    # TODO: 2017-01-03 Eventually want to have an 'active' enrollment
    # or enrollment periods
    enrollment = Enrollment.query.filter(Enrollment.employee_id == employee.id).one()
    # get all group plans that are available
    # TODO: 2017-01-05 Figure out way to generate these dynamically
    critical_plans = CriticalIllnessPlan.query.filter(Plan.active == True).all()
    critical_selections = get_selections(critical_plans, enrollment)
    cancer_plans = CancerPlan.query.filter(Plan.active == True).all()
    cancer_selections = get_selections(cancer_plans, enrollment)
    accident_plans = AccidentPlan.query.filter(Plan.active == True).all()
    accident_selections = get_selections(accident_plans, enrollment)
    hospital_confinement_plans = HospitalConfinementPlan.query.filter(Plan.active == True).all()
    hospital_confinement_selections = get_selections(hospital_confinement_plans, enrollment)
    parking_transit_plans = ParkingTransitPlan.query.filter(Plan.active == True).all()
    parking_transit_selections = get_selections(parking_transit_plans, enrollment)
    identity_theft_plans = IdentityTheftPlan.query.filter(Plan.active == True).all()
    identity_theft_selections = get_selections(identity_theft_plans, enrollment)
    ctx = {'critical_selections': critical_selections,
           'cancer_selections': cancer_selections,
           'accident_selections': accident_selections,
           'hospital_confinement_selections': hospital_confinement_selections,
           'parking_transit_selections': parking_transit_selections,
           'identity_theft_selections': identity_theft_selections,
    }  # NOQA
    return render_template('enroll/supplemental.html', **ctx)


class EnrollPlanAJAXView(MethodView):

    def get(self, id):
        employee = Employee.query.join(User).filter(
            User.id == g.user.id).first()
        if id is None:
            return self.display_all()
        else:
            # displaying a form to edit the election for this plan (id)
            plan = Plan.query.get(id)
            enrollment = Enrollment.query.filter(Enrollment.employee_id == employee.id).first()
            election = Election.query.filter(Election.enrollment_id == enrollment.id,
                                             Election.plan_id == plan.id).first()
            if not election:
                election = Election()
                election.plan_id = plan.id
                election.enrollment_id = enrollment.id
                val = '|'
            else:
                # TODO: this is a hack for amount supplied - maybe create plan specific methods to derive 'val'?
                if election.premium_id:
                    val = '{}|{}'.format(election.amount, election.premium_id)
                else:
                    val = election.amount
            form_class = plan.get_election_form()
            election_form = form_class(obj=election)
            election_form.selection.choices = plan.get_premium_choices(val, employee)
            template = env.get_template(self.template_name)
            ctx = {'election': election,
                   'employee': employee,
                   'plan_id': id,
                   'summary': False,
                   'election_form': election_form}

            if isinstance(plan, LifeMixin):
                dep_options, estate_option, heirs_option = get_beneficiary_options(plan, employee)
                deps_dict = {'dependent_beneficiaries': dep_options}
                beneficiaries_form = BeneficiariesForm(data=MultiDict(deps_dict))
                beneficiaries_form.estate_beneficiary = EstateBeneficiaryForm(obj=estate_option)
                beneficiaries_form.succession_of_heirs_beneficiary = SuccessionOfHeirsBeneficiaryForm(obj=heirs_option)

                ctx.update({'beneficiaries_form': beneficiaries_form})

            return template.render(ctx)

    def post(self):
        employee = Employee.query.join(User).filter(User.id == g.user.id).first()
        election = Election()
        election.id = None
        plan_id = request.form['plan_id']
        plan = Plan.query.get(plan_id)
        form_class = plan.get_election_form()
        form = form_class(request.form)
        form.selection.choices = plan.get_premium_choices(request.values['selection'], employee)
        form.populate_obj(election)
        plan.populate_election(form.selection.data, election, employee)
        db.session.add(election)
        db.session.commit()
        if isinstance(plan, LifeMixin):
            beneficiaries_form = BeneficiariesForm(request.form)
            estate_beneficiary = EstateBeneficiary(plan_id=plan_id)
            beneficiaries_form.estate_beneficiary.form.populate_obj(estate_beneficiary)
            estate_beneficiary.id = None
            heirs_beneficiary = SuccessionOfHeirsBeneficiary(plan_id=plan_id, )
            beneficiaries_form.succession_of_heirs_beneficiary.form.populate_obj(heirs_beneficiary)
            heirs_beneficiary.id = None
            if estate_beneficiary.percentage > 0:
                db.session.add(estate_beneficiary)
            if heirs_beneficiary.percentage > 0:
                db.session.add(heirs_beneficiary)

            deps_map = {dep.id: dep for dep in employee.dependents}
            for entry in beneficiaries_form.dependent_beneficiaries.entries:
                dependent_beneficiary = DependentBeneficiary(plan_id=plan_id, employee_id=employee.id)
                entry.form.populate_obj(dependent_beneficiary)
                dependent_beneficiary.id = None
                if dependent_beneficiary.percentage > 0:
                    dependent_beneficiary.dependent = deps_map[dependent_beneficiary.dependent_id]
                    db.session.add(dependent_beneficiary)
            db.session.commit()
        self.do_extra_persistence(employee, request, None)

        return self.display_all()

    def put(self, id):  # NOQA
        beneficiaries_form = BeneficiariesForm(request.form)
        employee = Employee.query.join(User).filter(User.id == g.user.id).first()
        plan = Plan.query.get(id)
        form_class = plan.get_election_form()
        form = form_class(request.form)
        form.selection.choices = plan.get_premium_choices(request.values['selection'], employee)
        assert(form.enrollment_id.data)
        enrollment = Enrollment.query.get(form.enrollment_id.data)
        election = Election.query.filter(Election.enrollment_id == enrollment.id, Election.plan_id == id).one()
        form.populate_obj(election)
        plan.populate_election(form.selection.data, election, employee)
        db.session.add(election)
        if election.selection == 'DE':
            # need to decline any dependent plans
            plans = Plan.query.filter_by(active=True)
            for pln in plans:
                if pln.required_plan_id == id:
                    for elc in enrollment.elections:
                        if elc.plan == plan:
                            if elc.selection != 'DE':
                                elc.selection = 'DE'
                                db.session.add(elc)

        db.session.commit()

        if isinstance(plan, LifeMixin):
            beneficiaries_form = BeneficiariesForm(request.form)
            # for each beneficiary returned ther are 4 possibilities:
            #   no original = add new
            #   values are the same = do nothing
            #   new value == 0 = delete
            #   values have changed = update
            estate_id = beneficiaries_form.estate_beneficiary.data['id']
            if estate_id:
                estate_beneficiary = EstateBeneficiary.query.get(estate_id)
                original_type = estate_beneficiary.beneficiary_type
                original_percentage = estate_beneficiary.percentage
            else:
                estate_beneficiary = EstateBeneficiary(plan_id=plan.id)
            beneficiaries_form.estate_beneficiary.form.populate_obj(estate_beneficiary)
            if not estate_id:
                if estate_beneficiary.percentage > 0:
                    db.session.add(estate_beneficiary)
            else:
                if ((original_percentage != estate_beneficiary.percentage) or
                        (original_type != estate_beneficiary.beneficiary_type)):
                    if estate_beneficiary.percentage == 0:
                        db.session.delete(estate_beneficiary)
                    else:
                        db.session.add(estate_beneficiary)

            heirs_id = beneficiaries_form.succession_of_heirs_beneficiary.data['id']
            if heirs_id:
                heirs_beneficiary = SuccessionOfHeirsBeneficiary.query.get(heirs_id)
                original_type = heirs_beneficiary.beneficiary_type
                original_percentage = heirs_beneficiary.percentage
            else:
                heirs_beneficiary = SuccessionOfHeirsBeneficiary(plan_id=plan.id)
            beneficiaries_form.succession_of_heirs_beneficiary.form.populate_obj(heirs_beneficiary)
            if not heirs_id:
                if heirs_beneficiary.percentage > 0:
                    db.session.add(heirs_beneficiary)
            else:
                if ((original_percentage != heirs_beneficiary.percentage) or
                        (original_type != heirs_beneficiary.beneficiary_type)):
                    if heirs_beneficiary.percentage == 0:
                        db.session.delete(heirs_beneficiary)
                    else:
                        db.session.add(heirs_beneficiary)

            deps_map = {dep.id: dep for dep in employee.dependents}
            for entry in beneficiaries_form.dependent_beneficiaries.entries:
                ben_id = entry.data['id']
                if ben_id:
                    dependent_beneficiary = DependentBeneficiary.query.get(ben_id)
                    original_type = dependent_beneficiary.beneficiary_type
                    original_percentage = dependent_beneficiary.percentage
                else:
                    dependent_beneficiary = DependentBeneficiary(plan_id=plan.id, employee_id=employee.id)

                dependent_beneficiary.dependent = deps_map[entry.data['dependent_id']]
                dependent_beneficiary.percentage = entry.data['percentage']
                dependent_beneficiary.beneficiary_type = entry.data['beneficiary_type']
                if not ben_id:
                    if dependent_beneficiary.percentage > 0:
                        db.session.add(dependent_beneficiary)
                else:
                    if ((original_type != dependent_beneficiary.beneficiary_type) or
                            (original_percentage != dependent_beneficiary.percentage)):
                        if dependent_beneficiary.percentage == 0:
                            del dependent_beneficiary
                        else:
                            db.session.add(dependent_beneficiary)
            db.session.commit()

        self.do_extra_persistence(employee, request, enrollment)

        return self.display_all()

    def do_extra_persistence(self, employee, request, enrollment=None):
        pass

    def display_all(self):
        employee = Employee.query.join(User).filter(User.id == g.user.id).first()
        plans = self.plan_class.query.all()
        if hasattr(self.plan_class(), 'sort_value'):
            plans.sort(key=methodcaller('sort_value'))

        enrollment = Enrollment.query.filter(Enrollment.employee_id == employee.id).one()
        selections = []
        for plan in plans:
            selection = {'plan_name': plan.name, 'plan_id': plan.id, 'election_label': 'Declined', 'available': True}
            selections.append(selection)
            election = Election.query.filter(Election.enrollment_id == enrollment.id,
                                             Election.plan_id == plan.id).first()
            # boolean
            if election and election.elected:
                selection['election_label'] = 'Enrolled'
                selection['amount'] = election.employee_cost
            # amount chosen/supplied
            elif election and election.amount:
                selection['amount'] = election.employee_cost
                selection['election_label'] = election.amount
            # tiered
            elif election and election.premium:
                selection['election_label'] = (election.premium.family_tier.value)
                selection['amount'] = election.employee_cost
            else:
                election = Election()
                election.plan = plan
                election.enrollment_id = enrollment.id
            form_class = plan.get_election_form()
            election_form = form_class()
            election_form.selection.choices = plan.get_premium_choices(election_form.data['selection'], employee)
        ctx = {'election_form': election_form,
               'election': election,
               'employee': employee,
               'summary': True,
               '{}_selections'.format(self.prefix): selections}
        return render_template(self.template_name, **ctx)


def get_beneficiary_options(plan, employee):
    # get all beneficiaries from the plan plus missing dependents, estate or heir options
    designated = plan.beneficiaries
    blank_estate = EstateBeneficiary(plan=plan, employee_id=employee.id)
    blank_heirs = SuccessionOfHeirsBeneficiary(plan=plan, employee_id=employee.id)

    estate_designated = [b for b in designated if isinstance(b, EstateBeneficiary)]
    heirs_designated = [b for b in designated if isinstance(b, SuccessionOfHeirsBeneficiary)]
    if estate_designated:
        estate_designated = estate_designated[0]
    if heirs_designated:
        heirs_designated = heirs_designated[0]
    deps_designated = [b for b in designated if isinstance(b, DependentBeneficiary)]
    dep_options = deps_designated[:]
    dep_ids_designated = [dep.dependent_id for dep in deps_designated]

    for dep in employee.dependents:
        if dep.id not in dep_ids_designated:
            dep_options.append(DependentBeneficiary(plan=plan, employee=employee, employee_id=employee.id,
                                                    dependent_id=dep.id, dependent=dep, percentage=0))

    dep_options.sort(key=lambda db: db.dependent.dob)
    return dep_options, estate_designated or blank_estate, heirs_designated or blank_heirs


@main.route('/update_totals/', methods=['GET'])
@login_required
def update_totals():
    from flask import session
    employee = Employee.query.join(User).filter(User.id == g.user.id).first()
    enrollment = Enrollment.query.filter(Enrollment.employee_id == employee.id).one()
    employer_total = 0
    employee_total = 0
    for election in enrollment.elections:
        logger.debug('{}: ER: {}'.format(election.plan.name, election.employer_cost))
        logger.debug('{}: EE: {}'.format(election.plan.name, election.employee_cost))
        employer_total += election.employer_cost
        employee_total += election.employee_cost

    logger.debug('ER Total: {}'.format(employer_total))
    logger.debug('EE Total: {}'.format(employee_total))
    session['employer_total'] = locale.currency(employer_total, grouping=True)
    session['employee_total'] = locale.currency(employee_total, grouping=True)
    totals = json.dumps({'employerTotal': session['employer_total'], 'employeeTotal': session['employee_total']})
    return totals


@main.route('/enroll/finalize', methods=['GET', 'POST'])
@login_required
def enroll_finalize():
    pass


@main.route('/messages')
@login_required
def messages():
    g.active_tab = 'messages'
    return render_template('messages/messages.html')


@main.route('/benefits')
@login_required
def benefits():
    g.active_tab = 'benefits'
    return render_template('benefits/benefits.html')


@main.route('/admin')
@login_required
def admin():
    g.active_tab = 'admin'
    # TODO: EG - Page redirection when loading admin page
    return redirect(url_for('main.admin_people'), )


@main.route('/admin/people', methods=['GET', 'POST'])
@login_required
def admin_people():
    g.active_tab = 'admin'
    g.active_step = 'people'
    employees = Employee.query.all()
    locations = Location.query.all()
    return render_template(
        'admin/people.html', marital_status_types=MARITAL_STATUS_TYPES,
        employee_form=EmployeeForm(), user_form=UserForm(),
        address_form=AddressForm(), location_form=LocationForm(),
        employees=employees, locations=locations)


@main.route('/admin/carriers', methods=['GET'])
@login_required
def admin_carriers():
    g.active_tab = 'admin'
    g.active_step = 'carriers'
    carriers = Carrier.query.all()
    form = CarrierForm()
    return render_template('admin/carriers.html', carriers=carriers,
                           carrier_form=form)


@main.route('/admin/enrollment_periods', methods=['GET'])
@login_required
def admin_enroll_dates():
    g.active_tab = 'admin'
    g.active_step = 'enroll_dates'
    enrollment_periods = EnrollmentPeriod.query.all()
    form = EnrollmentPeriodForm()
    return render_template('admin/enrollment_periods.html', enrollment_periods=enrollment_periods,
                           enrollment_period_form=form)


@main.route('/admin/core', methods=['GET'])
@login_required
def admin_core():
    g.active_tab = 'admin'
    g.active_step = 'core'
    medical_plans = MedicalPlan.query.all()
    medical_plan_form = MedicalPlanForm()
    dental_plans = DentalPlan.query.all()
    dental_plan_form = DentalPlanForm()
    vision_plans = VisionPlan.query.all()
    vision_plan_form = VisionPlanForm()
    medical_dental_vision_plans = MedicalDentalVisionBundlePlan.query.all()
    medical_dental_vision_plan_form = MedicalDentalVisionPlanForm()
    medical_dental_plans = MedicalDentalBundlePlan.query.all()
    medical_dental_plan_form = MedicalDentalPlanForm()
    medical_vision_plans = MedicalVisionBundlePlan.query.all()
    medical_vision_plan_form = MedicalVisionPlanForm()
    dental_vision_plans = DentalVisionBundlePlan.query.all()
    dental_vision_plan_form = DentalVisionPlanForm()
    return render_template('admin/core.html',
                           medical_plans=medical_plans,
                           medical_plan_form=medical_plan_form,
                           dental_plans=dental_plans,
                           dental_plan_form=dental_plan_form,
                           vision_plans=vision_plans,
                           vision_plan_form=vision_plan_form,
                           medical_dental_vision_plan_form=medical_dental_vision_plan_form,
                           medical_dental_vision_plans=medical_dental_vision_plans,
                           medical_dental_plan_form=medical_dental_plan_form,
                           medical_dental_plans=medical_dental_plans,
                           medical_vision_plan_form=medical_vision_plan_form,
                           medical_vision_plans=medical_vision_plans,
                           dental_vision_plan_form=dental_vision_plan_form,
                           dental_vision_plans=dental_vision_plans,
                           )


@main.route('/admin/group', methods=['GET', 'POST'])
@login_required
def admin_group():
    g.active_tab = 'admin'
    g.active_step = 'group'
    basic_life_plans = BasicLifePlan.query.all()
    basic_life_plan_form = BasicLifePlanForm()
    voluntary_life_plans = VoluntaryLifePlan.query.filter(VoluntaryLifePlan.plantype == 'voluntary_life').all()
    voluntary_life_plan_form = VoluntaryLifePlanForm()
    spouse_voluntary_life_plans = SpouseVoluntaryLifePlan.query.all()
    spouse_voluntary_life_plan_form = SpouseVoluntaryLifePlanForm()
    child_voluntary_life_plans = ChildVoluntaryLifePlan.query.all()
    child_voluntary_life_plan_form = ChildVoluntaryLifePlanForm()
    standalone_add_plans = StandaloneADDPlan.query.filter(StandaloneADDPlan.plantype == 'standalone_add').all()
    standalone_add_plan_form = StandaloneADDPlanForm()
    spouse_standalone_add_plans = SpouseStandaloneADDPlan.query.all()
    spouse_standalone_add_plan_form = SpouseStandaloneADDPlanForm()
    child_standalone_add_plans = ChildStandaloneADDPlan.query.all()
    child_standalone_add_plan_form = ChildStandaloneADDPlanForm()
    whole_life_plans = WholeLifePlan.query.all()
    whole_life_plan_form = WholeLifePlanForm()
    spouse_whole_life_plans = SpouseWholeLifePlan.query.all()
    spouse_whole_life_plan_form = SpouseWholeLifePlanForm()
    child_whole_life_plans = ChildWholeLifePlan.query.all()
    child_whole_life_plan_form = ChildWholeLifePlanForm()

    ltd_plans = LTDPlan.query.all()
    ltd_plan_form = LTDPlanForm()
    std_plans = STDPlan.query.all()
    std_plan_form = STDPlanForm()

    fsa_medical_plans = FSAMedicalPlan.query.filter(FSAMedicalPlan.plantype == 'fsa_medical').all()
    fsa_medical_plan_form = FSAMedicalPlanForm()
    fsa_dependent_care_plans = FSADependentCarePlan.query.all()
    fsa_dependent_care_plan_form = FSADependentCarePlanForm()
    hsa_plans = HSAPlan.query.all()
    hsa_plan_form = HSAPlanForm()
    hra_plans = HRAPlan.query.all()
    hra_plan_form = HRAPlanForm()

    e401k_plans = Employee401KPlan.query.all()
    e401k_plan_form = Employee401KPlanForm()
    ltc_plans = LongTermCarePlan.query.all()
    ltc_plan_form = LongTermCarePlanForm()

    eap_plans = EAPPlan.query.all()
    eap_plan_form = EAPPlanForm()
    return render_template('admin/group.html',
                           basic_life_plans=basic_life_plans,
                           basic_life_plan_form=basic_life_plan_form,
                           voluntary_life_plans=voluntary_life_plans,
                           voluntary_life_plan_form=voluntary_life_plan_form,
                           spouse_voluntary_life_plans=spouse_voluntary_life_plans,
                           spouse_voluntary_life_plan_form=spouse_voluntary_life_plan_form,
                           child_voluntary_life_plans=child_voluntary_life_plans,
                           child_voluntary_life_plan_form=child_voluntary_life_plan_form,
                           standalone_add_plans=standalone_add_plans,
                           standalone_add_plan_form=standalone_add_plan_form,
                           spouse_standalone_add_plans=spouse_standalone_add_plans,
                           spouse_standalone_add_plan_form=spouse_standalone_add_plan_form,
                           child_standalone_add_plans=child_standalone_add_plans,
                           child_standalone_add_plan_form=child_standalone_add_plan_form,
                           whole_life_plans=whole_life_plans,
                           whole_life_plan_form=whole_life_plan_form,
                           spouse_whole_life_plans=spouse_whole_life_plans,
                           spouse_whole_life_plan_form=spouse_whole_life_plan_form,
                           child_whole_life_plans=child_whole_life_plans,
                           child_whole_life_plan_form=child_whole_life_plan_form,

                           ltd_plans=ltd_plans,
                           ltd_plan_form=ltd_plan_form,
                           std_plans=std_plans,
                           std_plan_form=std_plan_form,

                           fsa_medical_plans=fsa_medical_plans,
                           fsa_medical_plan_form=fsa_medical_plan_form,
                           fsa_dependent_care_plans=fsa_dependent_care_plans,
                           fsa_dependent_care_plan_form=fsa_dependent_care_plan_form,
                           hsa_plans=hsa_plans,
                           hsa_plan_form=hsa_plan_form,
                           hra_plans=hra_plans,
                           hra_plan_form=hra_plan_form,

                           e401k_plans=e401k_plans,
                           e401k_plan_form=e401k_plan_form,
                           ltc_plans=ltc_plans,
                           ltc_plan_form=ltc_plan_form,

                           eap_plans=eap_plans,
                           eap_plan_form=eap_plan_form,
                           )


@main.route('/admin/supplemental', methods=['GET', 'POST'])
@login_required
def admin_supplemental():
    g.active_tab = 'admin'
    g.active_step = 'supplemental'
    critical_illness_plans = CriticalIllnessPlan.query.all()
    critical_illness_plan_form = CriticalIllnessPlanForm()
    cancer_plans = CancerPlan.query.all()
    cancer_plan_form = CancerPlanForm()
    accident_plans = AccidentPlan.query.all()
    accident_plan_form = AccidentPlanForm()
    hospital_confinement_plans = HospitalConfinementPlan.query.all()
    hospital_confinement_plan_form = HospitalConfinementPlanForm()
    parking_transit_plans = ParkingTransitPlan.query.all()
    parking_transit_plan_form = ParkingTransitPlanForm()
    identity_theft_plans = IdentityTheftPlan.query.all()
    identity_theft_plan_form = IdentityTheftPlanForm()
    other_plans = OtherPlan.query.all()
    other_plan_form = OtherPlanForm()
    return render_template(
        'admin/supplemental.html',
        critical_illness_plans=critical_illness_plans,
        critical_illness_plan_form=critical_illness_plan_form,
        cancer_plans=cancer_plans,
        cancer_plan_form=cancer_plan_form,
        accident_plans=accident_plans,
        accident_plan_form=accident_plan_form,
        hospital_confinement_plans=hospital_confinement_plans,
        hospital_confinement_plan_form=hospital_confinement_plan_form,
        parking_transit_plans=parking_transit_plans,
        parking_transit_plan_form=parking_transit_plan_form,
        identity_theft_plans=identity_theft_plans,
        identity_theft_plan_form=identity_theft_plan_form,
        other_plans=other_plans,
        other_plan_form=other_plan_form,
    )


@main.route('/admin/configuration', methods=['GET', 'POST'])
@login_required
def admin_configurator():
    image_path = static_path = _file = None
    g.active_tab = 'configuration'
    configuration_item = Configuration.query.get(1)
    form = ConfigurationForm(request.form)
    if request.method == 'GET':
        if configuration_item:
            form.company_text.data = configuration_item.company_text
    elif request.method == 'POST' and form.validate():
        configuration = configuration_item or Configuration()
        if request.files.get('logo').filename != '':
            image_path, static_path, _file = save_image_and_return_static_path(request)
        if static_path:
            configuration.logo = static_path
        configuration.company_text = form.company_text.data
        try:
            if not configuration_item:
                db.session.add(configuration)
            db.session.commit()
        except Exception:
            db.session.rollback()
        if image_path and _file:
            _file.save(image_path)
    return render_template(
        'admin/configuration.html', configuration_form=form)


def get_remaining_tier_choices(plan_id):
    # remove already chosen tiers from the dropdown list
    types_dict = {x[0]: x for x in FAMILY_TIER_TYPES}
    existing = [x.tier_type.code for x in Premium.query.filter(
        Premium.plan_id == plan_id).all()]
    diff = set(types_dict.keys()) - set(existing)
    return [types_dict[x] for x in diff]


@main.route('/admin/premiums', methods=['GET', 'POST'])
@login_required
def admin_premiums():
    g.active_tab = 'admin'
    g.active_step = 'premiums'
    plan_forms = []
    plans = Plan.query.all()
    for plan in plans:
        form = PremiumForm(data={'plan_id': plan.id})
        form.tier_type.choices = get_remaining_tier_choices(plan.id)
        plan_forms.append((plan, form))

    return render_template('admin/premiums.html', plan_forms=plan_forms)


# ADMIN Ajax views
class CarrierView(AJAXCrudView):
    main = {'model': Carrier, 'form': CarrierForm, 'class': 'Carrier',
            'form_class': 'CarrierForm', 'single': 'carrier',
            'plural': 'carriers', 'form_name': 'carrier_form',
            'template': '/admin/_carriers.html'}
    subs = []


class EnrollmentPeriodView(AJAXCrudView):
    main = {'model': EnrollmentPeriod, 'form': EnrollmentPeriodForm, 'class': 'EnrollmentPeriod',
            'form_class': 'EnrollmentPeriodForm', 'single': 'enrollment_period',
            'plural': 'enrollment_periods', 'form_name': 'enrollment_period_form',
            'template': '/admin/_enrollment_periods.html'}
    subs = []


class MedicalPlanView(AJAXCrudView):
    main = {'model': MedicalPlan, 'form': MedicalPlanForm,
            'class': 'MedicalPlan', 'form_class': 'MedicalPlanForm',
            'single': 'medical_plan', 'plural': 'medical_plans',
            'form_name': 'medical_plan_form',
            'template': '/admin/_medical_plans.html'}
    subs = []


class DentalPlanView(AJAXCrudView):
    main = {'model': DentalPlan, 'form': DentalPlanForm,
            'class': 'DentalPlan', 'form_class': 'DentalPlanForm',
            'single': 'dental_plan', 'plural': 'dental_plans',
            'form_name': 'dental_plan_form',
            'template': '/admin/_dental_plans.html'}
    subs = []


class VisionPlanView(AJAXCrudView):
    main = {'model': VisionPlan, 'form': VisionPlanForm,
            'class': 'VisionPlan', 'form_class': 'VisionPlanForm',
            'single': 'vision_plan', 'plural': 'vision_plans',
            'form_name': 'vision_plan_form',
            'template': '/admin/_vision_plans.html'}
    subs = []


class MedicalDentalVisionPlanView(AJAXCrudView):
    main = {'model': MedicalDentalVisionBundlePlan, 'form': MedicalDentalVisionPlanForm,
            'class': 'MedicalDentalVisionBundlePlan', 'form_class': 'MedicalDentalVisionPlanForm',
            'single': 'medical_dental_vision_plan', 'plural': 'medical_dental_vision_plans',
            'form_name': 'medical_dental_vision_plan_form',
            'template': '/admin/_medical_dental_vision_plans.html'}
    subs = []


class MedicalDentalPlanView(AJAXCrudView):
    main = {'model': MedicalDentalBundlePlan, 'form': MedicalDentalPlanForm,
            'class': 'MedicalDentalBundlePlan', 'form_class': 'MedicalDentalPlanForm',
            'single': 'medical_dental_plan', 'plural': 'medical_dental_plans',
            'form_name': 'medical_dental_plan_form',
            'template': '/admin/_medical_dental_plans.html'}
    subs = []


class MedicalVisionPlanView(AJAXCrudView):
    main = {'model': MedicalVisionBundlePlan, 'form': MedicalVisionPlanForm,
            'class': 'MedicalVisionBundlePlan', 'form_class': 'MedicalVisionPlanForm',
            'single': 'medical_vision_plan', 'plural': 'medical_vision_plans',
            'form_name': 'medical_vision_plan_form',
            'template': '/admin/_medical_vision_plans.html'}
    subs = []


class DentalVisionPlanView(AJAXCrudView):
    main = {'model': DentalVisionBundlePlan, 'form': DentalVisionPlanForm,
            'class': 'DentalVisionBundlePlan', 'form_class': 'DentalVisionPlanForm',
            'single': 'dental_vision_plan', 'plural': 'dental_vision_plans',
            'form_name': 'dental_vision_plan_form',
            'template': '/admin/_dental_vision_plans.html'}
    subs = []


class EAPPlanView(AJAXCrudView):
    main = {'model': EAPPlan, 'form': EAPPlanForm,
            'class': 'EAPPlan', 'form_class': 'EAPPlanForm',
            'single': 'eap_plan', 'plural': 'eap_plans',
            'form_name': 'eap_plan_form',
            'template': '/admin/_eap_plans.html'}
    subs = []


class LTDPlanView(AJAXCrudView):
    main = {'model': LTDPlan, 'form': LTDPlanForm,
            'class': 'LTDPlan', 'form_class': 'LTDPlanForm',
            'single': 'ltd_plan', 'plural': 'ltd_plans',
            'form_name': 'ltd_plan_form',
            'template': '/admin/_ltd_plans.html'}
    subs = []


class STDPlanView(AJAXCrudView):
    main = {'model': STDPlan, 'form': STDPlanForm,
            'class': 'STDPlan', 'form_class': 'STDPlanForm',
            'single': 'std_plan', 'plural': 'std_plans',
            'form_name': 'std_plan_form',
            'template': '/admin/_std_plans.html'}
    subs = []


class BasicLifePlanView(AJAXCrudView):
    main = {'model': BasicLifePlan, 'form': BasicLifePlanForm,
            'class': 'BasicLifePlan', 'form_class': 'BasicLifePlanForm',
            'single': 'basic_life_plan', 'plural': 'basic_life_plans',
            'form_name': 'basic_life_plan_form',
            'template': '/admin/_basic_life_plans.html'}
    subs = []


class WholeLifePlanView(AJAXCrudView):
    main = {'model': WholeLifePlan, 'form': WholeLifePlanForm,
            'class': 'WholeLifePlan', 'form_class': 'WholeLifePlanForm',
            'single': 'whole_life_plan', 'plural': 'whole_life_plans',
            'form_name': 'whole_life_plan_form',
            'template': '/admin/_whole_life_plans.html'}
    subs = []


class SpouseWholeLifePlanView(AJAXCrudView):
    main = {'model': SpouseWholeLifePlan, 'form': SpouseWholeLifePlanForm,
            'class': 'SpouseWholeLifePlan', 'form_class': 'SpouseWholeLifePlanForm',
            'single': 'spouse_whole_life_plan', 'plural': 'spouse_whole_life_plans',
            'form_name': 'spouse_whole_life_plan_form',
            'template': '/admin/_spouse_whole_life_plans.html'}
    subs = []


class ChildWholeLifePlanView(AJAXCrudView):
    main = {'model': ChildWholeLifePlan, 'form': ChildWholeLifePlanForm,
            'class': 'ChildWholeLifePlan', 'form_class': 'ChildWholeLifePlanForm',
            'single': 'child_whole_life_plan', 'plural': 'child_whole_life_plans',
            'form_name': 'child_whole_life_plan_form',
            'template': '/admin/_child_whole_life_plans.html'}
    subs = []


class UniversalLifePlanView(AJAXCrudView):
    main = {'model': UniversalLifePlan, 'form': UniversalLifePlanForm,
            'class': 'UniversalLifePlan', 'form_class': 'UniversalLifePlanForm',
            'single': 'universal_life_plan', 'plural': 'universal_life_plans',
            'form_name': 'universal_life_plan_form',
            'template': '/admin/_universal_life_plans.html'}
    subs = []


class VoluntaryLifePlanView(AJAXCrudView):
    main = {'model': VoluntaryLifePlan, 'form': VoluntaryLifePlanForm,
            'class': 'VoluntaryLifePlan', 'form_class': 'VoluntaryLifePlanForm',
            'single': 'voluntary_life_plan', 'plural': 'voluntary_life_plans',
            'form_name': 'voluntary_life_plan_form',
            'plantype': 'voluntary_life',
            'template': '/admin/_voluntary_life_plans.html'}
    subs = []


class SpouseVoluntaryLifePlanView(AJAXCrudView):
    main = {'model': SpouseVoluntaryLifePlan, 'form': SpouseVoluntaryLifePlanForm,
            'class': 'SpouseVoluntaryLifePlan', 'form_class': 'SpouseVoluntaryLifePlanForm',
            'single': 'spouse_voluntary_life_plan', 'plural': 'spouse_voluntary_life_plans',
            'form_name': 'spouse_voluntary_life_plan_form',
            'template': '/admin/_spouse_voluntary_life_plans.html'}
    subs = []


class ChildVoluntaryLifePlanView(AJAXCrudView):
    main = {'model': ChildVoluntaryLifePlan, 'form': ChildVoluntaryLifePlanForm,
            'class': 'ChildVoluntaryLifePlan', 'form_class': 'ChildVoluntaryLifePlanForm',
            'single': 'child_voluntary_life_plan', 'plural': 'child_voluntary_life_plans',
            'form_name': 'child_voluntary_life_plan_form',
            'template': '/admin/_child_voluntary_life_plans.html'}
    subs = []


class StandaloneADDPlanView(AJAXCrudView):
    main = {'model': StandaloneADDPlan, 'form': StandaloneADDPlanForm,
            'class': 'StandaloneADDPlan', 'form_class': 'StandaloneADDPlanForm',
            'single': 'standalone_add_plan', 'plural': 'standalone_add_plans',
            'form_name': 'standalone_add_plan_form',
            'plantype': 'standalone_add',
            'template': '/admin/_standalone_add_plans.html'}
    subs = []


class SpouseStandaloneADDPlanView(AJAXCrudView):
    main = {'model': SpouseStandaloneADDPlan, 'form': SpouseStandaloneADDPlanForm,
            'class': 'SpouseStandaloneADDPlan', 'form_class': 'SpouseStandaloneADDPlanForm',
            'single': 'spouse_standalone_add_plan', 'plural': 'spouse_standalone_add_plans',
            'form_name': 'spouse_standalone_add_plan_form',
            'template': '/admin/_spouse_standalone_add_plans.html'}
    subs = []


class ChildStandaloneADDPlanView(AJAXCrudView):
    main = {'model': ChildStandaloneADDPlan, 'form': ChildStandaloneADDPlanForm,
            'class': 'ChildStandaloneADDPlan', 'form_class': 'ChildStandaloneADDPlanForm',
            'single': 'child_standalone_add_plan', 'plural': 'child_standalone_add_plans',
            'form_name': 'child_standalone_add_plan_form',
            'template': '/admin/_child_standalone_add_plans.html'}
    subs = []


class LTCPlanView(AJAXCrudView):
    main = {'model': LongTermCarePlan, 'form': LongTermCarePlanForm,
            'class': 'LongTermCarePlan', 'form_class': 'LongTermCarePlanForm',
            'single': 'ltc_plan', 'plural': 'ltc_plans',
            'form_name': 'ltc_plan_form',
            'template': '/admin/_ltc_plans.html'}
    subs = []


class FSAMedicalPlanView(AJAXCrudView):
    main = {'model': FSAMedicalPlan, 'form': FSAMedicalPlanForm,
            'class': 'FSAMedicalPlan', 'form_class': 'FSAMedicalPlanForm',
            'single': 'fsa_medical_plan', 'plural': 'fsa_medical_plans',
            'form_name': 'fsa_medical_plan_form',
            'plantype': 'fsa_medical',
            'template': '/admin/_fsa_medical_plans.html'}
    subs = []


class FSADependentPlanView(AJAXCrudView):
    main = {'model': FSADependentCarePlan, 'form': FSADependentCarePlanForm,
            'class': 'FSADependentCarePlan', 'form_class': 'FSADependentPlanForm',
            'single': 'fsa_dependent_care_plan', 'plural': 'fsa_dependent_care_plans',
            'form_name': 'fsa_dependent_care_plan_form',
            'template': '/admin/_fsa_dependent_care_plans.html'}
    subs = []


class HSAPlanView(AJAXCrudView):
    main = {'model': HSAPlan, 'form': HSAPlanForm,
            'class': 'HSAPlan', 'form_class': 'HSAPlanForm',
            'single': 'hsa_plan', 'plural': 'hsa_plans',
            'form_name': 'hsa_plan_form',
            'template': '/admin/_hsa_plans.html'}
    subs = []


class HRAPlanView(AJAXCrudView):
    main = {'model': HRAPlan, 'form': HRAPlanForm,
            'class': 'HRAPlan', 'form_class': 'HRAPlanForm',
            'single': 'hra_plan', 'plural': 'hra_plans',
            'form_name': 'hra_plan_form',
            'template': '/admin/_hra_plans.html'}
    subs = []


class Employee401kPlanView(AJAXCrudView):
    main = {'model': Employee401KPlan,
            'form': Employee401KPlanForm,
            'class': 'Employee401KPlan',
            'form_class': 'Employee401KPlanForm',
            'single': 'e401k_plan', 'plural': 'e401k_plans',
            'form_name': 'e401k_plan_form',
            'template': '/admin/_e401k_plans.html'}
    subs = []


class CancerPlanView(AJAXCrudView):
    main = {'model': CancerPlan, 'form': CancerPlanForm,
            'class': 'CancerPlan', 'form_class': 'CancerPlanForm',
            'single': 'cancer_plan', 'plural': 'cancer_plans',
            'form_name': 'cancer_plan_form',
            'template': '/admin/_cancer_plans.html'}
    subs = []


class CriticalPlanView(AJAXCrudView):
    main = {'model': CriticalIllnessPlan, 'form': CriticalIllnessPlanForm,
            'class': 'CriticalIllnessPlan',
            'form_class': 'CriticalIllnessPlanForm',
            'single': 'critical_illness_plan',
            'plural': 'critical_illness_plans',
            'form_name': 'critical_illness_plan_form',
            'template': '/admin/_critical_illness_plans.html'}
    subs = []


class ParkingTransitPlanView(AJAXCrudView):
    main = {'model': ParkingTransitPlan, 'form': ParkingTransitPlanForm,
            'class': 'ParkingTransitPlan',
            'form_class': 'ParkingTransitPlanForm',
            'single': 'parking_transit_plan',
            'plural': 'parking_transit_plans',
            'form_name': 'parking_transit_plan_form',
            'template': '/admin/_parking_transit_plans.html'}
    subs = []


class AccidentPlanView(AJAXCrudView):
    main = {'model': AccidentPlan, 'form': AccidentPlanForm,
            'class': 'AccidentPlan', 'form_class': 'AccidentPlanForm',
            'single': 'accident_plan', 'plural': 'accident_plans',
            'form_name': 'accident_plan_form',
            'template': '/admin/_accident_plans.html'}
    subs = []


class HospitalConfinementPlanView(AJAXCrudView):
    main = {'model': HospitalConfinementPlan, 'form': HospitalConfinementPlanForm,
            'class': 'HospitalConfinementPlan', 'form_class': 'HospitalConfinementPlanForm',
            'single': 'hospital_confinement_plan', 'plural': 'hospital_confinement_plans',
            'form_name': 'hospital_confinement_plan_form',
            'template': '/admin/_hospital_confinement_plans.html'}
    subs = []


class IdentityTheftPlanView(AJAXCrudView):
    main = {'model': IdentityTheftPlan, 'form': IdentityTheftPlanForm,
            'class': 'IdentityTheftPlan',
            'form_class': 'IdentityTheftPlanForm',
            'single': 'identity_theft_plan',
            'plural': 'identity_theft_plans',
            'form_name': 'identity_theft_plan_form',
            'template': '/admin/_identity_theft_plans.html'}
    subs = []


class OtherPlanView(AJAXCrudView):
    main = {'model': OtherPlan, 'form': OtherPlanForm,
            'class': 'OtherPlan',
            'form_class': 'OtherPlanForm',
            'single': 'other_plan',
            'plural': 'other_plans',
            'form_name': 'other_plan_form',
            'template': '/admin/_other_plans.html'}
    subs = []


class EmployeeView(AJAXCrudView):
    main = {'model': Employee, 'form': EmployeeForm, 'class': 'Employee',
            'form_class': 'EmployeeForm', 'single': 'employee',
            'plural': 'employees', 'form_name': 'employee_form',
            'template': '/admin/_employees.html'}
    subs = [
        {'model': User, 'form': UserForm, 'class': 'User',
         'form_class': 'UserForm', 'single': 'user',
         'plural': 'users', 'form_name': 'user_form'},
        {'model': Address, 'form': AddressForm, 'class': 'Address',
         'form_class': 'AddressForm', 'single': 'address',
         'plural': 'addresss', 'form_name': 'address_form'},
    ]

    def on_save(self, employee):
        employee.user.password = employee.get_default_password()
        employee.user.confirmed_at = date.today()


class LocationView(AJAXCrudView):
    main = {'model': Location, 'form': LocationForm, 'class': 'Location',
            'form_class': 'LocationForm', 'single': 'location',
            'plural': 'locations', 'form_name': 'location_form',
            'template': '/admin/_locations.html'}
    subs = []


class PremiumView(AJAXCrudView):
    main = {'model': Premium, 'form': PremiumForm,
            'class': 'Premium', 'form_class': 'PremiumForm',
            'single': 'premium', 'plural': 'premiums',
            'form_name': 'premium_form',
            'template': '/admin/_premiums.html'}
    subs = []

    def get(self, id):
        assert(id)
        # show form
        main = self.main['model'].query.get(id)
        self.plan = main.plan
        template = env.get_template(self.main['template'])
        form = self.main['form'](None, main)
        form.tier_type.choices = get_remaining_tier_choices(id)

        ctx = {self.main['single']: main, 'plan': self.plan,
               self.main['form_name']: form}

        return template.render(ctx)

    def post(self):
        main = self.main['model']()
        form = self.main['form'](request.form)
        form.populate_obj(main)
        main.id = None

        db.session.add(main)
        db.session.commit()

        template = env.get_template(self.main['template'])
        plan = main.plan
        form = self.main['form'](None)
        form.tier_type.choices = get_remaining_tier_choices(plan.id)

        ctx = {self.main['plural']: plan.tiered_premiums,
               self.main['form_name']: form, 'plan': plan}
        return template.render(ctx)

    def put(self, id):
        template = env.get_template(self.main['template'])
        form = self.main['form'](request.form)
        main = self.main['model'].query.get(id)
        self.plan = main.plan
        form.populate_obj(main)
        db.session.add(main)
        db.session.commit()
        form = self.main['form'](None)
        form.tier_type.choices = get_remaining_tier_choices(id)
        ctx = {self.main['plural']: self.plan.tiered_premiums,
               self.main['form_name']: form, 'plan': self.plan}
        return template.render(ctx)

    def delete(self, id):
        template = env.get_template(self.main['template'])
        obj = self.main['model'].query.get(id)
        plan = obj.plan
        db.session.delete(obj)
        db.session.commit()
        form = self.main['form'](None)
        form.tier_type.choices = get_remaining_tier_choices(id)

        ctx = {'tiered_premiums': plan.tiered_premiums,
               'tiered_premium_form': form,
               'plan': plan}
        return template.render(ctx)


# Enrollment Ajax Views
class EnrollLifeEventAJAXView(MethodView):

    def get(self, id):
        template = env.get_template('/enroll/_life_events.html')
        if not id:
            employee = Employee.query.join(User).filter(
                User.id == g.user.id).first()
            enrollment = Enrollment.query.filter(Enrollment.employee_id == employee.id).first()
            return template.render({'life_event': enrollment})

        # displaying a form to choose a life event
        enrollment = Enrollment.query.get(id)
        life_event_form = LifeEventsForm(None, enrollment)
        ctx = {'life_event_form': life_event_form,
               'life_events': LIFE_EVENT_TYPES}

        return template.render(ctx)

    def put(self, id):
        # update the enrollment
        form = LifeEventsForm(request.form)
        enrollment = Enrollment.query.get(id)
        form.populate_obj(enrollment)
        enrollment.id = id

        db.session.add(enrollment)
        db.session.commit()

        # display the table view with one entry
        template = env.get_template('/enroll/_life_events.html')
        ctx = {'life_event': enrollment}
        return template.render(ctx)


class EnrollInfoAJAXView(MethodView):

    def get(self, id):
        template = env.get_template('/enroll/_personal.html')
        if not id:
            employee = Employee.query.join(User).filter(
                User.id == g.user.id).first()
            return template.render({'employee': employee})

        # displaying a form to choose a life event
        employee = Employee.query.get(id)
        info_form = EmployeeInfoForm(None, employee)
        address_form = AddressForm(None, employee.address)
        ctx = {'info_form': info_form, 'address_form': address_form}
        template = env.get_template('/enroll/_personal.html')

        return template.render(ctx)

    def put(self, id):
        # update the employee info
        employee = Employee.query.get(id)
        form = EmployeeInfoForm(request.form)
        form.populate_obj(employee)
        form = AddressForm(request.form)
        form.populate_obj(employee.address)

        db.session.add(employee)
        db.session.commit()

        # display the table view with one entry
        template = env.get_template('/enroll/_personal.html')
        ctx = {'employee': employee}
        return template.render(ctx)


class EnrollDependentsView(MethodView):

    def get(self, id):
        if not id:
            return self.display_all()
        # displaying a form to edit an existng dependent
        dependent = Dependent.query.get(id)
        dependent_form = DependentForm(None, dependent)
        address_form = AddressForm(None, dependent.address)

        template = env.get_template('enroll/_dependents.html')
        ctx = {'dependent_form': dependent_form,
               'dependent': dependent, 'address_form': address_form}

        return template.render(ctx)

    def post(self):
        # add the dependent from the form
        form = DependentForm(request.form)
        address_form = AddressForm(request.form)
        employee = Employee.query.join(User).filter(User.id == g.user.id).first()
        dependent = Dependent()
        valid = form.validate()
        add_valid = address_form.validate()
        if not valid or not add_valid:
            template = env.get_template('enroll/_dependents.html')
            ctx = {'dependent_form': form, 'address_form': address_form,
                   'employee': employee, 'dependent': dependent}
            return template.render(ctx)

        form.populate_obj(dependent)
        dependent.id = None
        dependent.employee_id = employee.id
        dependent.address.id = None

        db.session.add(dependent.address)

        db.session.add(dependent)
        db.session.commit()
        # display all the dependents
        return self.display_all()

    def put(self, id):
        # update the dependent from the form
        form = DependentForm(request.form)
        dependent = Dependent.query.get(id)
        form.populate_obj(dependent)

        db.session.add(dependent)
        db.session.commit()
        # display all the dependents
        return self.display_all()

    def delete(self, id):
        dependent = Dependent.query.get(id)

        db.session.delete(dependent)
        db.session.commit()

        return self.display_all()

    def display_all(self):
        employee = Employee.query.join(User).filter(User.id == g.user.id).first()
        dependents = employee.dependents
        return render_template('enroll/_dependents.html',
                               address_form=AddressForm(),
                               dependents=dependents,
                               dependent_form=DependentForm())


class EnrollMedicalView(EnrollPlanAJAXView):

    template_name = '/enroll/_medical.html'
    plan_class = MedicalPlan
    prefix = 'medical'


class EnrollDentalView(EnrollPlanAJAXView):

    template_name = '/enroll/_dental.html'
    plan_class = DentalPlan
    prefix = 'dental'


class EnrollVisionView(EnrollPlanAJAXView):

    template_name = '/enroll/_vision.html'
    plan_class = VisionPlan
    prefix = 'vision'


class EnrollEAPView(EnrollPlanAJAXView):

    template_name = '/enroll/_eap.html'
    plan_class = EAPPlan
    prefix = 'eap'


class EnrollLTDView(EnrollPlanAJAXView):

    template_name = '/enroll/_ltd.html'
    plan_class = LTDPlan
    prefix = 'ltd'


class EnrollSTDView(EnrollPlanAJAXView):

    template_name = '/enroll/_std.html'
    plan_class = STDPlan
    prefix = 'std'


class EnrollLifeADDView(EnrollPlanAJAXView):

    template_name = '/enroll/_life_add.html'
    plan_class = BasicLifePlan
    prefix = 'life_add'

    def do_extra_persistence(self, employee, request, enrollment=None):
        pass


class EnrollWholeLifeView(EnrollPlanAJAXView):

    template_name = '/enroll/_whole_life.html'
    plan_class = WholeLifePlan
    prefix = 'whole_life'

    def do_extra_persistence(self, employee, request, enrollment=None):
        pass


class EnrollUniversalLifeView(EnrollPlanAJAXView):

    template_name = '/enroll/_universal_life.html'
    plan_class = UniversalLifePlan
    prefix = 'universal_life'

    def do_extra_persistence(self, employee, request, enrollment=None):
        pass


class EnrollStandaloneADDView(EnrollPlanAJAXView):

    template_name = '/enroll/_standalone_add.html'
    plan_class = StandaloneADDPlan
    prefix = 'standalone_add'


class EnrollVoluntaryLifeView(EnrollPlanAJAXView):

    template_name = '/enroll/_voluntary_life.html'
    plan_class = VoluntaryLifePlan
    prefix = 'voluntary_life'


class EnrollSpouseVoluntaryLifeView(EnrollPlanAJAXView):

    template_name = '/enroll/_spouse_voluntary_life.html'
    plan_class = SpouseVoluntaryLifePlan
    prefix = 'spouse_voluntary_life'


class EnrollChildVoluntaryLifeView(EnrollPlanAJAXView):

    template_name = '/enroll/_child_voluntary_life.html'
    plan_class = ChildVoluntaryLifePlan
    prefix = 'child_voluntary_life'


class EnrollFSAPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_fsa.html'
    plan_class = FSAMedicalPlan
    prefix = 'fsa'


class EnrollFSADependentPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_fsa_dependent.html'
    plan_class = FSADependentCarePlan
    prefix = 'fsa_dependent'


class EnrollParkingTransitPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_parking.html'
    plan_class = ParkingTransitPlan
    prefix = 'parking_transit'


class EnrollHSAPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_hsa.html'
    plan_class = HSAPlan
    prefix = 'hsa'


class EnrollHRAPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_hra.html'
    plan_class = HRAPlan
    prefix = 'hra'


class EnrollEmployee401KPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_e401k.html'
    plan_class = Employee401KPlan
    prefix = 'e401k'


class EnrollLongTermCarePlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_ltc.html'
    plan_class = LongTermCarePlan
    prefix = 'ltc'


class EnrollCancerPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_cancer.html'
    plan_class = CancerPlan
    prefix = 'cancer'


class EnrollCriticalIllnessPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_critical.html'
    plan_class = CriticalIllnessPlan
    prefix = 'critical'


class EnrollAccidentPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_accident.html'
    plan_class = AccidentPlan
    prefix = 'accident'


class EnrollHospitalConfinementPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_hospital_confinement.html'
    plan_class = HospitalConfinementPlan
    prefix = 'hospital_confinement'


class EnrollIdentityTheftPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_identity_theft.html'
    plan_class = IdentityTheftPlan
    prefix = 'identity_theft'


class BulkLoadView(MethodView):

    def get(self):
        return render_template('admin/upload.html', form=UploadForm())

    def post(self):
        form = UploadForm(CombinedMultiDict((request.form, request.files)))
        do_bulk_load(form.xl.data.stream)
        flash("Bulk load completed.")
        return render_template('admin/upload.html', form=UploadForm())


main.add_url_rule('/admin/upload.html', view_func=BulkLoadView.as_view('bulk_load'))


def register_ajax_view(view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    main.add_url_rule(url, defaults={pk: None}, view_func=view_func, methods=['GET', ])
    main.add_url_rule(url, view_func=view_func, methods=['POST', ])
    main.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func, methods=['GET', 'PUT', 'DELETE'])

# admin
register_ajax_view(AccidentPlanView, 'accident_plan_ajax', '/admin/_accident_plans/')
register_ajax_view(BasicLifePlanView, 'basic_life_plan_ajax', '/admin/_basic_life_plans/')
register_ajax_view(CancerPlanView, 'cancer_plan_ajax', '/admin/_cancer_plans/')
register_ajax_view(CarrierView, 'carrier_ajax', '/admin/_carriers/')
register_ajax_view(EnrollmentPeriodView, 'enrollment_period_ajax', '/admin/_enrollment_periods/')
register_ajax_view(CriticalPlanView, 'critical_plan_ajax', '/admin/_critical_illness_plans/')
register_ajax_view(DentalPlanView, 'dental_plan_ajax', '/admin/_dental_plans/')
register_ajax_view(EAPPlanView, 'eap_plan_ajax', '/admin/_eap_plans/')
register_ajax_view(Employee401kPlanView, 'employee_401k_ajax', '/admin/_e401k_plans/')
register_ajax_view(EmployeeView, 'employee_ajax', '/admin/_employees/')
register_ajax_view(FSAMedicalPlanView, 'fsa_medical_plan_ajax', '/admin/_fsa_medical_plans/')
register_ajax_view(FSADependentPlanView, 'fsa_depndent_plan_ajax', '/admin/_fsa_dependent_care_plans/')
register_ajax_view(HospitalConfinementPlanView, 'hospital_confinement_plan_ajax', '/admin/_hospital_confinement_plans/')
register_ajax_view(IdentityTheftPlanView, 'identity_theft_plan_ajax', '/admin/_identity_theft_plans/')
register_ajax_view(HSAPlanView, 'hsa_plan_ajax', '/admin/_hsa_plans/')
register_ajax_view(HRAPlanView, 'hra_plan_ajax', '/admin/_hra_plans/')
register_ajax_view(LTCPlanView, 'ltc_plan_ajax', '/admin/_ltc_plans/')
register_ajax_view(LTDPlanView, 'ltd_plan_ajax', '/admin/_ltd_plans/')
register_ajax_view(STDPlanView, 'std_plan_ajax', '/admin/_std_plans/')
register_ajax_view(LocationView, 'location_ajax', '/admin/_locations/')
register_ajax_view(MedicalPlanView, 'medical_plan_ajax', '/admin/_medical_plans/')
register_ajax_view(MedicalDentalVisionPlanView, 'medical_dental_vision_plan_ajax',
                   '/admin/_medical_dental_vision_plans/')
register_ajax_view(MedicalDentalPlanView, 'medical_dental_plan_ajax', '/admin/_medical_dental_plans/')
register_ajax_view(MedicalVisionPlanView, 'medical_vision_plan_ajax', '/admin/_medical_vision_plans/')
register_ajax_view(DentalVisionPlanView, 'dental_vision_plan_ajax', '/admin/_dental_vision_plans/')
register_ajax_view(ParkingTransitPlanView, 'parking_transit_plan_ajax', '/admin/_parking_transit_plans/')
register_ajax_view(StandaloneADDPlanView, 'standalone_add_plan_ajax', '/admin/_standalone_add_plans/')
register_ajax_view(SpouseStandaloneADDPlanView, 'spouse_standalone_add_plan_ajax',
                   '/admin/_spouse_standalone_add_plans/')
register_ajax_view(ChildStandaloneADDPlanView, 'child_standalone_add_plan_ajax',
                   '/admin/_child_standalone_add_plans/')
register_ajax_view(VisionPlanView, 'vision_plan_ajax', '/admin/_vision_plans/')
register_ajax_view(VoluntaryLifePlanView, 'voluntary_life_plan_ajax', '/admin/_voluntary_life_plans/')
register_ajax_view(SpouseVoluntaryLifePlanView, 'spouse_voluntary_life_plan_ajax',
                   '/admin/_spouse_voluntary_life_plans/')
register_ajax_view(ChildVoluntaryLifePlanView, 'child_voluntary_life_plan_ajax', '/admin/_child_voluntary_life_plans/')
register_ajax_view(PremiumView, 'tiered_premium_ajax', '/admin/_tiered_premiums/')
register_ajax_view(OtherPlanView, 'other_plan_ajax', '/admin/_other_plans/')
register_ajax_view(WholeLifePlanView, 'whole_life_plan_ajax', '/admin/_whole_life_plans/')
register_ajax_view(UniversalLifePlanView, 'universal_life_plan_ajax', '/admin/_universal_life_plans/')
register_ajax_view(SpouseWholeLifePlanView, 'spouse_whole_life_plan_ajax', '/admin/_spouse_whole_life_plans/')
register_ajax_view(ChildWholeLifePlanView, 'child_whole_life_plan_ajax', '/admin/_child_whole_life_plans/')

# enroll
register_ajax_view(EnrollDependentsView, 'dependent_ajax', '/enroll/_dependents/')
register_ajax_view(EnrollMedicalView, 'enroll_medical_ajax', '/enroll/_medicals/')
register_ajax_view(EnrollDentalView, 'enroll_dental_ajax', '/enroll/_dentals/')
register_ajax_view(EnrollVisionView, 'enroll_vision_ajax', '/enroll/_visions/')
register_ajax_view(EnrollEAPView, 'enroll_eap_ajax', '/enroll/_eaps/')
register_ajax_view(EnrollLTDView, 'enroll_ltd_ajax', '/enroll/_ltds/')
register_ajax_view(EnrollSTDView, 'enroll_std_ajax', '/enroll/_stds/')
register_ajax_view(EnrollLifeADDView, 'enroll_life_add_ajax', '/enroll/_life_adds/')
register_ajax_view(EnrollWholeLifeView, 'enroll_whole_life_ajax', '/enroll/_whole_lifes/')
register_ajax_view(EnrollStandaloneADDView, 'enroll_standalone_add_ajax', '/enroll/_standalone_adds/')
register_ajax_view(EnrollUniversalLifeView, 'enroll_universal_life_ajax', '/enroll/_universal_lifes/')
register_ajax_view(EnrollVoluntaryLifeView, 'enroll_voluntary_life_ajax', '/enroll/_voluntary_lifes/')
register_ajax_view(EnrollSpouseVoluntaryLifeView, 'enroll_spouse_voluntary_life_ajax',
                   '/enroll/_spouse_voluntary_lifes/')
register_ajax_view(EnrollChildVoluntaryLifeView, 'enroll_child_voluntary_life_ajax',
                   '/enroll/_child_voluntary_lifes/')
register_ajax_view(EnrollFSAPlanView, 'enroll_fsa_ajax', '/enroll/_fsas/')
register_ajax_view(EnrollFSADependentPlanView, 'enroll_fsa_dependent_ajax', '/enroll/_fsa_dependents/')
register_ajax_view(EnrollParkingTransitPlanView, 'enroll_parking_transit_ajax', '/enroll/_parking_transits/')
register_ajax_view(EnrollHRAPlanView, 'enroll_hra_ajax', '/enroll/_hras/')
register_ajax_view(EnrollHSAPlanView, 'enroll_hsa_ajax', '/enroll/_hsas/')
register_ajax_view(EnrollEmployee401KPlanView, 'enroll_e401k_ajax', '/enroll/_e401ks/')
register_ajax_view(EnrollLongTermCarePlanView, 'enroll_ltc_ajax', '/enroll/_ltcs/')
register_ajax_view(EnrollCancerPlanView, 'enroll_cancer_ajax', '/enroll/_cancers/')
register_ajax_view(EnrollCriticalIllnessPlanView, 'enroll_critical_ajax', '/enroll/_criticals/')
register_ajax_view(EnrollAccidentPlanView, 'enroll_accident_ajax', '/enroll/_accidents/')
register_ajax_view(EnrollHospitalConfinementPlanView, 'enroll_hospital_ajax', '/enroll/_hospital_confinements/')
register_ajax_view(EnrollIdentityTheftPlanView, 'enroll_identity_theft_ajax', '/enroll/_identity_thefts/')
register_ajax_view(EnrollLifeEventAJAXView, 'enroll_life_events_ajax', '/enroll/_life_events/')
register_ajax_view(EnrollInfoAJAXView, 'enroll_info_ajax', '/enroll/_infos/')
