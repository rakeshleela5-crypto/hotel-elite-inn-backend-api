from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String(20), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=False) # 'Deluxe Room', 'Super Deluxe', 'Executive Suite'
    base_price = Column(Float, nullable=False, default=2499.0)
    status = Column(String(30), nullable=False, default="clean") # 'clean', 'dirty', 'occupied', 'maintenance'
    floor = Column(Integer, default=1)
    amenities = Column(Text, default="High-Speed Wi-Fi, Smart TV, Hot Water, Work Desk")
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="room")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_reference = Column(String(50), unique=True, index=True, nullable=False)
    guest_name = Column(String(100), nullable=False)
    guest_phone = Column(String(30), nullable=False)
    guest_email = Column(String(100), nullable=True)
    guest_id_type = Column(String(50), default="Aadhaar Card")
    guest_id_number = Column(String(50), nullable=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    check_in_date = Column(DateTime, nullable=False)
    check_out_date = Column(DateTime, nullable=False)
    status = Column(String(30), default="confirmed") # 'confirmed', 'checked_in', 'checked_out', 'cancelled'
    total_amount = Column(Float, default=0.0)
    advance_paid = Column(Float, default=0.0)
    balance_amount = Column(Float, default=0.0)
    corporate_account_id = Column(Integer, ForeignKey("corporate_accounts.id"), nullable=True)
    key_handed_over = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    room = relationship("Room", back_populates="bookings")
    corporate_account = relationship("CorporateAccount", back_populates="bookings")


class RestaurantTable(Base):
    __tablename__ = "restaurant_tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String(20), unique=True, nullable=False) # T-1, T-2, etc.
    capacity = Column(Integer, default=4)
    status = Column(String(30), default="available") # 'available', 'occupied', 'merged', 'reserved'
    merged_into_table_id = Column(Integer, nullable=True) # Merged into another table for single bill
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    orders = relationship("PosOrder", back_populates="table")


class PosOrder(Base):
    __tablename__ = "pos_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    table_id = Column(Integer, ForeignKey("restaurant_tables.id"), nullable=True)
    room_number = Column(String(20), nullable=True)
    order_type = Column(String(30), default="dine_in") # 'dine_in', 'room_service', 'takeaway'
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    discount_amount = Column(Float, default=0.0)
    final_amount = Column(Float, default=0.0)
    payment_status = Column(String(30), default="pending") # 'pending', 'paid', 'billed_to_room', 'billed_to_company'
    payment_method = Column(String(30), nullable=True) # 'Cash', 'UPI', 'Credit Card', 'Direct Billing'
    status = Column(String(30), default="open") # 'open', 'settled', 'cancelled'
    created_at = Column(DateTime, default=datetime.utcnow)

    table = relationship("RestaurantTable", back_populates="orders")
    items = relationship("PosOrderItem", back_populates="order", cascade="all, delete-orphan")


class PosOrderItem(Base):
    __tablename__ = "pos_order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("pos_orders.id"), nullable=False)
    item_name = Column(String(100), nullable=False)
    quantity = Column(Integer, default=1)
    rate = Column(Float, default=0.0)
    amount = Column(Float, default=0.0)
    kot_status = Column(String(30), default="printed") # 'pending', 'printed', 'served', 'voided'
    is_voided = Column(Boolean, default=False)
    void_reason = Column(String(255), nullable=True) # e.g. 'Guest Disliked Taste / Food Quality Reject'
    void_authorized_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("PosOrder", back_populates="items")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(50), unique=True, nullable=False)
    item_name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False) # 'Kitchen Raw Food', 'Dairy & Poultry', 'Beverages', 'Gas & Fuel'
    unit = Column(String(20), default="KG") # 'KG', 'Ltr', 'Pcs', 'Cylinders'
    current_stock = Column(Float, default=0.0)
    min_reorder_level = Column(Float, default=10.0)
    cost_per_unit = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CorporateAccount(Base):
    __tablename__ = "corporate_accounts"

    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(150), unique=True, nullable=False)
    gst_number = Column(String(50), nullable=True)
    contact_person = Column(String(100), nullable=True)
    contact_phone = Column(String(30), nullable=True)
    contact_email = Column(String(100), nullable=True)
    credit_limit = Column(Float, default=100000.0)
    current_outstanding = Column(Float, default=0.0)
    billing_cycle_days = Column(Integer, default=30)
    last_billed_date = Column(DateTime, nullable=True)

    bookings = relationship("Booking", back_populates="corporate_account")


class RoomDefect(Base):
    __tablename__ = "room_defects"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), nullable=False)
    defect_type = Column(String(50), nullable=False) # 'AC / Cooling Defect', 'Geyser / Plumbing', 'Electrical'
    description = Column(Text, nullable=False)
    severity = Column(String(20), default="High") # 'Low', 'Medium', 'High', 'Critical'
    status = Column(String(30), default="reported") # 'reported', 'in_progress', 'resolved'
    reported_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


class NightAuditLog(Base):
    __tablename__ = "night_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    audit_date = Column(String(30), nullable=False)
    sealed_by = Column(String(100), default="Duty Manager")
    total_revenue = Column(Float, default=0.0)
    room_revenue = Column(Float, default=0.0)
    f_and_b_revenue = Column(Float, default=0.0)
    cash_reconciled = Column(Float, default=0.0)
    corporate_aging_due = Column(Float, default=0.0)
    status = Column(String(30), default="SEALED")
    timestamp = Column(DateTime, default=datetime.utcnow)


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(120), nullable=False)
    category = Column(String(60), nullable=False)
    price = Column(Float, nullable=False)
    is_veg = Column(Boolean, default=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

