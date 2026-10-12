from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, UniqueConstraint
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


class Gstr1Filing(Base):
    __tablename__ = "gstr1_filings"

    id = Column(Integer, primary_key=True, index=True)
    return_period = Column(String(20), index=True, nullable=False) # e.g. "OCT-2026"
    invoice_number = Column(String(50), index=True, nullable=False)
    invoice_date = Column(String(30), nullable=False) # e.g. "10-OCT-2026"
    invoice_type = Column(String(30), default="B2B") # 'B2B', 'B2CS', 'B2CL'
    customer_name = Column(String(150), nullable=False)
    customer_gstin = Column(String(50), nullable=True) # e.g. "21AAACJ1122K1Z9"
    place_of_supply = Column(String(50), default="21-Odisha")
    hsn_sac_code = Column(String(20), default="996311") # 996311 (Room), 996331 (F&B)
    taxable_value = Column(Float, default=0.0)
    cgst_rate = Column(Float, default=6.0)
    cgst_amount = Column(Float, default=0.0)
    sgst_rate = Column(Float, default=6.0)
    sgst_amount = Column(Float, default=0.0)
    igst_rate = Column(Float, default=0.0)
    igst_amount = Column(Float, default=0.0)
    total_invoice_value = Column(Float, default=0.0)
    filing_status = Column(String(30), default="Ready for Upload") # 'Ready for Upload', 'Uploaded', 'Filed'
    acknowledgement_num = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class StaffAttendance(Base):
    __tablename__ = "staff_attendance"

    id = Column(Integer, primary_key=True, index=True)
    staff_id = Column(String(30), index=True, nullable=False) # e.g. "EMP-001"
    staff_name = Column(String(100), nullable=False)
    department = Column(String(50), nullable=False) # 'Front Office', 'Housekeeping', 'Food & Beverage', 'Kitchen', 'Accounts'
    designation = Column(String(60), nullable=False)
    shift = Column(String(50), default="Morning (07:00-15:00)")
    attendance_date = Column(String(30), index=True, nullable=False) # e.g. "10-OCT-2026"
    punch_in_time = Column(String(30), nullable=True) # e.g. "06:55 AM"
    punch_out_time = Column(String(30), nullable=True) # e.g. "03:10 PM"
    status = Column(String(30), default="Present") # 'Present', 'Half Day', 'Late', 'Absent', 'On Leave'
    remarks = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class LaundryOrder(Base):
    __tablename__ = "laundry_orders"

    id = Column(Integer, primary_key=True, index=True)
    reference_number = Column(String(50), unique=True, index=True, nullable=False) # e.g. "LND-2026-001"
    room_number = Column(String(20), nullable=False) # "102", "201", "301"
    guest_name = Column(String(100), nullable=False)
    service_type = Column(String(30), default="Normal") # 'Normal', 'Express (+50%)', 'Dry Clean'
    items_detail = Column(Text, nullable=True) # e.g. "Shirt x 2, Trouser x 2"
    total_pieces = Column(Integer, default=1)
    rate_amount = Column(Float, default=0.0)
    express_surcharge = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    order_status = Column(String(30), default="Received") # 'Received', 'In-Process', 'Ready', 'Delivered'
    billing_status = Column(String(30), default="Billed to Room") # 'Billed to Room', 'Direct Cash', 'Complimentary'
    received_date = Column(String(30), nullable=False) # e.g. "10-OCT-2026"
    expected_delivery = Column(String(30), nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    attendant = Column(String(100), default="Sunil Mohapatra")
    created_at = Column(DateTime, default=datetime.utcnow)


class FolioTransaction(Base):
    __tablename__ = "folio_transactions"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), index=True, nullable=False) # e.g. "102"
    folio_number = Column(Integer, default=1)
    guest_name = Column(String(100), nullable=False)
    transaction_type = Column(String(50), nullable=False) # 'Room Charge', 'POS F&B', 'Laundry', 'Advance Deposit', 'Allowance', 'Paid Out'
    voucher_or_bill_no = Column(String(50), nullable=True)
    particulars = Column(String(255), nullable=False)
    sac_code = Column(String(20), default="996311")
    debit_amount = Column(Float, default=0.0) # Charged to guest
    credit_amount = Column(Float, default=0.0) # Paid / allowed by guest
    tax_amount = Column(Float, default=0.0)
    posting_date = Column(String(30), nullable=False) # e.g. "11-OCT-2026"
    posted_by = Column(String(100), default="MANAGER")
    is_settled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AdvanceDeposit(Base):
    __tablename__ = "advance_deposits"

    id = Column(Integer, primary_key=True, index=True)
    receipt_number = Column(String(50), unique=True, index=True, nullable=False) # e.g. "REC-2026-001"
    room_number = Column(String(20), index=True, nullable=False)
    guest_name = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    payment_mode = Column(String(30), default="Cash") # 'Cash', 'UPI', 'Credit Card', 'Bank Transfer'
    reference_no = Column(String(100), nullable=True)
    remarks = Column(String(255), default="Room Advance Deposit")
    status = Column(String(30), default="Active") # 'Active', 'Adjusted', 'Deleted', 'Refunded'
    date = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class PaidOutVoucher(Base):
    __tablename__ = "paid_out_vouchers"

    id = Column(Integer, primary_key=True, index=True)
    voucher_number = Column(String(50), unique=True, index=True, nullable=False) # e.g. "POV-2026-001"
    room_number = Column(String(20), index=True, nullable=False)
    guest_name = Column(String(100), nullable=False)
    paid_amount = Column(Float, nullable=False)
    purpose = Column(String(255), nullable=False) # e.g. "Guest Taxi Fare Advance", "Medicine Refund"
    authorized_by = Column(String(100), default="Duty Manager")
    date = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ForexEncashment(Base):
    __tablename__ = "forex_encashments"

    id = Column(Integer, primary_key=True, index=True)
    encashment_no = Column(String(50), unique=True, index=True, nullable=False) # e.g. "ENC/2026/001"
    room_number = Column(String(20), nullable=False)
    guest_name = Column(String(100), nullable=False)
    passport_number = Column(String(50), nullable=False)
    nationality = Column(String(50), default="USA")
    currency_code = Column(String(10), nullable=False) # 'USD', 'EUR', 'GBP', 'AED'
    foreign_amount = Column(Float, nullable=False)
    exchange_rate = Column(Float, nullable=False)
    inr_value = Column(Float, nullable=False)
    gst_amount = Column(Float, default=0.0)
    net_payable = Column(Float, nullable=False)
    date = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class LostAndFoundItem(Base):
    __tablename__ = "lost_and_found_items"

    id = Column(Integer, primary_key=True, index=True)
    tracking_no = Column(String(50), unique=True, index=True, nullable=False) # e.g. "LF-2026-001"
    item_description = Column(String(255), nullable=False)
    room_number = Column(String(20), nullable=True)
    found_location = Column(String(100), default="Room")
    found_by = Column(String(100), default="Housekeeping Attendant")
    found_date = Column(String(30), nullable=False)
    status = Column(String(30), default="Found/Stored") # 'Found/Stored', 'Claimed/Returned', 'Disposed'
    claimed_by = Column(String(100), nullable=True)
    claim_date = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RoomTransferLog(Base):
    __tablename__ = "room_transfer_logs"

    id = Column(Integer, primary_key=True, index=True)
    guest_name = Column(String(100), nullable=False)
    from_room = Column(String(20), nullable=False)
    to_room = Column(String(20), nullable=False)
    reason = Column(String(255), default="Guest Preference / Maintenance Move")
    authorized_by = Column(String(100), default="Front Office Duty Manager")
    transfer_date = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CorporateRateLink(Base):
    __tablename__ = "corporate_rate_links"

    id = Column(Integer, primary_key=True, index=True)
    company_code = Column(String(30), index=True, nullable=False) # e.g. "COM0001"
    company_name = Column(String(150), nullable=False) # e.g. "Ashok Leyland Ltd"
    rate_table_no = Column(String(30), nullable=False) # "100", "101", "102"
    description = Column(String(255), nullable=False)
    valid_from = Column(String(30), nullable=False)
    valid_to = Column(String(30), nullable=False)
    status = Column(String(30), default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)


class HotelSaleRecord(Base):
    __tablename__ = "hotel_sale_records"

    id = Column(Integer, primary_key=True, index=True)
    serial_no = Column(Integer, index=True)
    date = Column(String(30), index=True, nullable=False)
    bill_no = Column(String(50), index=True, nullable=False)
    room_number = Column(String(20), index=True, nullable=False)
    rent = Column(Float, default=0.0)
    cgst = Column(Float, default=0.0)
    sgst = Column(Float, default=0.0)
    misc = Column(Float, default=0.0)
    laundry = Column(Float, default=0.0)
    minibar = Column(Float, default=0.0)
    room_service = Column(Float, default=0.0)
    net_amount = Column(Float, default=0.0)
    advance = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    complimentary = Column(Float, default=0.0)
    void_amount = Column(Float, default=0.0)
    allowances = Column(Float, default=0.0)
    paid_out = Column(Float, default=0.0)
    cash = Column(Float, default=0.0)
    btc = Column(Float, default=0.0)
    credit_card = Column(Float, default=0.0)
    online = Column(Float, default=0.0)
    remark = Column(String(255), default="")
    guest_name = Column(String(150), default="")
    company = Column(String(150), default="FIT")
    gstin = Column(String(50), nullable=True)
    month = Column(String(20), default="JUNE-2026")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('bill_no', 'month', name='uq_hotel_bill_month'),
    )


class RestaurantSaleRecord(Base):
    __tablename__ = "restaurant_sale_records"

    id = Column(Integer, primary_key=True, index=True)
    running_no = Column(Integer, index=True)
    date = Column(String(30), index=True, nullable=False)
    bill_no = Column(String(50), index=True, nullable=False)
    amount = Column(Float, default=0.0)
    food = Column(Float, default=0.0)
    beverage = Column(Float, default=0.0)
    cgst = Column(Float, default=0.0)
    sgst = Column(Float, default=0.0)
    discount = Column(Float, default=0.0)
    total = Column(Float, default=0.0)
    pos_outlet = Column(String(50), default="RESTAURANT")
    table_room = Column(String(50), default="")
    cost_center = Column(String(150), default="")
    auth_officer = Column(String(100), default="")
    reason = Column(String(255), default="")
    settlement_mode = Column(String(50), default="Cash")
    is_management_nc = Column(Boolean, default=False)
    month = Column(String(20), default="JUNE-2026")
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint('bill_no', 'month', name='uq_restaurant_bill_month'),
    )


class StorePurchase(Base):
    __tablename__ = "store_purchases"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. "PUR-2026-001"
    vendor_name = Column(String(150), index=True, nullable=False)
    invoice_no = Column(String(50), nullable=True)
    purchase_date = Column(String(30), index=True, nullable=False)
    category = Column(String(50), default="Groceries")
    items_summary = Column(Text, nullable=True)
    total_amount = Column(Float, default=0.0)
    payment_status = Column(String(50), default="Cash Paid") # 'Cash Paid', 'Credit', 'UPI Paid'
    received_by = Column(String(100), default="STORE INCHARGE")
    created_at = Column(DateTime, default=datetime.utcnow)


class KitchenRequisition(Base):
    __tablename__ = "kitchen_requisitions"

    id = Column(Integer, primary_key=True, index=True)
    requisition_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. "REQ-2026-001"
    issue_date = Column(String(30), index=True, nullable=False)
    target_outlet = Column(String(50), default="Main Kitchen") # 'Main Kitchen', 'Tandoor Section', 'Bakery'
    item_name = Column(String(100), nullable=False)
    quantity_issued = Column(Float, default=0.0)
    unit = Column(String(20), default="KG")
    approx_cost = Column(Float, default=0.0)
    issued_to = Column(String(100), default="HEAD CHEF")
    issued_by = Column(String(100), default="STORE KEEPER")
    created_at = Column(DateTime, default=datetime.utcnow)


class VendorPayable(Base):
    __tablename__ = "vendor_payables"

    id = Column(Integer, primary_key=True, index=True)
    vendor_name = Column(String(150), unique=True, index=True, nullable=False)
    category = Column(String(100), default="General Supplier")
    contact = Column(String(100), nullable=True)
    supplies_amount = Column(Float, default=0.0)
    paid_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


# =============================================================
# Category 1: Front Office PMS & Guest Management Models
# =============================================================
class PoliceManifest(Base):
    __tablename__ = "police_manifests"

    id = Column(Integer, primary_key=True, index=True)
    room_no = Column(String(20), index=True, nullable=False)
    name = Column(String(150), nullable=False)
    mobile = Column(String(30), nullable=False)
    age = Column(Integer, default=30)
    gender = Column(String(20), default="Male")
    id_proof_type = Column(String(50), default="Aadhaar Card")
    id_proof_no = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    arrived_from = Column(String(100), default="Rayagada")
    destination = Column(String(100), default="Muniguda")
    purpose = Column(String(255), default="Business Visit")
    vehicle_no = Column(String(50), nullable=True)
    check_in_time = Column(String(50), nullable=False)
    expected_check_out = Column(String(50), nullable=True)
    status = Column(String(30), default="In-House") # 'In-House', 'Checked Out'
    guest_type = Column(String(50), default="Corporate")
    created_at = Column(DateTime, default=datetime.utcnow)


class ForeignerFormC(Base):
    __tablename__ = "foreigner_form_c"

    id = Column(Integer, primary_key=True, index=True)
    form_c_no = Column(String(50), unique=True, index=True, nullable=False)
    room_no = Column(String(20), nullable=False)
    guest_name = Column(String(150), nullable=False)
    passport_no = Column(String(50), nullable=False)
    visa_no = Column(String(50), nullable=False)
    nationality = Column(String(50), default="Foreign")
    arrival_date = Column(String(30), nullable=False)
    departure_date = Column(String(30), nullable=True)
    purpose_of_visit = Column(String(255), default="Technical Consultant")
    indian_ref_contact = Column(String(150), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class GuestKycDocument(Base):
    __tablename__ = "guest_kyc_documents"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), index=True, nullable=False)
    guest_name = Column(String(150), nullable=False)
    doc_type = Column(String(50), default="Aadhaar Card")
    doc_number_masked = Column(String(50), nullable=False)
    id_file_url = Column(String(255), nullable=True)
    verified_by = Column(String(100), default="FRONT DESK")
    verified_at = Column(DateTime, default=datetime.utcnow)


class CashierShiftRecord(Base):
    __tablename__ = "cashier_shift_records"

    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(String(30), index=True, nullable=False) # 'shift1', 'shift2', 'shift3'
    shift_name = Column(String(100), nullable=False) # 'Shift 1 — Morning', 'Shift 2 — Evening', 'Shift 3 — Night'
    cashier_name = Column(String(100), nullable=False) # 'Ranjan Kumar Dash (FO-01)'
    cashier_code = Column(String(30), nullable=False) # 'FO-01', 'FO-02', 'FO-03'
    accounting_date = Column(String(30), index=True, nullable=False) # e.g. "02-10-2026"
    status = Column(String(30), default="OPEN") # 'OPEN', 'CLOSED'
    drawer_float = Column(Float, default=2000.0) # Opening drawer float
    safe_drop = Column(Float, default=0.0)
    denominations_json = Column(Text, default="{}") # {n500: 4, n200: 0, n100: 0, coins: 0}
    physical_cash = Column(Float, default=2000.0)
    collections_json = Column(Text, default="{}") # {cash: 0, upi: 0, card: 0, btc: 0, total: 0}
    fnb_split_json = Column(Text, default="{}") # {roomService: 0, restaurant: 0, takeAway: 0}
    handover_notes = Column(Text, default="")
    closed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# =============================================================
# Category 2: Folio Accounting & Adjustments Models
# =============================================================
class FolioChargeTransfer(Base):
    __tablename__ = "folio_charge_transfers"

    id = Column(Integer, primary_key=True, index=True)
    from_room = Column(String(20), nullable=False)
    to_room = Column(String(20), nullable=False)
    from_folio = Column(Integer, default=1)
    to_folio = Column(Integer, default=1)
    amount = Column(Float, nullable=False)
    charge_type = Column(String(50), default="Room Charge")
    reason = Column(String(255), default="Guest Request / Combined Billing")
    authorized_by = Column(String(100), default="Duty Manager")
    created_at = Column(DateTime, default=datetime.utcnow)


class BillAllowance(Base):
    __tablename__ = "bill_allowances"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), nullable=False)
    folio_number = Column(Integer, default=1)
    bill_no = Column(String(50), nullable=True)
    allowance_amount = Column(Float, nullable=False)
    tax_reversed = Column(Float, default=0.0)
    reason = Column(String(255), nullable=False) # 'Service Deficiency Rebate', 'Manager Courtesy Discount'
    approved_by = Column(String(100), default="GENERAL MANAGER")
    date = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class CorporateSplitBilling(Base):
    __tablename__ = "corporate_split_billings"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), nullable=False)
    corporate_id = Column(Integer, nullable=True)
    company_name = Column(String(150), nullable=False)
    btc_amount = Column(Float, default=0.0) # Room rent + GST to company
    personal_amount = Column(Float, default=0.0) # Food + personal laundry to guest
    billing_date = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class RoomBlock(Base):
    __tablename__ = "room_blocks"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), index=True, nullable=False)
    block_type = Column(String(50), default="Maintenance") # 'Out of Order', 'Out of Service', 'VIP Hold', 'Painting/AC Work'
    reason = Column(String(255), nullable=False)
    start_date = Column(String(30), nullable=False)
    end_date = Column(String(30), nullable=False)
    blocked_by = Column(String(100), default="MAINTENANCE ENGINEER")
    status = Column(String(30), default="ACTIVE") # 'ACTIVE', 'RELEASED'
    created_at = Column(DateTime, default=datetime.utcnow)


# =============================================================
# Category 3: POS, F&B & Banquet Models
# =============================================================
class BanquetEvent(Base):
    __tablename__ = "banquet_events"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(50), unique=True, index=True, nullable=False) # e.g. "BNQ-2026-001"
    event_name = Column(String(150), nullable=False) # e.g. "JK Paper Annual Dealers Conference"
    host_name = Column(String(150), nullable=False)
    host_phone = Column(String(30), nullable=False)
    event_date = Column(String(30), index=True, nullable=False)
    slot = Column(String(50), default="Full Day") # 'Morning (09:00-14:00)', 'Evening (18:00-23:00)', 'Full Day'
    pax = Column(Integer, default=50)
    hall_name = Column(String(100), default="Grand Ballroom / Conference Hall")
    hall_rental = Column(Float, default=15000.0)
    food_package_rate = Column(Float, default=650.0) # Per pax
    menu_summary = Column(Text, default="Buffet Lunch + Hi-Tea + Dinner")
    subtotal = Column(Float, default=0.0)
    gst_amount = Column(Float, default=0.0) # 18% GST (SAC 997212)
    total_amount = Column(Float, default=0.0)
    advance_paid = Column(Float, default=0.0)
    balance_due = Column(Float, default=0.0)
    status = Column(String(30), default="Confirmed") # 'Enquiry', 'Confirmed', 'Running', 'Settled', 'Cancelled'
    created_at = Column(DateTime, default=datetime.utcnow)


class PosServer(Base):
    __tablename__ = "pos_servers"

    id = Column(Integer, primary_key=True, index=True)
    server_code = Column(String(20), unique=True, index=True, nullable=False) # 'S-01', 'C-01'
    name = Column(String(100), nullable=False)
    role = Column(String(50), default="Steward") # 'Captain', 'Steward', 'Trainee'
    section = Column(String(50), default="Restaurant") # 'Restaurant', 'Room Service', 'Banquet'
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# =============================================================
# Category 4: Store, Materials & Inventory Models
# =============================================================
class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    po_number = Column(String(50), unique=True, index=True, nullable=False) # 'PO-2026-001'
    vendor_name = Column(String(150), index=True, nullable=False)
    order_date = Column(String(30), nullable=False)
    expected_delivery = Column(String(30), nullable=True)
    status = Column(String(30), default="Draft") # 'Draft', 'Approved', 'Partially Received', 'Completed', 'Cancelled'
    total_amount = Column(Float, default=0.0)
    items_detail_json = Column(Text, default="[]") # [{item_code, item_name, quantity, unit, rate, amount}]
    approved_by = Column(String(100), default="STORE MANAGER")
    created_at = Column(DateTime, default=datetime.utcnow)


class GoodsReceiptNote(Base):
    __tablename__ = "goods_receipt_notes"

    id = Column(Integer, primary_key=True, index=True)
    grn_number = Column(String(50), unique=True, index=True, nullable=False) # 'GRN-2026-001'
    po_number = Column(String(50), nullable=True)
    vendor_name = Column(String(150), nullable=False)
    challan_no = Column(String(50), nullable=True)
    invoice_no = Column(String(50), nullable=True)
    received_date = Column(String(30), nullable=False)
    total_val = Column(Float, default=0.0)
    verified_by = Column(String(100), default="STORE INCHARGE")
    items_received_json = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow)


class StoreIssueVoucher(Base):
    __tablename__ = "store_issue_vouchers"

    id = Column(Integer, primary_key=True, index=True)
    voucher_no = Column(String(50), unique=True, index=True, nullable=False) # 'SIV-2026-001'
    department = Column(String(50), nullable=False) # 'Kitchen', 'Housekeeping', 'Front Desk', 'Maintenance'
    target_outlet = Column(String(50), default="Main Kitchen")
    item_name = Column(String(100), nullable=False)
    quantity = Column(Float, default=0.0)
    unit = Column(String(20), default="KG")
    cost = Column(Float, default=0.0)
    issued_by = Column(String(100), default="STORE KEEPER")
    received_by = Column(String(100), default="HEAD CHEF")
    issue_date = Column(String(30), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# =============================================================
# Category 5: Housekeeping, Linen & Asset Models
# =============================================================
class LinenInventory(Base):
    __tablename__ = "linen_inventory"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), unique=True, nullable=False) # 'King Bedsheet White', 'Bath Towel 650 GSM', etc.
    category = Column(String(50), default="Bed Linen") # 'Bed Linen', 'Bath Linen', 'F&B Linen'
    total_stock = Column(Integer, default=100)
    in_use = Column(Integer, default=54)
    in_laundry = Column(Integer, default=20)
    discard_count = Column(Integer, default=0)
    unit_cost = Column(Float, default=450.0)
    par_stock = Column(Integer, default=120)
    last_audited = Column(String(30), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class RoomAmenityTracker(Base):
    __tablename__ = "room_amenity_tracker"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(100), unique=True, nullable=False) # 'Dental Kit', 'Herbal Soap 30g', 'Shampoo 30ml', 'Mineral Water 1L'
    par_stock = Column(Integer, default=200)
    current_stock = Column(Integer, default=150)
    unit = Column(String(20), default="Pcs")
    daily_consumption = Column(Integer, default=30)
    last_updated = Column(DateTime, default=datetime.utcnow)


class HousekeepingInspection(Base):
    __tablename__ = "housekeeping_inspections"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), index=True, nullable=False)
    inspector = Column(String(100), default="HK Executive")
    inspection_date = Column(String(30), nullable=False)
    score = Column(Float, default=100.0) # 0 - 100%
    remarks = Column(Text, default="Bed properly tucked, washroom sanitized, mini amenities restocked")
    checklist_json = Column(Text, default="{}")
    status = Column(String(30), default="Passed") # 'Passed', 'Needs Touchup', 'Failed'
    created_at = Column(DateTime, default=datetime.utcnow)


# =============================================================
# Category 7: Corporate BTC, Aging, TDS & Bank Recon Models
# =============================================================
class BankReconciliation(Base):
    __tablename__ = "bank_reconciliations"

    id = Column(Integer, primary_key=True, index=True)
    statement_date = Column(String(30), index=True, nullable=False)
    bank_name = Column(String(100), default="State Bank of India (SBI) - Muniguda Branch")
    account_number = Column(String(50), default="38910294812")
    statement_balance = Column(Float, default=0.0)
    book_balance = Column(Float, default=0.0)
    uncredited_cheques = Column(Float, default=0.0)
    unpresented_cheques = Column(Float, default=0.0)
    reconciled_balance = Column(Float, default=0.0)
    difference = Column(Float, default=0.0)
    status = Column(String(30), default="Reconciled") # 'Reconciled', 'Variance Pending'
    reconciled_by = Column(String(100), default="CHIEF ACCOUNTANT")
    created_at = Column(DateTime, default=datetime.utcnow)


class TdsTcsRecord(Base):
    __tablename__ = "tds_tcs_records"

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String(50), index=True, nullable=False)
    corporate_name = Column(String(150), index=True, nullable=False)
    gstin = Column(String(50), nullable=True)
    tan_no = Column(String(50), nullable=True)
    section = Column(String(20), default="194C") # '194C' (1%/2% Contractor), '194J' (10% Prof/Tech)
    gross_amount = Column(Float, default=0.0)
    tds_rate = Column(Float, default=2.0)
    tds_amount = Column(Float, default=0.0)
    net_receivable = Column(Float, default=0.0)
    financial_year = Column(String(20), default="2026-27")
    quarter = Column(String(10), default="Q3")
    created_at = Column(DateTime, default=datetime.utcnow)


class TransitSlot(Base):
    __tablename__ = "transit_slots"

    id = Column(Integer, primary_key=True, index=True)
    room_number = Column(String(20), index=True, nullable=False)
    guest_name = Column(String(120), nullable=False)
    mobile = Column(String(20), nullable=False)
    age = Column(Integer, default=30)
    train_number = Column(String(50), nullable=False) # e.g. "18518 (Visakhapatnam - Korba Express)"
    pnr_number = Column(String(50), nullable=True)
    destination = Column(String(150), nullable=True)
    rate_bracket = Column(Float, default=500.0) # ₹500 or ₹600 for 3 hours
    check_in_time = Column(String(30), nullable=False)
    expected_check_out = Column(String(30), nullable=False)
    status = Column(String(30), default="Occupied") # 'Occupied', 'Completed', 'Extended'
    created_at = Column(DateTime, default=datetime.utcnow)


class SalesPromotion(Base):
    __tablename__ = "sales_promotions"

    id = Column(Integer, primary_key=True, index=True)
    promo_code = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=False)
    discount_percentage = Column(Float, default=0.0)
    flat_discount_amount = Column(Float, default=0.0)
    applicable_outlet = Column(String(50), default="ALL") # 'ALL', 'RESTAURANT', 'ROOM_SERVICE', 'BAR'
    min_order_amount = Column(Float, default=0.0)
    valid_from = Column(String(30), nullable=False)
    valid_to = Column(String(30), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)



