"""initial migration

Revision ID: 5943dbc4c29b
Revises:
Create Date: 2017-09-29 13:07:53.222978

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy_utils.types.email import EmailType
from sqlalchemy_utils.types.phone_number import PhoneNumberType
from sqlalchemy_utils.types.url import URLType

from app.models import (
    BENEFICIARY_TYPES,
    DEPENDENT_TYPES,
    FAMILY_TIER_TYPES,
    GENDER_TYPES,
    LIFE_EVENT_TYPES,
    MARITAL_STATUS_TYPES,
    PLAN_TERMINATION_TIMING_TYPES,
    SALARY_MODE_TYPES,
    SMOKER_TYPES,
    STATES,
)


# revision identifiers, used by Alembic.
revision = '5943dbc4c29b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'address',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('street_1', sa.Unicode(length=100), nullable=False),
        sa.Column('street_2', sa.Unicode(length=100), nullable=True),
        sa.Column('city', sa.Unicode(length=100), nullable=False),
        sa.Column('state', ChoiceType(STATES), nullable=False),
        sa.Column('zip_code', sa.Unicode(length=10), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'carrier',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Unicode(length=50), nullable=False),
        sa.Column('phone', PhoneNumberType(length=20), nullable=True),
        sa.Column('api_endpoint', sa.Unicode(length=200), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'dependent_eligibility',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('eligible', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'domestic_partner_eligibility',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('eligible', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'employee_eligibility',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('full_time_only', sa.Boolean(), nullable=True),
        sa.Column('minimum_days_employed', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'enrollment_period',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'irs_limits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('max_fsa_medical_contribution', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('max_fsa_dependent_care_contribution', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('max_hsa_individual_contribution', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('max_hsa_family_contribution', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('max_hsa_family_over_55_contribution', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('max_401k_salary_deferal', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('max_401k_salary_deferal_over_50', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'location',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=12), nullable=False),
        sa.Column('description', sa.String(length=60), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('password_hash', sa.String(length=128), nullable=True),
        sa.Column('email', EmailType(length=255), nullable=True),
        sa.Column('reset_password_token', sa.String(length=100), server_default='', nullable=True),
        sa.Column('is_admin', sa.Boolean(), server_default='0', nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=False)
    op.create_table(
        'employee',
        sa.Column('first_name', sa.Unicode(length=50), server_default=u'', nullable=False),
        sa.Column('middle_name', sa.Unicode(length=50), server_default=u'', nullable=True),
        sa.Column('last_name', sa.Unicode(length=50), server_default=u'', nullable=False),
        sa.Column('ssn', sa.Unicode(length=11), nullable=False),
        sa.Column('dob', sa.Date(), nullable=False),
        sa.Column('gender', ChoiceType(GENDER_TYPES), nullable=True),
        sa.Column('marital_status', ChoiceType(MARITAL_STATUS_TYPES), nullable=True),
        sa.Column('smoker_type', ChoiceType(SMOKER_TYPES), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('hire_date', sa.Date(), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('termination_date', sa.Date(), nullable=True),
        sa.Column('employee_number', sa.Unicode(length=25), nullable=True),
        sa.Column('group_id', sa.String(length=50), nullable=False),
        sa.Column('sub_group_id', sa.String(length=50), nullable=False),
        sa.Column('sub_group_effective_date', sa.Date(), nullable=False),
        sa.Column('salary_mode', ChoiceType(SALARY_MODE_TYPES), nullable=True),
        sa.Column('salary_effective_date', sa.Date(), nullable=False),
        sa.Column('salary', sa.Numeric(precision=9, scale=2), nullable=False),
        sa.Column('phone', PhoneNumberType(length=20), nullable=True),
        sa.Column('alternate_phone', PhoneNumberType(length=20), nullable=True),
        sa.Column('emergency_contact_phone', PhoneNumberType(length=20), nullable=True),
        sa.Column('emergency_contact_name', sa.String(), nullable=True),
        sa.Column('emergency_contact_relationship', sa.String(), nullable=True),
        sa.Column('location_id', sa.Integer(), nullable=True),
        sa.Column('address_id', sa.Integer(), nullable=True),
        sa.Column('spouse_dob', sa.Date(), nullable=False),
        sa.Column('spouse_smoker_type', ChoiceType(SMOKER_TYPES), nullable=True),
        sa.ForeignKeyConstraint(['address_id'], ['address.id'], ),
        sa.ForeignKeyConstraint(['location_id'], ['location.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employee_user_id'), 'employee', ['user_id'], unique=False)
    op.create_table(
        'plan',
        sa.Column('er_flat_amount_contributed', sa.Numeric(precision=9, scale=2), server_default='0', nullable=True),
        sa.Column('er_percentage_contributed', sa.Numeric(precision=3, scale=2), server_default='0', nullable=True),
        sa.Column('er_max_contribution', sa.Numeric(precision=9, scale=2), server_default='0', nullable=True),
        sa.Column('salary_chunk_size', sa.Integer(), nullable=True),
        sa.Column('coverage_chunk_size', sa.Integer(), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plantype', sa.String(length=50), nullable=True),
        sa.Column('code', sa.String(length=10), nullable=True),
        sa.Column('name', sa.Unicode(length=70), nullable=False),
        sa.Column('description', sa.String(length=250), nullable=False),
        sa.Column('special_instructions', sa.String(length=250), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('carrier_id', sa.Integer(), nullable=True),
        sa.Column('website', URLType(), nullable=True),
        sa.Column('cust_service_phone', PhoneNumberType(length=20), nullable=True),
        sa.Column('required_plan_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['carrier_id'], ['carrier.id'], ),
        sa.ForeignKeyConstraint(['required_plan_id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_plan_is_active'), 'plan', ['is_active'], unique=False)
    op.create_table(
        'accident_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'age_based_reduction',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=False),
        sa.Column('percentage', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_age_based_reduction_plan_id'), 'age_based_reduction', ['plan_id'], unique=False)
    op.create_table(
        'beneficiary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('beneficiary_type', ChoiceType(BENEFICIARY_TYPES), nullable=True),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('employee_id', sa.Integer(), nullable=True),
        sa.Column('percentage', sa.Integer(), server_default='0', nullable=True),
        sa.Column('btype', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_beneficiary_plan_id'), 'beneficiary', ['plan_id'], unique=False)
    op.create_table(
        'cancer_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'child_standalone_add_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'child_voluntary_life_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'child_whole_life_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'cricial_illness_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('payout_amount', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'dental_plan',
        sa.Column('pre_tax', sa.Boolean(), nullable=False),
        sa.Column('group_number', sa.Unicode(length=24), nullable=False),
        sa.Column('original_effective_date', sa.Date(), nullable=True),
        sa.Column('renewal_date', sa.Date(), nullable=True),
        sa.Column('list_billed', sa.Boolean(), nullable=True),
        sa.Column('doctor_selection_required', sa.Boolean(), nullable=True),
        sa.Column('cobra_eligible', sa.Boolean(), nullable=False),
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_termination_timing_type_id', ChoiceType(PLAN_TERMINATION_TIMING_TYPES), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'dental_vision_bundle_plan',
        sa.Column('pre_tax', sa.Boolean(), nullable=False),
        sa.Column('group_number', sa.Unicode(length=24), nullable=False),
        sa.Column('original_effective_date', sa.Date(), nullable=True),
        sa.Column('renewal_date', sa.Date(), nullable=True),
        sa.Column('list_billed', sa.Boolean(), nullable=True),
        sa.Column('doctor_selection_required', sa.Boolean(), nullable=True),
        sa.Column('cobra_eligible', sa.Boolean(), nullable=False),
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_termination_timing_type_id', ChoiceType(PLAN_TERMINATION_TIMING_TYPES), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'dependent',
        sa.Column('first_name', sa.Unicode(length=50), server_default=u'', nullable=False),
        sa.Column('middle_name', sa.Unicode(length=50), server_default=u'', nullable=True),
        sa.Column('last_name', sa.Unicode(length=50), server_default=u'', nullable=False),
        sa.Column('ssn', sa.Unicode(length=11), nullable=False),
        sa.Column('dob', sa.Date(), nullable=False),
        sa.Column('gender', ChoiceType(GENDER_TYPES), nullable=True),
        sa.Column('marital_status', ChoiceType(MARITAL_STATUS_TYPES), nullable=True),
        sa.Column('smoker_type', ChoiceType(SMOKER_TYPES), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dependent_type', ChoiceType(DEPENDENT_TYPES), nullable=True),
        sa.Column('full_time_student', sa.Boolean(), server_default='0', nullable=True),
        sa.Column('disabled', sa.Boolean(), server_default='0', nullable=True),
        sa.Column('disability_date', sa.Date(), nullable=True),
        sa.Column('employee_id', sa.Integer(), nullable=True),
        sa.Column('address_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['address_id'], ['address.id'], ),
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'eap_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'employee_401k_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employer_percent_matched', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('employer_max_contribution', sa.Numeric(precision=9, scale=2), nullable=False),
        sa.Column('min_contribution', sa.Numeric(precision=9, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'enrollment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=True),
        sa.Column('life_event', ChoiceType(LIFE_EVENT_TYPES), nullable=True),
        sa.Column('enrollment_period_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['employee_id'], ['employee.id'], ),
        sa.ForeignKeyConstraint(['enrollment_period_id'], ['enrollment_period.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_enrollment_employee_id'), 'enrollment', ['employee_id'], unique=False)
    op.create_table(
        'fsa_dependent_care_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'fsa_medical_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('min_contribution', sa.Numeric(precision=9, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'hospital_confinement_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'hra_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'hsa_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('min_contribution', sa.Numeric(precision=9, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'identity_theft_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'life_add_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('age_based_reduction_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('multiple_of_salary_paid', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('min_benefit', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('max_benefit', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('spouse_benefit', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('child_benefit', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('guarantee_issue', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('addl_salary_multiple_accidental_death', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('addl_salary_multiple_accidental_dismemberment', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'long_term_care_plan',
        sa.Column('pre_tax', sa.Boolean(), nullable=False),
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'ltd_plan',
        sa.Column('pre_tax', sa.Boolean(), nullable=False),
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('max_monthly_benefit', sa.Numeric(precision=9, scale=2), nullable=False),
        sa.Column('percentage_of_salary_paid', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'ltd_voluntary_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'medical_dental_bundle_plan',
        sa.Column('pre_tax', sa.Boolean(), nullable=False),
        sa.Column('group_number', sa.Unicode(length=24), nullable=False),
        sa.Column('original_effective_date', sa.Date(), nullable=True),
        sa.Column('renewal_date', sa.Date(), nullable=True),
        sa.Column('list_billed', sa.Boolean(), nullable=True),
        sa.Column('doctor_selection_required', sa.Boolean(), nullable=True),
        sa.Column('cobra_eligible', sa.Boolean(), nullable=False),
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_termination_timing_type_id', ChoiceType(PLAN_TERMINATION_TIMING_TYPES), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'medical_dental_vision_bundle_plan',
        sa.Column('pre_tax', sa.Boolean(), nullable=False),
        sa.Column('group_number', sa.Unicode(length=24), nullable=False),
        sa.Column('original_effective_date', sa.Date(), nullable=True),
        sa.Column('renewal_date', sa.Date(), nullable=True),
        sa.Column('list_billed', sa.Boolean(), nullable=True),
        sa.Column('doctor_selection_required', sa.Boolean(), nullable=True),
        sa.Column('cobra_eligible', sa.Boolean(), nullable=False),
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_termination_timing_type_id', ChoiceType(PLAN_TERMINATION_TIMING_TYPES), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'medical_plan',
        sa.Column('pre_tax', sa.Boolean(), nullable=False),
        sa.Column('group_number', sa.Unicode(length=24), nullable=False),
        sa.Column('original_effective_date', sa.Date(), nullable=True),
        sa.Column('renewal_date', sa.Date(), nullable=True),
        sa.Column('list_billed', sa.Boolean(), nullable=True),
        sa.Column('doctor_selection_required', sa.Boolean(), nullable=True),
        sa.Column('cobra_eligible', sa.Boolean(), nullable=False),
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_termination_timing_type_id', ChoiceType(PLAN_TERMINATION_TIMING_TYPES), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'medical_vision_bundle_plan',
        sa.Column('pre_tax', sa.Boolean(), nullable=False),
        sa.Column('group_number', sa.Unicode(length=24), nullable=False),
        sa.Column('original_effective_date', sa.Date(), nullable=True),
        sa.Column('renewal_date', sa.Date(), nullable=True),
        sa.Column('list_billed', sa.Boolean(), nullable=True),
        sa.Column('doctor_selection_required', sa.Boolean(), nullable=True),
        sa.Column('cobra_eligible', sa.Boolean(), nullable=False),
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_termination_timing_type_id', ChoiceType(PLAN_TERMINATION_TIMING_TYPES), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'other_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'parking_transit_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'premium',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('rate', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('gender', ChoiceType(GENDER_TYPES), nullable=True),
        sa.Column('smoker_status', ChoiceType(SMOKER_TYPES), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('age_band_low', sa.Integer(), nullable=True),
        sa.Column('age_band_high', sa.Integer(), nullable=True),
        sa.Column('family_tier', ChoiceType(FAMILY_TIER_TYPES), nullable=True),
        sa.Column('payout_amount', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_premium_plan_id'), 'premium', ['plan_id'], unique=False)
    op.create_table(
        'spouse_standalone_add_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'spouse_voluntary_life_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('use_employee_age_for_spouse', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'spouse_whole_life_plan',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'standalone_add_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('increments', sa.Integer(), nullable=True),
        sa.Column('min_election', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('max_election', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'std_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('max_weekly_benefit', sa.Numeric(precision=9, scale=2), nullable=False),
        sa.Column('percentage_of_salary_paid', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'std_voluntary_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('max_weekly_benefit', sa.Numeric(precision=9, scale=2), nullable=False),
        sa.Column('percentage_of_salary_paid', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'universal_life_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('age_based_reduction_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('spouse_benefit', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('child_benefit', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'vision_plan',
        sa.Column('pre_tax', sa.Boolean(), nullable=False),
        sa.Column('group_number', sa.Unicode(length=24), nullable=False),
        sa.Column('original_effective_date', sa.Date(), nullable=True),
        sa.Column('renewal_date', sa.Date(), nullable=True),
        sa.Column('list_billed', sa.Boolean(), nullable=True),
        sa.Column('doctor_selection_required', sa.Boolean(), nullable=True),
        sa.Column('cobra_eligible', sa.Boolean(), nullable=False),
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('plan_termination_timing_type_id', ChoiceType(PLAN_TERMINATION_TIMING_TYPES), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'voluntary_life_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('increments', sa.Integer(), nullable=True),
        sa.Column('min_election', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('max_election', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('guarantee_issue', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('addl_salary_multiple_accidental_death', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('addl_salary_multiple_accidental_dismemberment', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'whole_life_plan',
        sa.Column('premium_matrix', sa.String(length=5000), nullable=True),
        sa.Column('age_based_reduction_matrix', sa.String(length=5000), nullable=True),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('spouse_benefit', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.Column('child_benefit', sa.Numeric(precision=9, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['plan.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'dependent_beneficiary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('dependent_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['dependent_id'], ['dependent.id'], ),
        sa.ForeignKeyConstraint(['id'], ['beneficiary.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'election',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('enrollment_id', sa.Integer(), nullable=True),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('premium_id', sa.Integer(), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=True),
        sa.Column('elected', sa.Boolean(), nullable=True),
        sa.Column('total_cost', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('employer_cost', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.Column('employee_cost', sa.Numeric(precision=6, scale=2), nullable=True),
        sa.ForeignKeyConstraint(['enrollment_id'], ['enrollment.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ),
        sa.ForeignKeyConstraint(['premium_id'], ['premium.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_election_plan_id'), 'election', ['plan_id'], unique=False)
    op.create_table(
        'estate_beneficiary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['beneficiary.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'succession_of_heirs_beneficiary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['id'], ['beneficiary.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('succession_of_heirs_beneficiary')
    op.drop_table('estate_beneficiary')
    op.drop_index(op.f('ix_election_plan_id'), table_name='election')
    op.drop_table('election')
    op.drop_table('dependent_beneficiary')
    op.drop_table('whole_life_plan')
    op.drop_table('voluntary_life_plan')
    op.drop_table('vision_plan')
    op.drop_table('universal_life_plan')
    op.drop_table('std_voluntary_plan')
    op.drop_table('std_plan')
    op.drop_table('standalone_add_plan')
    op.drop_table('spouse_whole_life_plan')
    op.drop_table('spouse_voluntary_life_plan')
    op.drop_table('spouse_standalone_add_plan')
    op.drop_index(op.f('ix_premium_plan_id'), table_name='premium')
    op.drop_table('premium')
    op.drop_table('parking_transit_plan')
    op.drop_table('other_plan')
    op.drop_table('medical_vision_bundle_plan')
    op.drop_table('medical_plan')
    op.drop_table('medical_dental_vision_bundle_plan')
    op.drop_table('medical_dental_bundle_plan')
    op.drop_table('ltd_voluntary_plan')
    op.drop_table('ltd_plan')
    op.drop_table('long_term_care_plan')
    op.drop_table('life_add_plan')
    op.drop_table('identity_theft_plan')
    op.drop_table('hsa_plan')
    op.drop_table('hra_plan')
    op.drop_table('hospital_confinement_plan')
    op.drop_table('fsa_medical_plan')
    op.drop_table('fsa_dependent_care_plan')
    op.drop_index(op.f('ix_enrollment_employee_id'), table_name='enrollment')
    op.drop_table('enrollment')
    op.drop_table('employee_401k_plan')
    op.drop_table('eap_plan')
    op.drop_table('dependent')
    op.drop_table('dental_vision_bundle_plan')
    op.drop_table('dental_plan')
    op.drop_table('cricial_illness_plan')
    op.drop_table('child_whole_life_plan')
    op.drop_table('child_voluntary_life_plan')
    op.drop_table('child_standalone_add_plan')
    op.drop_table('cancer_plan')
    op.drop_index(op.f('ix_beneficiary_plan_id'), table_name='beneficiary')
    op.drop_table('beneficiary')
    op.drop_index(op.f('ix_age_based_reduction_plan_id'), table_name='age_based_reduction')
    op.drop_table('age_based_reduction')
    op.drop_table('accident_plan')
    op.drop_index(op.f('ix_plan_is_active'), table_name='plan')
    op.drop_table('plan')
    op.drop_index(op.f('ix_employee_user_id'), table_name='employee')
    op.drop_table('employee')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('location')
    op.drop_table('irs_limits')
    op.drop_table('enrollment_period')
    op.drop_table('employee_eligibility')
    op.drop_table('domestic_partner_eligibility')
    op.drop_table('dependent_eligibility')
    op.drop_table('carrier')
    op.drop_table('address')
