# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.
from datetime import date
import locale


from flask import g, flash, request, render_template, redirect, url_for
from flask.views import MethodView
from flask_login import current_user, login_required
from jinja2 import Environment, PackageLoader
from werkzeug.datastructures import CombinedMultiDict

from . import app, db
from .forms import (
    AddressForm,
    CancerPlanForm,
    CarrierForm,
    CriticalIllnessPlanForm,
    DentalPlanForm,
    DependentForm,
    EAPPlanForm,
    Employee401KPlanForm,
    EmployeeForm,
    EmployeeInfoForm,
    FSAMedicalPlanForm,
    HSAPlanForm,
    LongTermCarePlanForm,
    LTDPlanForm,
    LifeADDPlanForm,
    LifeEventsForm,
    LocationForm,
    MedicalPlanForm,
    ParkingTransitPlanForm,
    PremiumForm,
    STDPlanForm,
    UploadForm,
    UserForm,
    VisionPlanForm,
)
from .importer import do_bulk_load
from .models import (
    AccidentPlan,
    Address,
    BasicLifePlan,
    CancerPlan,
    Carrier,
    ChildVoluntaryLifePlan,
    Dependent,
    DentalVisionBundlePlan,
    CriticalIllnessPlan,
    DentalPlan,
    EAPPlan,
    Election,
    Employee,
    Employee401KPlan,
    Enrollment,
    FAMILY_TIER_TYPES,
    FSAMedicalPlan,
    HospitalConfinementPlan,
    HRAPlan,
    HSAPlan,
    IdentityTheftPlan,
    LIFE_EVENT_TYPES,
    LongTermCarePlan,
    LTDPlan,
    LTDVoluntaryPlan,
    Location,
    MARITAL_STATUS_TYPES,
    MedicalPlan,
    MedicalDentalBundlePlan,
    MedicalDentalVisionBundlePlan,
    MedicalVisionBundlePlan,
    ParkingTransitPlan,
    Plan,
    Premium,
    Role,
    SpouseVoluntaryLifePlan,
    StandaloneADDPlan,
    STDPlan,
    STDVoluntaryPlan,
    UniversalLifePlan,
    User,
    VisionPlan,
    VoluntaryLifePlan,
    WholeLifePlan,
    user_manager,
)


env = Environment(loader=PackageLoader('perks', 'templates'))
locale.setlocale(locale.LC_ALL, '')


@app.login_manager.user_loader
def load_user(user_id):
    if user_id:
        return User.query.get(int(user_id))
    else:
        return None


@app.before_request
def before_request():
    g.user = current_user
    load_user(current_user.get_id())


@app.route('/')
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
        valid = True
        main = self.main['model']()
        form = self.main['form'](request.form)
        if not form.validate():
            valid = False
        forms[self.main['form_name']] = form
        form.populate_obj(main)
        main.id = None
        for sub in self.subs:
            obj = sub['model']()
            form = sub['form'](request.form)
            if not form.validate():
                valid = False
            forms[sub['form_name']] = form
            form.populate_obj(obj)
            if obj.id == '':
                obj.id = None
            db.session.add(obj)
            setattr(main, sub['single'], obj)

        template = env.get_template(self.main['template'])
        if not valid:
            return self.display_errors(main, forms)

        self.on_save(main)

        db.session.add(main)
        db.session.commit()

        objects = self.main['model'].query.all()
        ctx = {self.main['plural']: objects, self.main['form_name']: self.main['form'](None)}
        for sub in self.subs:
            ctx[sub['form_name']] = sub['form'](None)
        return template.render(ctx)

    def put(self, id):
        forms = {}
        valid = True
        main = self.main['model'].query.get(id)
        form = self.main['form'](request.form, obj=main)
        if not form.validate:
            valid = False
        forms[self.main['form_name']] = form
        form.populate_obj(main)
        for sub in self.subs:
            obj = getattr(main, sub['single'])
            form = sub['form'](request.form, obj=obj)
            if not form.validate():
                valid = False
            forms[sub['form_name']] = form
            if not obj:
                obj = sub['model']()
                setattr(main, sub['single'], obj)
            form.populate_obj(obj)
        if not valid:
            return self.display_errors(main, forms)

        self.on_edit(main)
        db.session.commit()
        return self.display_all()

    def delete(self, id):
        obj = self.main['model'].query.get(id)
        self.on_delete(obj)
        db.session.delete(obj)
        db.session.commit()
        return self.display_all()

    def display_errors(self, main, forms):
        ctx = {self.main['single']: main}
        ctx.update(forms)
        template = env.get_template(self.main['template'])
        return template.render(ctx)

    def display_all(self):
        objects = self.main['model'].query.all()
        template = env.get_template(self.main['template'])
        ctx = {self.main['plural']: objects, self.main['form_name']: self.main['form'](None)}
        for sub in self.subs:
            ctx[sub['form_name']] = sub['form'](None)
        return template.render(ctx)


# ENROLL
@app.route('/enroll')
@login_required
def enroll():
    employee = Employee.query.join(User).filter(
        User.id == g.user.id).first()
    if not employee:
        flash("You must be an employee in order to enroll.", 'error')
        return redirect(url_for('index'))
    enrollment = Enrollment.query.filter(
        Enrollment.employee_id == employee.id).first()
    if not enrollment:
        enrollment = Enrollment()
        enrollment.employee_id = employee.id
        db.session.add(enrollment)
        db.session.commit()

    return redirect(url_for('enroll_life_events'))


@app.route('/enroll/life_events', methods=['GET', 'POST'])
@login_required
def enroll_life_events():
    g.active_tab = 'enroll'
    g.active_step = 'life'

    employee = Employee.query.join(User).filter(User.id == g.user.id).first()
    enrollment = Enrollment.query.filter(Enrollment.employee_id == employee.id).first()

    return render_template('enroll/life_events.html', life_event=enrollment)


@app.route('/enroll/dependents', methods=['GET', 'POST'])
@login_required
def enroll_dependents():
    g.active_tab = 'enroll'
    g.active_step = 'dependents'
    employee = Employee.query.join(User).filter(
        User.id == g.user.id).first()
    dependents = employee.dependents
    return render_template('enroll/dependents.html',
                           dependents=dependents,
                           dependent_form=DependentForm(),
                           address_form=AddressForm(),
                           employee=employee,
                           )


def get_selections(plans, enrollment_id):
    selections = []
    for plan in plans:
        selection = {'plan_name': plan.name,
                     'plan_id': plan.id,
                     'election_label': 'Declined'}
        selections.append(selection)
        election = Election.query.filter(
            Election.enrollment_id == enrollment_id,
            Election.plan_id == plan.id).first()
        if election and election.premium:
            selection['election_label'] = (election.premium.family_tier.value)
        elif election and election.amount:
            selection['amount'] = election.amount
            selection['election_label'] = election.amount
    return selections


@app.route('/enroll/core', methods=['GET'])
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
    medical_selections = get_selections(medical_plans, enrollment.id)
    dental_plans = DentalPlan.query.filter(Plan.active == True).all()
    dental_selections = get_selections(dental_plans, enrollment.id)
    vision_plans = VisionPlan.query.filter(Plan.active == True).all()
    vision_selections = get_selections(vision_plans, enrollment.id)
    medical_dental_plans = MedicalDentalBundlePlan.query.filter(Plan.active == True).all()
    medical_dental_selections = get_selections(medical_dental_plans, enrollment.id)
    medical_vision_plans = MedicalVisionBundlePlan.query.filter(Plan.active == True).all()
    medical_vision_selections = get_selections(medical_vision_plans, enrollment.id)
    medical_dental_vision_plans = MedicalDentalVisionBundlePlan.query.filter(Plan.active == True).all()
    medical_dental_vision_selections = get_selections(medical_dental_vision_plans, enrollment.id)
    dental_vision_plans = DentalVisionBundlePlan.query.filter(Plan.active == True).all()
    dental_vision_selections = get_selections(dental_vision_plans, enrollment.id)
    ctx = {'medical_selections': medical_selections,
           'dental_selections': dental_selections,
           'vision_selections': vision_selections,
           'medical_dental_selections': medical_dental_selections,
           'medical_vision_selections': medical_vision_selections,
           'medical_dental_vision_selections': medical_dental_vision_selections,
           'dental_vision_selections': dental_vision_selections,
           }
    return render_template('enroll/core.html', **ctx)


@app.route('/enroll/group', methods=['GET'])
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
    life_add_selections = get_selections(life_add_plans, enrollment.id)
    voluntary_life_plans = VoluntaryLifePlan.query.filter(Plan.active == True).all()
    voluntary_life_selections = get_selections(voluntary_life_plans, enrollment.id)
    spouse_voluntary_life_plans = SpouseVoluntaryLifePlan.query.filter(Plan.active == True).all()
    spouse_voluntary_life_selections = get_selections(spouse_voluntary_life_plans, enrollment.id)
    child_voluntary_life_plans = ChildVoluntaryLifePlan.query.filter(Plan.active == True).all()
    child_voluntary_life_selections = get_selections(child_voluntary_life_plans, enrollment.id)
    whole_life_plans = WholeLifePlan.query.filter(Plan.active == True).all()
    whole_life_selections = get_selections(whole_life_plans, enrollment.id)
    universal_life_plans = UniversalLifePlan.query.filter(Plan.active == True).all()
    universal_life_selections = get_selections(universal_life_plans, enrollment.id)
    standalone_add_plans = StandaloneADDPlan.query.filter(Plan.active == True).all()
    standalone_add_selections = get_selections(standalone_add_plans, enrollment.id)

    ltd_plans = LTDPlan.query.filter(Plan.active == True).all()
    ltd_selections = get_selections(ltd_plans, enrollment.id)
    ltd_voluntary_plans = LTDVoluntaryPlan.query.filter(Plan.active == True).all()
    ltd_voluntary_selections = get_selections(ltd_voluntary_plans, enrollment.id)
    std_plans = STDPlan.query.filter(Plan.active == True).all()
    std_selections = get_selections(std_plans, enrollment.id)
    std_voluntary_plans = STDVoluntaryPlan.query.filter(Plan.active == True).all()
    std_voluntary_selections = get_selections(std_voluntary_plans, enrollment.id)

    fsa_plans = FSAMedicalPlan.query.filter(Plan.active == True).all()
    fsa_selections = get_selections(fsa_plans, enrollment.id)
    hsa_plans = HSAPlan.query.filter(Plan.active == True).all()
    hsa_selections = get_selections(hsa_plans, enrollment.id)
    hra_plans = HRAPlan.query.filter(Plan.active == True).all()
    hra_selections = get_selections(hra_plans, enrollment.id)
    e401k_plans = Employee401KPlan.query.filter(Plan.active == True).all()
    e401k_selections = get_selections(e401k_plans, enrollment.id)

    ltc_plans = LongTermCarePlan.query.filter(Plan.active == True).all()
    ltc_selections = get_selections(ltc_plans, enrollment.id)
    eap_plans = EAPPlan.query.filter(Plan.active == True).all()
    eap_selections = get_selections(eap_plans, enrollment.id)
    ctx = {'life_add_selections': life_add_selections,
           'voluntary_life_selections': voluntary_life_selections,
           'spouse_voluntary_life_selections': spouse_voluntary_life_selections,
           'child_voluntary_life_selections': child_voluntary_life_selections,
           'whole_life_selections': whole_life_selections,
           'universal_life_selections': universal_life_selections,
           'standalone_add_selections': standalone_add_selections,

           'ltd_selections': ltd_selections,
           'ltd_voluntary_selections': ltd_voluntary_selections,
           'std_selections': std_selections,
           'std_voluntary_selections': std_voluntary_selections,

           'fsa_selections': fsa_selections,
           'hsa_selections': hsa_selections,
           'hra_selections': hra_selections,
           'e401k_selections': e401k_selections,

           'ltc_selections': ltc_selections,
           'eap_selections': eap_selections,
           }
    return render_template('enroll/group.html', **ctx)


@app.route('/enroll/supplemental', methods=['GET'])
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
    critical_selections = get_selections(critical_plans, enrollment.id)
    cancer_plans = CancerPlan.query.filter(Plan.active == True).all()
    cancer_selections = get_selections(cancer_plans, enrollment.id)
    accident_plans = AccidentPlan.query.filter(Plan.active == True).all()
    accident_selections = get_selections(accident_plans, enrollment.id)
    hospital_confinement_plans = HospitalConfinementPlan.query.filter(Plan.active == True).all()
    hospital_confinement_selections = get_selections(hospital_confinement_plans, enrollment.id)
    parking_transit_plans = ParkingTransitPlan.query.filter(Plan.active == True).all()
    parking_transit_selections = get_selections(parking_transit_plans, enrollment.id)
    identity_theft_plans = IdentityTheftPlan.query.filter(Plan.active == True).all()
    identity_theft_selections = get_selections(identity_theft_plans, enrollment.id)
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
            # displaying a form to edit the election
            plan = Plan.query.get(id)
            enrollment = Enrollment.query.filter(Enrollment.employee_id == employee.id).first()
            election = Election.query.filter(Election.enrollment_id == enrollment.id,
                                             Election.plan_id == plan.id).first()
            if not election:
                election = Election()
                election.plan_id = plan.id
                election.enrollment_id = enrollment.id
            form_class = plan.get_election_form()
            election_form = form_class(obj=election)
            election_form.selection.choices = plan.get_premium_choices(
                election.premium_id or election.amount or election.elected, employee)
            template = env.get_template(self.template_name)
            ctx = {'election': election,
                   'election_form': election_form}

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
        form.populate_election(election)
        db.session.add(election)
        db.session.commit()

        return self.display_all()

    def put(self, id):
        employee = Employee.query.join(User).filter(User.id == g.user.id).first()
        plan = Plan.query.get(id)
        form_class = plan.get_election_form()
        form = form_class(request.form)
        form.selection.choices = plan.get_premium_choices(request.values['selection'], employee)
        assert(form.enrollment_id.data)
        enrollment = Enrollment.query.get(form.enrollment_id.data)
        election = Election.query.filter(Election.enrollment_id == enrollment.id, Election.plan_id == id).one()
        form.populate_obj(election)
        form.populate_election(election)
        db.session.add(election)
        db.session.commit()
        return self.display_all()

    def display_all(self):
        employee = Employee.query.join(User).filter(User.id == g.user.id).first()
        plans = self.plan_class.query.all()
        enrollment = Enrollment.query.filter(Enrollment.employee_id == employee.id).one()
        selections = []
        for plan in plans:
            selection = {'plan_name': plan.name, 'plan_id': plan.id, 'election_label': 'Declined'}
            selections.append(selection)
            election = Election.query.filter(Election.enrollment_id == enrollment.id,
                                             Election.plan_id == plan.id).first()
            if election and election.premium:
                selection['election_label'] = (election.premium.family_tier.value)
            elif election and election.amount:
                selection['amount'] = (election.amount)
                selection['election_label'] = election.amount
            elif election and election.elected:
                selection['election_label'] = 'Enrolled'
            else:
                election = Election()
                election.plan = plan
                election.enrollment_id = enrollment.id
            form_class = plan.get_election_form()
            election_form = form_class()
            election_form.selection.choices = plan.get_premium_choices(election_form.data['selection'], employee)
        ctx = {'election_form': election_form,
               '{}_selections'.format(self.prefix): selections}
        return render_template(self.template_name, **ctx)


@app.route('/enroll/finalize', methods=['GET', 'POST'])
@login_required
def enroll_finalize():
    pass


@app.route('/messages')
@login_required
def messages():
    g.active_tab = 'messages'
    return render_template('messages/messages.html')


@app.route('/benefits')
@login_required
def benefits():
    g.active_tab = 'benefits'
    return render_template('benefits/benefits.html')


@app.route('/admin')
@login_required
def admin():
    g.active_tab = 'admin'
    return redirect(url_for('admin_people'), )


@app.route('/admin/people', methods=['GET', 'POST'])
@login_required
def admin_people():
    g.active_tab = 'admin'
    g.active_step = 'people'
    admin_role = Role.query.filter(Role.name == 'admin').one()
    users = admin_role.users.all()
    employees = Employee.query.all()
    locations = Location.query.all()
    return render_template(
        'admin/people.html', marital_status_types=MARITAL_STATUS_TYPES,
        users=users, user_form=UserForm(), employee_form=EmployeeForm(),
        address_form=AddressForm(), location_form=LocationForm(),
        employees=employees, locations=locations)


def update_user(user, request):
    form = UserForm(request.form)
    original = user.password
    form.populate_obj(user)
    if original != user.password:
        password = user_manager.hash_password(user.password)
        user.password = password

    return user


@app.route('/admin/carriers', methods=['GET'])
@login_required
def admin_carriers():
    g.active_tab = 'admin'
    g.active_step = 'carriers'
    carriers = Carrier.query.all()
    form = CarrierForm()
    return render_template('admin/carriers.html', carriers=carriers,
                           carrier_form=form)


@app.route('/admin/core', methods=['GET'])
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
    return render_template('admin/core.html', medical_plans=medical_plans,
                           medical_plan_form=medical_plan_form,
                           dental_plans=dental_plans,
                           dental_plan_form=dental_plan_form,
                           vision_plans=vision_plans,
                           vision_plan_form=vision_plan_form)


@app.route('/admin/group', methods=['GET', 'POST'])
@login_required
def admin_group():
    g.active_tab = 'admin'
    g.active_step = 'group'
    eap_plans = EAPPlan.query.all()
    eap_plan_form = EAPPlanForm()
    std_plans = STDPlan.query.all()
    std_plan_form = STDPlanForm()
    ltd_plans = LTDPlan.query.all()
    ltd_plan_form = LTDPlanForm()
    add_plans = BasicLifePlan.query.all()
    add_plan_form = LifeADDPlanForm()
    return render_template('admin/group.html', eap_plans=eap_plans,
                           eap_plan_form=eap_plan_form,
                           ltd_plans=ltd_plans,
                           ltd_plan_form=ltd_plan_form,
                           std_plans=std_plans,
                           std_plan_form=std_plan_form,
                           add_plans=add_plans,
                           add_plan_form=add_plan_form)


@app.route('/admin/supplemental', methods=['GET', 'POST'])
@login_required
def admin_supplemental():
    g.active_tab = 'admin'
    g.active_step = 'supplemental'
    fsa_plans = FSAMedicalPlan.query.all()
    fsa_plan_form = FSAMedicalPlanForm()
    hsa_plans = HSAPlan.query.all()
    hsa_plan_form = HSAPlanForm()
    e401k_plans = Employee401KPlan.query.all()
    e401k_plan_form = Employee401KPlanForm()
    cancer_plans = CancerPlan.query.all()
    cancer_plan_form = CancerPlanForm()
    ltc_plans = LongTermCarePlan.query.all()
    ltc_plan_form = LongTermCarePlanForm()
    critical_illness_plans = CriticalIllnessPlan.query.all()
    critical_illness_plan_form = CriticalIllnessPlanForm()
    parking_transit_plans = ParkingTransitPlan.query.all()
    parking_transit_plan_form = ParkingTransitPlanForm()
    return render_template(
        'admin/supplemental.html',
        fsa_plans=fsa_plans,
        fsa_plan_form=fsa_plan_form,
        hsa_plans=hsa_plans,
        hsa_plan_form=hsa_plan_form,
        e401k_plans=e401k_plans,
        e401k_plan_form=e401k_plan_form,
        cancer_plans=cancer_plans,
        cancer_plan_form=cancer_plan_form,
        cricial_illness_plans=critical_illness_plans,
        critical_illness_plan_form=critical_illness_plan_form,
        ltc_plans=ltc_plans,
        ltc_plan_form=ltc_plan_form,
        parking_transit_plans=parking_transit_plans,
        parking_transit_plan_form=parking_transit_plan_form,
    )


def get_remaining_tier_choices(plan_id):
    # remove already chosen tiers from the dropdown list
    types_dict = {x[0]: x for x in FAMILY_TIER_TYPES}
    existing = [x.tier_type.code for x in Premium.query.filter(
        Premium.plan_id == plan_id).all()]
    diff = set(types_dict.keys()) - set(existing)
    return [types_dict[x] for x in diff]


@app.route('/admin/premiums', methods=['GET', 'POST'])
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


class ADDPlanView(AJAXCrudView):
    main = {'model': BasicLifePlan, 'form': LifeADDPlanForm,
            'class': 'BasicLifePlan', 'form_class': 'LifeADDPlanForm',
            'single': 'add_plan', 'plural': 'add_plans',
            'form_name': 'add_plan_form',
            'template': '/admin/_add_plans.html'}
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
            'template': '/admin/_fsa_medical_plans.html'}
    subs = []


class HSAPlanView(AJAXCrudView):
    main = {'model': HSAPlan, 'form': HSAPlanForm,
            'class': 'HSAPlan', 'form_class': 'HSAPlanForm',
            'single': 'hsa_plan', 'plural': 'hsa_plans',
            'form_name': 'hsa_plan_form',
            'template': '/admin/_hsa_plans.html'}
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
        employee.user.password = user_manager.hash_password(employee.user.password)
        employee.user.confirmed_at = date.today()

    def on_edit(self, employee):
        original = Employee.query.get(employee.id)
        hashed = user_manager.hash_password(employee.user.password)
        if (original.user.password == employee.user.password or hashed == employee.user.password):
            return
        else:
            employee.user.password = hashed


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
        # displaying a form to choose a life event
        enrollment = Enrollment.query.get(id)
        life_event_form = LifeEventsForm(None, enrollment)
        ctx = {'life_event_form': life_event_form,
               'life_events': LIFE_EVENT_TYPES}
        template = env.get_template('/enroll/_life_events.html')

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
        employee = Employee.query.join(User).filter(User.id == g.user.id).first()
        dependent = Dependent()
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


class EnrollParkingTransitPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_parking_transit.html'
    plan_class = ParkingTransitPlan
    prefix = 'parking_transit'


class EnrollHSAPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_hsa.html'
    plan_class = HSAPlan
    prefix = 'hsa'


class EnrollEmployee401KPlanView(EnrollPlanAJAXView):

    template_name = '/enroll/_e401k.html'
    plan_class = HSAPlan
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


class BulkLoadView(MethodView):

    def get(self):
        return render_template('admin/upload.html', form=UploadForm())

    def post(self):
        form = UploadForm(CombinedMultiDict((request.form, request.files)))
        do_bulk_load(form.xl.data.stream)
        flash("Bulk load completed.")
        return render_template('admin/upload.html', form=UploadForm())


app.add_url_rule('/admin/upload.html', view_func=BulkLoadView.as_view('bulk_load'))


def register_ajax_view(view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None}, view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func, methods=['GET', 'PUT', 'DELETE'])

# admin
register_ajax_view(ADDPlanView, 'add_plan_ajax', '/admin/_add_plans/')
register_ajax_view(CancerPlanView, 'cancer_plan_ajax', '/admin/_cancer_plans/')
register_ajax_view(CarrierView, 'carrier_ajax', '/admin/_carriers/')
register_ajax_view(CriticalPlanView, 'critical_plan_ajax', '/admin/_critical_illness_plans/')
register_ajax_view(DentalPlanView, 'dental_plan_ajax', '/admin/_dental_plans/')
register_ajax_view(EAPPlanView, 'eap_plan_ajax', '/admin/_eap_plans/')
register_ajax_view(Employee401kPlanView, 'employee_401k_ajax', '/admin/_e401k_plans/')
register_ajax_view(EmployeeView, 'employee_ajax', '/admin/_employees/')
register_ajax_view(FSAMedicalPlanView, 'fsa_plan_ajax', '/admin/_fsa_plans/')
register_ajax_view(HSAPlanView, 'hsa_plan_ajax', '/admin/_hsa_plans/')
register_ajax_view(LTCPlanView, 'ltc_plan_ajax', '/admin/_ltc_plans/')
register_ajax_view(LTDPlanView, 'ltd_plan_ajax', '/admin/_ltd_plans/')
register_ajax_view(STDPlanView, 'std_plan_ajax', '/admin/_std_plans/')
register_ajax_view(LocationView, 'location_ajax', '/admin/_locations/')
register_ajax_view(MedicalPlanView, 'medical_plan_ajax', '/admin/_medical_plans/')
register_ajax_view(ParkingTransitPlanView, 'parking_transit_plan_ajax', '/admin/_parking_transit_plans/')
register_ajax_view(VisionPlanView, 'vision_plan_ajax', '/admin/_vision_plans/')
register_ajax_view(PremiumView, 'tiered_premium_ajax', '/admin/_tiered_premiums/')

# enroll
register_ajax_view(EnrollDependentsView, 'dependent_ajax', '/enroll/_dependents/')
register_ajax_view(EnrollMedicalView, 'enroll_medical_ajax', '/enroll/_medicals/')
register_ajax_view(EnrollDentalView, 'enroll_dental_ajax', '/enroll/_dentals/')
register_ajax_view(EnrollVisionView, 'enroll_vision_ajax', '/enroll/_visions/')
register_ajax_view(EnrollEAPView, 'enroll_eap_ajax', '/enroll/_eaps/')
register_ajax_view(EnrollLTDView, 'enroll_ltd_ajax', '/enroll/_ltds/')
register_ajax_view(EnrollSTDView, 'enroll_std_ajax', '/enroll/_stds/')
register_ajax_view(EnrollLifeADDView, 'enroll_life_add_ajax', '/enroll/_life_adds/')
register_ajax_view(EnrollStandaloneADDView, 'enroll_standalone_add_ajax', '/enroll/_standalone_adds/')
register_ajax_view(EnrollVoluntaryLifeView, 'enroll_voluntary_life_ajax', '/enroll/_voluntary_lifes/')
register_ajax_view(EnrollSpouseVoluntaryLifeView, 'enroll_spouse_voluntary_life_ajax',
                   '/enroll/_spouse_voluntary_lifes/')
register_ajax_view(EnrollChildVoluntaryLifeView, 'enroll_child_voluntary_life_ajax',
                   '/enroll/_child_voluntary_lifes/')
register_ajax_view(EnrollFSAPlanView, 'enroll_fsa_ajax', '/enroll/_fsas/')
register_ajax_view(EnrollParkingTransitPlanView, 'enroll_parking_transit_ajax', '/enroll/_parking_transits/')
register_ajax_view(EnrollHSAPlanView, 'enroll_hsa_ajax', '/enroll/_hsas/')
register_ajax_view(EnrollEmployee401KPlanView, 'enroll_e401k_ajax', '/enroll/_e401ks/')
register_ajax_view(EnrollLongTermCarePlanView, 'enroll_ltc_ajax', '/enroll/_ltcs/')
register_ajax_view(EnrollCancerPlanView, 'enroll_cancer_ajax', '/enroll/_cancers/')
register_ajax_view(EnrollCriticalIllnessPlanView, 'enroll_critical_ajax', '/enroll/_criticals/')
register_ajax_view(EnrollLifeEventAJAXView, 'enroll_life_events_ajax', '/enroll/_life_events/')
register_ajax_view(EnrollInfoAJAXView, 'enroll_info_ajax', '/enroll/_infos/')
