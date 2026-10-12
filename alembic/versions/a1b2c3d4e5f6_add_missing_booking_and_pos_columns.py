"""add_missing_booking_and_pos_columns

Revision ID: a1b2c3d4e5f6
Revises: 77a97b43997f
Create Date: 2026-10-12 20:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '77a97b43997f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # 1. bookings columns
    if 'bookings' in existing_tables:
        booking_cols = {c['name'] for c in inspector.get_columns('bookings')}
        if 'grc_number' not in booking_cols:
            op.add_column('bookings', sa.Column('grc_number', sa.String(length=50), nullable=True))
        if 'num_pax' not in booking_cols:
            op.add_column('bookings', sa.Column('num_pax', sa.Integer(), nullable=True, server_default='1'))
        if 'second_pax_name' not in booking_cols:
            op.add_column('bookings', sa.Column('second_pax_name', sa.String(length=100), nullable=True))
        if 'second_pax_phone' not in booking_cols:
            op.add_column('bookings', sa.Column('second_pax_phone', sa.String(length=30), nullable=True))
        if 'second_pax_id' not in booking_cols:
            op.add_column('bookings', sa.Column('second_pax_id', sa.String(length=100), nullable=True))
        if 'plan_code' not in booking_cols:
            op.add_column('bookings', sa.Column('plan_code', sa.String(length=20), nullable=True, server_default='EP'))
        if 'billing_mode' not in booking_cols:
            op.add_column('bookings', sa.Column('billing_mode', sa.String(length=50), nullable=True, server_default='Cash'))
        if 'vehicle_no' not in booking_cols:
            op.add_column('bookings', sa.Column('vehicle_no', sa.String(length=50), nullable=True))
        if 'purpose_of_visit' not in booking_cols:
            op.add_column('bookings', sa.Column('purpose_of_visit', sa.String(length=100), nullable=True, server_default='Business Visit'))

    # 2. restaurant_tables columns
    if 'restaurant_tables' in existing_tables:
        table_cols = {c['name'] for c in inspector.get_columns('restaurant_tables')}
        if 'outlet' not in table_cols:
            op.add_column('restaurant_tables', sa.Column('outlet', sa.String(length=50), nullable=True, server_default='RESTAURANT'))
        if 'outlet_code' not in table_cols:
            op.add_column('restaurant_tables', sa.Column('outlet_code', sa.String(length=20), nullable=True, server_default='RES'))
        if 'location_view' not in table_cols:
            op.add_column('restaurant_tables', sa.Column('location_view', sa.String(length=100), nullable=True, server_default='AC MAIN HALL'))

    # 3. pos_orders columns
    if 'pos_orders' in existing_tables:
        order_cols = {c['name'] for c in inspector.get_columns('pos_orders')}
        if 'steward_name' not in order_cols:
            op.add_column('pos_orders', sa.Column('steward_name', sa.String(length=100), nullable=True, server_default='Santosh Biswal'))
        if 'cooking_note' not in order_cols:
            op.add_column('pos_orders', sa.Column('cooking_note', sa.Text(), nullable=True))
        if 'is_jain_satvik' not in order_cols:
            op.add_column('pos_orders', sa.Column('is_jain_satvik', sa.Boolean(), nullable=True, server_default=sa.false()))

    # 4. corporate_accounts columns
    if 'corporate_accounts' in existing_tables:
        corp_cols = {c['name'] for c in inspector.get_columns('corporate_accounts')}
        if 'company_code' not in corp_cols:
            op.add_column('corporate_accounts', sa.Column('company_code', sa.String(length=30), nullable=True))
        if 'pan_number' not in corp_cols:
            op.add_column('corporate_accounts', sa.Column('pan_number', sa.String(length=30), nullable=True))
        if 'address' not in corp_cols:
            op.add_column('corporate_accounts', sa.Column('address', sa.Text(), nullable=True))
        if 'city' not in corp_cols:
            op.add_column('corporate_accounts', sa.Column('city', sa.String(length=100), nullable=True, server_default='Rayagada'))
        if 'state' not in corp_cols:
            op.add_column('corporate_accounts', sa.Column('state', sa.String(length=100), nullable=True, server_default='Odisha'))
        if 'pin_code' not in corp_cols:
            op.add_column('corporate_accounts', sa.Column('pin_code', sa.String(length=20), nullable=True, server_default='765017'))
        if 'linked_rate_table' not in corp_cols:
            op.add_column('corporate_accounts', sa.Column('linked_rate_table', sa.String(length=30), nullable=True, server_default='100'))
        if 'billing_type' not in corp_cols:
            op.add_column('corporate_accounts', sa.Column('billing_type', sa.String(length=30), nullable=True, server_default='BTC'))

    # 5. menu_items columns
    if 'menu_items' in existing_tables:
        menu_cols = {c['name'] for c in inspector.get_columns('menu_items')}
        if 'uom' not in menu_cols:
            op.add_column('menu_items', sa.Column('uom', sa.String(length=20), nullable=True, server_default='POR'))
        if 'tax_rate' not in menu_cols:
            op.add_column('menu_items', sa.Column('tax_rate', sa.Float(), nullable=True, server_default='5.0'))
        if 'sac_hsn_code' not in menu_cols:
            op.add_column('menu_items', sa.Column('sac_hsn_code', sa.String(length=20), nullable=True, server_default='996331'))
        if 'discount_allowed' not in menu_cols:
            op.add_column('menu_items', sa.Column('discount_allowed', sa.Boolean(), nullable=True, server_default=sa.true()))
        if 'portions_json' not in menu_cols:
            op.add_column('menu_items', sa.Column('portions_json', sa.Text(), nullable=True, server_default='[]'))


def downgrade() -> None:
    pass
