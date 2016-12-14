# -*- coding: utf-8 -*-
from flask import g, request, render_template, redirect, url_for
from flask.views import MethodView
from flask_login import current_user, login_required
from jinja2 import Environment, PackageLoader

from . import app, db_session
#  from .exporter import Exporter
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
    FSAPlanForm,
    HSAPlanForm,
    LongTermCarePlanForm,
    LTDPlanForm,
    LifeADDDependentPlanForm,
    LifeADDPlanForm,
    LifeEventsForm,
    LocationForm,
    MedicalPlanForm,
    OtherPlanForm,
    ParkingTransitPlanForm,
    SupplementalInsurancePlanForm,
    UserForm,
    VisionPlanForm,
)
#  from .models import Employee, Enrollment, LifeEventType, User
from .models import (
    Address,
    CancerPlan,
    Carrier,
    Dependent,
    CriticalIllnessPlan,
    DentalPlan,
    EAPPlan,
    Employee,
    Employee401KPlan,
    FSAPlan,
    HSAPlan,
    LIFE_EVENT_TYPES,
    LifeADDDependentPlan,
    LifeADDPlan,
    LongTermCarePlan,
    LTDPlan,
    Location,
    MARITAL_STATUSES,
    MedicalPlan,
    OtherPlan,
    ParkingTransitPlan,
    Role,
    SupplumentalInsurancePlan,
    User,
    VisionPlan,
    user_manager,
)


env = Environment(loader=PackageLoader('perks', 'templates'))


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


@app.route('/enroll')
@login_required
def enroll():
    return redirect(url_for('enroll_life_events'))


@app.route('/enroll/life_events', methods=['GET', 'POST'])
@login_required
def enroll_life_events():
    g.active_tab = 'enroll'
    g.active_step = 'life'

    enrollment = None
    form = LifeEventsForm(request.form, enrollment)
    if form.validate_on_submit():
        return redirect(url_for('enroll_dependents'))
    else:
        return render_template('enroll/life_events.html', form=form,
                               life_events=LIFE_EVENT_TYPES)


@app.route('/enroll/dependents', methods=['GET', 'POST'])
@login_required
def enroll_dependents():
    g.active_tab = 'enroll'
    g.active_step = 'dependents'
    employee = Employee.query.first()
    dependents = employee.dependents
    dependent_form = DependentForm(data={'employee_id': employee.id})
    address_form = AddressForm()
    return render_template('enroll/dependents.html',
                           dependents=dependents,
                           dependent_form=dependent_form,
                           address_form=address_form,
                           )


@app.route('/enroll/core', methods=['GET', 'POST'])
@login_required
def enroll_core():
    pass


@app.route('/enroll/group', methods=['GET', 'POST'])
@login_required
def enroll_group():
    pass


@app.route('/enroll/supplemental', methods=['GET', 'POST'])
@login_required
def enroll_supplemental():
    pass


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


class AJAXCrudView(MethodView):

    def get(self, id):
        if id is None:
            return self.display_all()
        else:
            main = self.main['model'].query.get(id)
            template = env.get_template(self.main['template'])
            ctx = {self.main['single']: main,
                   self.main['form_name']: self.main['form'](None, main)}
            for sub in self.subs:
                ctx[sub['form_name']] = sub['form'](
                    None, getattr(main, sub['single']))

            return template.render(ctx)

    def post(self):
        main = self.main['model']()
        form = self.main['form'](request.form)
        form.populate_obj(main)
        main.id = None
        for sub in self.subs:
            obj = sub['model']()
            form = sub['form'](request.form)
            form.populate_obj(obj)
            if obj.id == '':
                obj.id = None
            db_session.add(obj)
            setattr(main, sub['single'], obj)

        db_session.add(main)
        db_session.commit()

        objects = self.main['model'].query.all()
        template = env.get_template(self.main['template'])
        ctx = {self.main['plural']: objects,
               self.main['form_name']: self.main['form'](None)}
        for sub in self.subs:
            ctx[sub['form_name']] = sub['form'](None)
        return template.render(ctx)

    def put(self, id):
        import ipdb
        ipdb.set_trace()
        form = self.main['form'](request.form)
        main = self.main['model'].query.get(id)
        form.populate_obj(main)
        db_session.add(main)
        for sub in self.subs:
            form = sub['form'](request.form)
            obj = getattr(main, sub['single'])
            if not obj:
                obj = sub['model']()
                setattr(main, sub['single'], obj)
            form.populate_obj(obj)
            db_session.add(obj)
        try:
            db_session.commit()
        except:
            db_session.rollback()
        return self.display_all()

    def delete(self, id):
        obj = self.main['model'].query.get(id)
        db_session.delete(obj)
        db_session.commit()
        return self.display_all()

    def display_all(self):
        objects = self.main['model'].query.all()
        template = env.get_template(self.main['template'])
        ctx = {self.main['plural']: objects,
               self.main['form_name']: self.main['form'](None)}
        for sub in self.subs:
            ctx[sub['form_name']] = sub['form'](None)
        return template.render(ctx)


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
        'admin/people.html', marital_status_types=MARITAL_STATUSES,
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
    ltd_plans = LTDPlan.query.all()
    ltd_plan_form = LTDPlanForm()
    add_plans = LifeADDPlan.query.all()
    add_plan_form = LifeADDPlanForm()
    addd_plans = LifeADDDependentPlan.query.all()
    addd_plan_form = LifeADDDependentPlanForm()
    return render_template('admin/group.html', eap_plans=eap_plans,
                           eap_plan_form=eap_plan_form,
                           ltd_plans=ltd_plans,
                           ltd_plan_form=ltd_plan_form,
                           add_plans=add_plans,
                           add_plan_form=add_plan_form,
                           addd_plans=addd_plans,
                           addd_plan_form=addd_plan_form)


@app.route('/admin/supplemental', methods=['GET', 'POST'])
@login_required
def admin_supplemental():
    g.active_tab = 'admin'
    g.active_step = 'supplemental'
    fsa_plans = FSAPlan.query.all()
    fsa_plan_form = FSAPlanForm()
    hsa_plans = HSAPlan.query.all()
    hsa_plan_form = HSAPlanForm()
    e401k_plans = Employee401KPlan.query.all()
    e401k_plan_form = Employee401KPlanForm()
    cancer_plans = CancerPlan.query.all()
    cancer_plan_form = CancerPlanForm()
    supp_life_plans = SupplumentalInsurancePlan.query.all()
    supp_life_plan_form = SupplementalInsurancePlanForm()
    ltc_plans = LongTermCarePlan.query.all()
    ltc_plan_form = LongTermCarePlanForm()
    critical_illness_plans = CriticalIllnessPlan.query.all()
    critical_illness_plan_form = CriticalIllnessPlanForm()
    parking_transit_plans = ParkingTransitPlan.query.all()
    parking_transit_plan_form = ParkingTransitPlanForm()
    other_plans = OtherPlan.query.all()
    other_plan_form = OtherPlanForm()
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
        supp_life_plans=supp_life_plans,
        supp_life_plan_form=supp_life_plan_form,
        cricial_illness_plans=critical_illness_plans,
        critical_illness_plan_form=critical_illness_plan_form,
        ltc_plans=ltc_plans,
        ltc_plan_form=ltc_plan_form,
        parking_transit_plans=parking_transit_plans,
        parking_transit_plan_form=parking_transit_plan_form,
        other_plans=other_plans,
        other_plan_form=other_plan_form,
        )


@app.route('/admin/premiums', methods=['GET', 'POST'])
@login_required
def admin_premiums():
    g.active_tab = 'admin'
    g.active_step = 'premiums'
    return render_template('admin/premiums.html')


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


class ADDPlanView(AJAXCrudView):
    main = {'model': LifeADDPlan, 'form': LifeADDPlanForm,
            'class': 'LifeADDPlan', 'form_class': 'LifeADDPlanForm',
            'single': 'add_plan', 'plural': 'add_plans',
            'form_name': 'add_plan_form',
            'template': '/admin/_add_plans.html'}
    subs = []


class ADDDependentPlanView(AJAXCrudView):
    main = {'model': LifeADDDependentPlan, 'form': LifeADDDependentPlanForm,
            'class': 'LifeADDPlan', 'form_class': 'LifeADDDPlanForm',
            'single': 'addd_plan', 'plural': 'addd_plans',
            'form_name': 'addd_plan_form',
            'template': '/admin/_addd_plans.html'}
    subs = []


class LTCPlanView(AJAXCrudView):
    main = {'model': LongTermCarePlan, 'form': LongTermCarePlanForm,
            'class': 'LongTermCarePlan', 'form_class': 'LongTermCarePlanForm',
            'single': 'ltc_plan', 'plural': 'ltc_plans',
            'form_name': 'ltc_plan_form',
            'template': '/admin/_ltc_plans.html'}
    subs = []


class FSAPlanView(AJAXCrudView):
    main = {'model': FSAPlan, 'form': FSAPlanForm,
            'class': 'FSAPlan', 'form_class': 'FSAPlanForm',
            'single': 'fsa_plan', 'plural': 'fsa_plans',
            'form_name': 'fsa_plan_form',
            'template': '/admin/_fsa_plans.html'}
    subs = []


class HSAPlanView(AJAXCrudView):
    main = {'model': HSAPlan, 'form': HSAPlanForm,
            'class': 'HSAPlan', 'form_class': 'HSAPlanForm',
            'single': 'hsa_plan', 'plural': 'hsa_plans',
            'form_name': 'hsa_plan_form',
            'template': '/admin/_hsa_plans.html'}
    subs = []


class SuppLifePlanView(AJAXCrudView):
    main = {'model': SupplumentalInsurancePlan,
            'form': SupplementalInsurancePlanForm,
            'class': 'SupplumentalInsurancePlan',
            'form_class': 'SupplementalInsurancePlanForm',
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
            'template': '/admin/_401k_plans.html'}
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


class OtherPlanView(AJAXCrudView):
    main = {'model': OtherPlan, 'form': OtherPlanForm,
            'class': 'OtherPlan', 'form_class': 'OtherPlanForm',
            'single': 'other_plan', 'plural': 'other_plans',
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


class LocationView(AJAXCrudView):
    main = {'model': Location, 'form': LocationForm, 'class': 'Location',
            'form_class': 'LocationForm', 'single': 'location',
            'plural': 'locations', 'form_name': 'location_form',
            'template': '/admin/_locations.html'}
    subs = []


# Enrollment
class DependentView(AJAXCrudView):
    main = {'model': Dependent, 'form': DependentForm, 'class': 'Dependent',
            'form_class': 'DepndentForm', 'single': 'dependent',
            'plural': 'dependents', 'form_name': 'dependent_form',
            'template': '/enroll/_dependents.html'}
    subs = [
        {'model': Address, 'form': AddressForm, 'class': 'Address',
         'form_class': 'AddressForm', 'single': 'address',
         'plural': 'addresss', 'form_name': 'address_form'},
    ]


def register_ajax_view(view, endpoint, url, pk='id', pk_type='int'):
    view_func = view.as_view(endpoint)
    app.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET', ])
    app.add_url_rule(url, view_func=view_func, methods=['POST', ])
    app.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

# admin
register_ajax_view(ADDDependentPlanView, 'addd_plan_ajax', '/admin/_addd_plans/')  # NOQA
register_ajax_view(ADDPlanView, 'add_plan_ajax', '/admin/_add_plans/')  # NOQA
register_ajax_view(CancerPlanView, 'cancer_plan_ajax', '/admin/_cancer_plans/')  # NOQA
register_ajax_view(CarrierView, 'carrier_ajax', '/admin/_carriers/')
register_ajax_view(CriticalPlanView, 'critical_plan_ajax', '/admin/_critical_illness_plans/')  # NOQA
register_ajax_view(DentalPlanView, 'dental_plan_ajax', '/admin/_dental_plans/')  # NOQA
register_ajax_view(EAPPlanView, 'eap_plan_ajax', '/admin/_eap_plans/')  # NOQA
register_ajax_view(Employee401kPlanView, 'employee_401k_ajax', '/admin/_401k_plans/')  # NOQA
register_ajax_view(EmployeeView, 'employee_ajax', '/admin/_employees/')  # NOQA
register_ajax_view(FSAPlanView, 'fsa_plan_ajax', '/admin/_fsa_plans/')  # NOQA
register_ajax_view(HSAPlanView, 'hsa_plan_ajax', '/admin/_hsa_plans/')  # NOQA
register_ajax_view(LTCPlanView, 'ltc_plan_ajax', '/admin/_ltc_plans/')  # NOQA
register_ajax_view(LTDPlanView, 'ltd_plan_ajax', '/admin/_ltd_plans/')  # NOQA
register_ajax_view(LocationView, 'location_ajax', '/admin/_locations/')  # NOQA
register_ajax_view(MedicalPlanView, 'medical_plan_ajax', '/admin/_medical_plans/')  # NOQA
register_ajax_view(OtherPlanView, 'other_plan_ajax', '/admin/_other_plans/')  # NOQA
register_ajax_view(ParkingTransitPlanView, 'parking_transit_plan_ajax', '/admin/_parking_transit_plans/')  # NOQA
register_ajax_view(SuppLifePlanView, 'supp_plan_ajax', '/admin/_supp_life_plans/')  # NOQA
register_ajax_view(VisionPlanView, 'vision_plan_ajax', '/admin/_vision_plans/')  # NOQA

# enroll
register_ajax_view(DependentView, 'dependent_ajax', '/enroll/_dependents/')  # NOQA
