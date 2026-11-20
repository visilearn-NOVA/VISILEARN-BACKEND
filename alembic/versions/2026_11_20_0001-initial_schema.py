"""Initial normalized database schema for VisiLearn.

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-11-20 09:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Users Table
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_users'))
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 2. Students Table
    op.create_table(
        'students',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=True),
        sa.Column('matric_number', sa.String(length=50), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=False),
        sa.Column('programme', sa.String(length=150), nullable=False),
        sa.Column('current_level', sa.Integer(), nullable=False),
        sa.Column('gender', sa.String(length=20), nullable=False),
        sa.Column('enrollment_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_students_user_id_users'), ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_students')),
        sa.UniqueConstraint('user_id', name=op.f('uq_students_user_id'))
    )
    op.create_index(op.f('ix_students_department'), 'students', ['department'], unique=False)
    op.create_index(op.f('ix_students_id'), 'students', ['id'], unique=False)
    op.create_index(op.f('ix_students_matric_number'), 'students', ['matric_number'], unique=True)
    op.create_index(op.f('ix_students_programme'), 'students', ['programme'], unique=False)

    # 3. Academic Records Table
    op.create_table(
        'academic_records',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('academic_year', sa.String(length=20), nullable=False),
        sa.Column('semester', sa.Integer(), nullable=False),
        sa.Column('semester_gpa', sa.Float(), nullable=False),
        sa.Column('cumulative_gpa', sa.Float(), nullable=False),
        sa.Column('total_credits_registered', sa.Integer(), nullable=False),
        sa.Column('total_credits_earned', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_academic_records_student_id_students'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_academic_records')),
        sa.UniqueConstraint('student_id', 'academic_year', 'semester', name='uq_student_academic_semester')
    )
    op.create_index(op.f('ix_academic_records_id'), 'academic_records', ['id'], unique=False)
    op.create_index(op.f('ix_academic_records_student_id'), 'academic_records', ['student_id'], unique=False)

    # 4. Course Enrollments Table
    op.create_table(
        'course_enrollments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('academic_record_id', sa.Uuid(), nullable=False),
        sa.Column('course_code', sa.String(length=20), nullable=False),
        sa.Column('course_title', sa.String(length=150), nullable=False),
        sa.Column('credit_units', sa.Integer(), nullable=False),
        sa.Column('grade_point', sa.Float(), nullable=False),
        sa.Column('letter_grade', sa.String(length=2), nullable=False),
        sa.ForeignKeyConstraint(['academic_record_id'], ['academic_records.id'], name=op.f('fk_course_enrollments_academic_record_id_academic_records'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_course_enrollments'))
    )
    op.create_index(op.f('ix_course_enrollments_academic_record_id'), 'course_enrollments', ['academic_record_id'], unique=False)
    op.create_index(op.f('ix_course_enrollments_id'), 'course_enrollments', ['id'], unique=False)

    # 5. Survey Responses Table
    op.create_table(
        'survey_responses',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('survey_version', sa.String(length=20), nullable=False),
        sa.Column('study_hours_per_week', sa.Float(), nullable=False),
        sa.Column('attendance_rate_pct', sa.Float(), nullable=False),
        sa.Column('sleep_hours_per_night', sa.Float(), nullable=False),
        sa.Column('travel_time_minutes', sa.Integer(), nullable=False),
        sa.Column('internet_access', sa.String(length=20), nullable=False),
        sa.Column('class_participation', sa.String(length=20), nullable=False),
        sa.Column('parental_education', sa.String(length=30), nullable=False),
        sa.Column('social_media_hours_per_day', sa.Float(), nullable=False),
        sa.Column('participates_extracurricular', sa.Boolean(), nullable=False),
        sa.Column('stress_level', sa.String(length=20), nullable=False),
        sa.Column('financial_support', sa.String(length=20), nullable=False),
        sa.Column('additional_attributes', sa.JSON(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_survey_responses_student_id_students'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_survey_responses'))
    )
    op.create_index(op.f('ix_survey_responses_id'), 'survey_responses', ['id'], unique=False)
    op.create_index(op.f('ix_survey_responses_student_id'), 'survey_responses', ['student_id'], unique=False)

    # 6. Predictions Table
    op.create_table(
        'predictions',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('predicted_gpa', sa.Float(), nullable=False),
        sa.Column('performance_category', sa.String(length=50), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('input_features_snapshot', sa.JSON(), nullable=False),
        sa.Column('feature_importances_snapshot', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_predictions_student_id_students'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_predictions'))
    )
    op.create_index(op.f('ix_predictions_id'), 'predictions', ['id'], unique=False)
    op.create_index(op.f('ix_predictions_student_id'), 'predictions', ['student_id'], unique=False)

    # 7. Prediction History Table
    op.create_table(
        'prediction_history',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('prediction_id', sa.Uuid(), nullable=False),
        sa.Column('student_id', sa.Uuid(), nullable=False),
        sa.Column('change_reason', sa.String(length=255), nullable=False),
        sa.Column('prior_predicted_gpa', sa.Float(), nullable=True),
        sa.Column('new_predicted_gpa', sa.Float(), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('recorded_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['prediction_id'], ['predictions.id'], name=op.f('fk_prediction_history_prediction_id_predictions'), ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_prediction_history_student_id_students'), ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_prediction_history'))
    )
    op.create_index(op.f('ix_prediction_history_id'), 'prediction_history', ['id'], unique=False)
    op.create_index(op.f('ix_prediction_history_prediction_id'), 'prediction_history', ['prediction_id'], unique=False)
    op.create_index(op.f('ix_prediction_history_student_id'), 'prediction_history', ['student_id'], unique=False)


def downgrade() -> None:
    op.drop_table('prediction_history')
    op.drop_table('predictions')
    op.drop_table('survey_responses')
    op.drop_table('course_enrollments')
    op.drop_table('academic_records')
    op.drop_table('students')
    op.drop_table('users')
