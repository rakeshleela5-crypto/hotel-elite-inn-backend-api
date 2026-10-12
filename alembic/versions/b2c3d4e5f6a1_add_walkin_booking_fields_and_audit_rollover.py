"""add_walkin_booking_fields_and_audit_rollover

Adds 11 new columns to the bookings table that the IDS Walk-In modal
already collects but were missing from the DB schema:
  - nationality, arrival_from, proceeding_to, identification_no
  - company_name, rate_authorized_by, special_instructions
  - guest_status, rate_amount, rate_option

Also adds rollover_status to night_audit_logs for the new rollover endpoint.

Revision ID: b2c3d4e5f6a1
Revises: a1b2c3d4e5f6
Create Date: 2026-10-12 23:40:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a1'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add 11 missing columns to bookings table (Walk-In modal audit fix)
    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.add_column(sa.Column('nationality', sa.String(length=50), nullable=True, server_default='India'))
        batch_op.add_column(sa.Column('arrival_from', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('proceeding_to', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('identification_no', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('company_name', sa.String(length=150), nullable=True))
        batch_op.add_column(sa.Column('rate_authorized_by', sa.String(length=100), nullable=True, server_default='MANAGER'))
        batch_op.add_column(sa.Column('special_instructions', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('guest_status', sa.String(length=20), nullable=True, server_default='WLK'))
        batch_op.add_column(sa.Column('rate_amount', sa.Float(), nullable=True, server_default=sa.text('0.0')))
        batch_op.add_column(sa.Column('rate_option', sa.String(length=30), nullable=True, server_default='DISCOUNT'))

    # Add rollover_status to night_audit_logs for the new /api/night-audit/rollover endpoint
    with op.batch_alter_table('night_audit_logs', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rollover_status', sa.String(length=20), nullable=True, server_default='PENDING'))


def downgrade() -> None:
    with op.batch_alter_table('night_audit_logs', schema=None) as batch_op:
        batch_op.drop_column('rollover_status')

    with op.batch_alter_table('bookings', schema=None) as batch_op:
        batch_op.drop_column('rate_option')
        batch_op.drop_column('rate_amount')
        batch_op.drop_column('guest_status')
        batch_op.drop_column('special_instructions')
        batch_op.drop_column('rate_authorized_by')
        batch_op.drop_column('company_name')
        batch_op.drop_column('identification_no')
        batch_op.drop_column('proceeding_to')
        batch_op.drop_column('arrival_from')
        batch_op.drop_column('nationality')
