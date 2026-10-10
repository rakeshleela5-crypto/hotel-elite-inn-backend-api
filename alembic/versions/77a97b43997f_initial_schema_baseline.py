"""initial_schema_baseline

Revision ID: 77a97b43997f
Revises: 
Create Date: 2026-10-10 23:52:40.629062

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77a97b43997f'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - safe idempotent baseline creation."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # 1. corporate_accounts
    if 'corporate_accounts' not in existing_tables:
        op.create_table('corporate_accounts',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('company_name', sa.String(length=150), nullable=False),
            sa.Column('gst_number', sa.String(length=50), nullable=True),
            sa.Column('contact_person', sa.String(length=100), nullable=True),
            sa.Column('contact_phone', sa.String(length=30), nullable=True),
            sa.Column('contact_email', sa.String(length=100), nullable=True),
            sa.Column('credit_limit', sa.Float(), nullable=True),
            sa.Column('current_outstanding', sa.Float(), nullable=True),
            sa.Column('billing_cycle_days', sa.Integer(), nullable=True),
            sa.Column('last_billed_date', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('company_name')
        )
        op.create_index(op.f('ix_corporate_accounts_id'), 'corporate_accounts', ['id'], unique=False)

    # 2. gstr1_filings
    if 'gstr1_filings' not in existing_tables:
        op.create_table('gstr1_filings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('return_period', sa.String(length=20), nullable=False),
            sa.Column('invoice_number', sa.String(length=50), nullable=False),
            sa.Column('invoice_date', sa.String(length=30), nullable=False),
            sa.Column('invoice_type', sa.String(length=30), nullable=True),
            sa.Column('customer_name', sa.String(length=150), nullable=False),
            sa.Column('customer_gstin', sa.String(length=50), nullable=True),
            sa.Column('place_of_supply', sa.String(length=50), nullable=True),
            sa.Column('hsn_sac_code', sa.String(length=20), nullable=True),
            sa.Column('taxable_value', sa.Float(), nullable=True),
            sa.Column('cgst_rate', sa.Float(), nullable=True),
            sa.Column('cgst_amount', sa.Float(), nullable=True),
            sa.Column('sgst_rate', sa.Float(), nullable=True),
            sa.Column('sgst_amount', sa.Float(), nullable=True),
            sa.Column('igst_rate', sa.Float(), nullable=True),
            sa.Column('igst_amount', sa.Float(), nullable=True),
            sa.Column('total_invoice_value', sa.Float(), nullable=True),
            sa.Column('filing_status', sa.String(length=30), nullable=True),
            sa.Column('acknowledgement_num', sa.String(length=100), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_gstr1_filings_id'), 'gstr1_filings', ['id'], unique=False)
        op.create_index(op.f('ix_gstr1_filings_invoice_number'), 'gstr1_filings', ['invoice_number'], unique=False)
        op.create_index(op.f('ix_gstr1_filings_return_period'), 'gstr1_filings', ['return_period'], unique=False)

    # 3. inventory_items
    if 'inventory_items' not in existing_tables:
        op.create_table('inventory_items',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('item_code', sa.String(length=50), nullable=False),
            sa.Column('item_name', sa.String(length=100), nullable=False),
            sa.Column('category', sa.String(length=50), nullable=False),
            sa.Column('unit', sa.String(length=20), nullable=True),
            sa.Column('current_stock', sa.Float(), nullable=True),
            sa.Column('min_reorder_level', sa.Float(), nullable=True),
            sa.Column('cost_per_unit', sa.Float(), nullable=True),
            sa.Column('last_updated', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('item_code')
        )
        op.create_index(op.f('ix_inventory_items_id'), 'inventory_items', ['id'], unique=False)

    # 4. laundry_orders
    if 'laundry_orders' not in existing_tables:
        op.create_table('laundry_orders',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('reference_number', sa.String(length=50), nullable=False),
            sa.Column('room_number', sa.String(length=20), nullable=False),
            sa.Column('guest_name', sa.String(length=100), nullable=False),
            sa.Column('service_type', sa.String(length=30), nullable=True),
            sa.Column('items_detail', sa.Text(), nullable=True),
            sa.Column('total_pieces', sa.Integer(), nullable=True),
            sa.Column('rate_amount', sa.Float(), nullable=True),
            sa.Column('express_surcharge', sa.Float(), nullable=True),
            sa.Column('tax_amount', sa.Float(), nullable=True),
            sa.Column('total_amount', sa.Float(), nullable=True),
            sa.Column('order_status', sa.String(length=30), nullable=True),
            sa.Column('billing_status', sa.String(length=30), nullable=True),
            sa.Column('received_date', sa.String(length=30), nullable=False),
            sa.Column('expected_delivery', sa.String(length=30), nullable=True),
            sa.Column('delivered_at', sa.DateTime(), nullable=True),
            sa.Column('attendant', sa.String(length=100), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_laundry_orders_id'), 'laundry_orders', ['id'], unique=False)
        op.create_index(op.f('ix_laundry_orders_reference_number'), 'laundry_orders', ['reference_number'], unique=True)

    # 5. menu_items
    if 'menu_items' not in existing_tables:
        op.create_table('menu_items',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('item_code', sa.String(length=30), nullable=False),
            sa.Column('name', sa.String(length=120), nullable=False),
            sa.Column('category', sa.String(length=60), nullable=False),
            sa.Column('price', sa.Float(), nullable=False),
            sa.Column('is_veg', sa.Boolean(), nullable=True),
            sa.Column('description', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_menu_items_id'), 'menu_items', ['id'], unique=False)
        op.create_index(op.f('ix_menu_items_item_code'), 'menu_items', ['item_code'], unique=True)

    # 6. night_audit_logs
    if 'night_audit_logs' not in existing_tables:
        op.create_table('night_audit_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('audit_date', sa.String(length=30), nullable=False),
            sa.Column('sealed_by', sa.String(length=100), nullable=True),
            sa.Column('total_revenue', sa.Float(), nullable=True),
            sa.Column('room_revenue', sa.Float(), nullable=True),
            sa.Column('f_and_b_revenue', sa.Float(), nullable=True),
            sa.Column('cash_reconciled', sa.Float(), nullable=True),
            sa.Column('corporate_aging_due', sa.Float(), nullable=True),
            sa.Column('status', sa.String(length=30), nullable=True),
            sa.Column('timestamp', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_night_audit_logs_id'), 'night_audit_logs', ['id'], unique=False)

    # 7. restaurant_tables
    if 'restaurant_tables' not in existing_tables:
        op.create_table('restaurant_tables',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('table_number', sa.String(length=20), nullable=False),
            sa.Column('capacity', sa.Integer(), nullable=True),
            sa.Column('status', sa.String(length=30), nullable=True),
            sa.Column('merged_into_table_id', sa.Integer(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('table_number')
        )
        op.create_index(op.f('ix_restaurant_tables_id'), 'restaurant_tables', ['id'], unique=False)

    # 8. room_defects
    if 'room_defects' not in existing_tables:
        op.create_table('room_defects',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('room_number', sa.String(length=20), nullable=False),
            sa.Column('defect_type', sa.String(length=50), nullable=False),
            sa.Column('description', sa.Text(), nullable=False),
            sa.Column('severity', sa.String(length=20), nullable=True),
            sa.Column('status', sa.String(length=30), nullable=True),
            sa.Column('reported_at', sa.DateTime(), nullable=True),
            sa.Column('resolved_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_room_defects_id'), 'room_defects', ['id'], unique=False)

    # 9. rooms
    if 'rooms' not in existing_tables:
        op.create_table('rooms',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('number', sa.String(length=20), nullable=False),
            sa.Column('category', sa.String(length=50), nullable=False),
            sa.Column('base_price', sa.Float(), nullable=False),
            sa.Column('status', sa.String(length=30), nullable=False),
            sa.Column('floor', sa.Integer(), nullable=True),
            sa.Column('amenities', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_rooms_id'), 'rooms', ['id'], unique=False)
        op.create_index(op.f('ix_rooms_number'), 'rooms', ['number'], unique=True)

    # 10. staff_attendance
    if 'staff_attendance' not in existing_tables:
        op.create_table('staff_attendance',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('staff_id', sa.String(length=30), nullable=False),
            sa.Column('staff_name', sa.String(length=100), nullable=False),
            sa.Column('department', sa.String(length=50), nullable=False),
            sa.Column('designation', sa.String(length=60), nullable=False),
            sa.Column('shift', sa.String(length=50), nullable=True),
            sa.Column('attendance_date', sa.String(length=30), nullable=False),
            sa.Column('punch_in_time', sa.String(length=30), nullable=True),
            sa.Column('punch_out_time', sa.String(length=30), nullable=True),
            sa.Column('status', sa.String(length=30), nullable=True),
            sa.Column('remarks', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_staff_attendance_attendance_date'), 'staff_attendance', ['attendance_date'], unique=False)
        op.create_index(op.f('ix_staff_attendance_id'), 'staff_attendance', ['id'], unique=False)
        op.create_index(op.f('ix_staff_attendance_staff_id'), 'staff_attendance', ['staff_id'], unique=False)

    # 11. bookings
    if 'bookings' not in existing_tables:
        op.create_table('bookings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('booking_reference', sa.String(length=50), nullable=False),
            sa.Column('guest_name', sa.String(length=100), nullable=False),
            sa.Column('guest_phone', sa.String(length=30), nullable=False),
            sa.Column('guest_email', sa.String(length=100), nullable=True),
            sa.Column('guest_id_type', sa.String(length=50), nullable=True),
            sa.Column('guest_id_number', sa.String(length=50), nullable=True),
            sa.Column('room_id', sa.Integer(), nullable=False),
            sa.Column('check_in_date', sa.DateTime(), nullable=False),
            sa.Column('check_out_date', sa.DateTime(), nullable=False),
            sa.Column('status', sa.String(length=30), nullable=True),
            sa.Column('total_amount', sa.Float(), nullable=True),
            sa.Column('advance_paid', sa.Float(), nullable=True),
            sa.Column('balance_amount', sa.Float(), nullable=True),
            sa.Column('corporate_account_id', sa.Integer(), nullable=True),
            sa.Column('key_handed_over', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['corporate_account_id'], ['corporate_accounts.id'], ),
            sa.ForeignKeyConstraint(['room_id'], ['rooms.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_bookings_booking_reference'), 'bookings', ['booking_reference'], unique=True)
        op.create_index(op.f('ix_bookings_id'), 'bookings', ['id'], unique=False)

    # 12. pos_orders
    if 'pos_orders' not in existing_tables:
        op.create_table('pos_orders',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('order_number', sa.String(length=50), nullable=False),
            sa.Column('table_id', sa.Integer(), nullable=True),
            sa.Column('room_number', sa.String(length=20), nullable=True),
            sa.Column('order_type', sa.String(length=30), nullable=True),
            sa.Column('subtotal', sa.Float(), nullable=True),
            sa.Column('tax_amount', sa.Float(), nullable=True),
            sa.Column('discount_amount', sa.Float(), nullable=True),
            sa.Column('final_amount', sa.Float(), nullable=True),
            sa.Column('payment_status', sa.String(length=30), nullable=True),
            sa.Column('payment_method', sa.String(length=30), nullable=True),
            sa.Column('status', sa.String(length=30), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['table_id'], ['restaurant_tables.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_pos_orders_id'), 'pos_orders', ['id'], unique=False)
        op.create_index(op.f('ix_pos_orders_order_number'), 'pos_orders', ['order_number'], unique=True)

    # 13. pos_order_items
    if 'pos_order_items' not in existing_tables:
        op.create_table('pos_order_items',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('order_id', sa.Integer(), nullable=False),
            sa.Column('item_name', sa.String(length=100), nullable=False),
            sa.Column('quantity', sa.Integer(), nullable=True),
            sa.Column('rate', sa.Float(), nullable=True),
            sa.Column('amount', sa.Float(), nullable=True),
            sa.Column('kot_status', sa.String(length=30), nullable=True),
            sa.Column('is_voided', sa.Boolean(), nullable=True),
            sa.Column('void_reason', sa.String(length=255), nullable=True),
            sa.Column('void_authorized_by', sa.String(length=100), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['order_id'], ['pos_orders.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_pos_order_items_id'), 'pos_order_items', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_pos_order_items_id'), table_name='pos_order_items')
    op.drop_table('pos_order_items')
    op.drop_index(op.f('ix_pos_orders_order_number'), table_name='pos_orders')
    op.drop_index(op.f('ix_pos_orders_id'), table_name='pos_orders')
    op.drop_table('pos_orders')
    op.drop_index(op.f('ix_bookings_id'), table_name='bookings')
    op.drop_index(op.f('ix_bookings_booking_reference'), table_name='bookings')
    op.drop_table('bookings')
    op.drop_index(op.f('ix_staff_attendance_staff_id'), table_name='staff_attendance')
    op.drop_index(op.f('ix_staff_attendance_id'), table_name='staff_attendance')
    op.drop_index(op.f('ix_staff_attendance_attendance_date'), table_name='staff_attendance')
    op.drop_table('staff_attendance')
    op.drop_index(op.f('ix_rooms_number'), table_name='rooms')
    op.drop_index(op.f('ix_rooms_id'), table_name='rooms')
    op.drop_table('rooms')
    op.drop_index(op.f('ix_room_defects_id'), table_name='room_defects')
    op.drop_table('room_defects')
    op.drop_index(op.f('ix_restaurant_tables_id'), table_name='restaurant_tables')
    op.drop_table('restaurant_tables')
    op.drop_index(op.f('ix_night_audit_logs_id'), table_name='night_audit_logs')
    op.drop_table('night_audit_logs')
    op.drop_index(op.f('ix_menu_items_item_code'), table_name='menu_items')
    op.drop_index(op.f('ix_menu_items_id'), table_name='menu_items')
    op.drop_table('menu_items')
    op.drop_index(op.f('ix_laundry_orders_reference_number'), table_name='laundry_orders')
    op.drop_index(op.f('ix_laundry_orders_id'), table_name='laundry_orders')
    op.drop_table('laundry_orders')
    op.drop_index(op.f('ix_inventory_items_id'), table_name='inventory_items')
    op.drop_table('inventory_items')
    op.drop_index(op.f('ix_gstr1_filings_return_period'), table_name='gstr1_filings')
    op.drop_index(op.f('ix_gstr1_filings_invoice_number'), table_name='gstr1_filings')
    op.drop_index(op.f('ix_gstr1_filings_id'), table_name='gstr1_filings')
    op.drop_table('gstr1_filings')
    op.drop_index(op.f('ix_corporate_accounts_id'), table_name='corporate_accounts')
    op.drop_table('corporate_accounts')
