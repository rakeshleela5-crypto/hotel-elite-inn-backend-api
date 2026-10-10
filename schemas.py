from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

# Base & Room Schemas
class RoomBase(BaseModel):
    number: str
    category: str
    base_price: float
    status: str = "clean"
    floor: int = 1
    amenities: Optional[str] = None

class RoomCreate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RoomStatusUpdate(BaseModel):
    status: str # 'clean', 'dirty', 'occupied', 'maintenance'

# Booking Schemas
class BookingCreate(BaseModel):
    guest_name: str
    guest_phone: str
    guest_email: Optional[str] = None
    guest_id_type: str = "Aadhaar Card"
    guest_id_number: Optional[str] = None
    room_id: int
    check_in_date: datetime
    check_out_date: datetime
    advance_paid: float = 0.0
    corporate_account_id: Optional[int] = None

class BookingResponse(BaseModel):
    id: int
    booking_reference: str
    guest_name: str
    guest_phone: str
    guest_email: Optional[str] = None
    guest_id_type: str
    guest_id_number: Optional[str] = None
    room_id: int
    check_in_date: datetime
    check_out_date: datetime
    status: str
    total_amount: float
    advance_paid: float
    balance_amount: float
    corporate_account_id: Optional[int] = None
    key_handed_over: bool
    created_at: datetime

    class Config:
        from_attributes = True

# POS Schemas
class PosOrderItemCreate(BaseModel):
    item_name: str
    quantity: int = 1
    rate: float

class PosOrderItemResponse(BaseModel):
    id: int
    order_id: int
    item_name: str
    quantity: int
    rate: float
    amount: float
    kot_status: str
    is_voided: bool
    void_reason: Optional[str] = None
    void_authorized_by: Optional[str] = None

    class Config:
        from_attributes = True

class PosOrderCreate(BaseModel):
    table_id: Optional[int] = None
    room_number: Optional[str] = None
    order_type: str = "dine_in" # 'dine_in', 'room_service', 'takeaway'
    items: List[PosOrderItemCreate]

class PosOrderResponse(BaseModel):
    id: int
    order_number: str
    table_id: Optional[int] = None
    room_number: Optional[str] = None
    order_type: str
    subtotal: float
    tax_amount: float
    discount_amount: float
    final_amount: float
    payment_status: str
    payment_method: Optional[str] = None
    status: str
    created_at: datetime
    items: List[PosOrderItemResponse] = []

    class Config:
        from_attributes = True

class VoidItemRequest(BaseModel):
    reason: str = Field(..., description="Statutory void reason (e.g. 'Guest Disliked Taste / Food Quality Reject')")
    manager_pin: str = Field(..., description="Manager Authorization PIN")
    authorized_by: str = Field(default="Duty Manager")

class TableMergeRequest(BaseModel):
    source_table_id: int
    target_table_id: int
    manager_pin: str

class OrderSettleRequest(BaseModel):
    payment_method: str = "Cash" # 'Cash', 'UPI', 'Credit Card', 'Bill to Room', 'Bill to Company'
    discount_amount: float = 0.0

# Inventory Schemas
class InventoryItemBase(BaseModel):
    item_code: str
    item_name: str
    category: str
    unit: str
    current_stock: float
    min_reorder_level: float
    cost_per_unit: float

class InventoryItemResponse(InventoryItemBase):
    id: int
    last_updated: datetime

    class Config:
        from_attributes = True

class StockAdjustmentRequest(BaseModel):
    quantity_change: float
    reason: str

# Corporate Account Schemas
class CorporateAccountResponse(BaseModel):
    id: int
    company_name: str
    gst_number: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    credit_limit: float
    current_outstanding: float
    billing_cycle_days: int
    last_billed_date: Optional[datetime] = None

    class Config:
        from_attributes = True

class CorporatePaymentRequest(BaseModel):
    amount: float
    payment_reference: str
    notes: Optional[str] = None

# Housekeeping Defect Schemas
class RoomDefectCreate(BaseModel):
    room_number: str
    defect_type: str
    description: str
    severity: str = "High"

class RoomDefectResponse(BaseModel):
    id: int
    room_number: str
    defect_type: str
    description: str
    severity: str
    status: str
    reported_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Night Audit Schemas
class NightAuditRequest(BaseModel):
    audit_date: str
    manager_pin: str
    sealed_by: str = "Night Auditor"

class NightAuditResponse(BaseModel):
    id: int
    audit_date: str
    sealed_by: str
    total_revenue: float
    room_revenue: float
    f_and_b_revenue: float
    cash_reconciled: float
    corporate_aging_due: float
    status: str
    timestamp: datetime

    class Config:
        from_attributes = True

# Dashboard Stats Schema
class DashboardStats(BaseModel):
    total_rooms: int
    occupied_rooms: int
    occupancy_rate: float
    total_revenue_today: float
    room_revenue_today: float
    f_and_b_revenue_today: float
    open_pos_orders: int
    corporate_aging_due: float
    active_defects: int

# Menu Item Schemas
class MenuItemCreate(BaseModel):
    item_code: str
    name: str
    category: str
    price: float
    is_veg: bool = True
    description: Optional[str] = None

class MenuItemResponse(BaseModel):
    id: int
    item_code: str
    name: str
    category: str
    price: float
    is_veg: bool
    description: Optional[str] = None

    class Config:
        from_attributes = True

# Property Info Schema
class PropertyInfoResponse(BaseModel):
    name: str
    trade_name: str
    location: str
    phone: str
    email: str
    checkout_policy: str
    accepted_cards: str
    tariffs: dict
    plans: dict
    complimentary: List[str]
    facilities: List[str]
    wifi: dict
    intercom: List[dict]
    gstin: Optional[str] = "21AEWFS9433F1ZN"
    sac_code: Optional[str] = "996332"
    fssai_no: Optional[str] = "10523016000047"
    cashier: Optional[str] = "Bikram26"
    place_of_supply: Optional[str] = "O.D"


# -------------------------------------------------------------
# GST GSTR-1 Filing Schemas
# -------------------------------------------------------------
class Gstr1FilingCreate(BaseModel):
    return_period: str # "OCT-2026"
    invoice_number: str
    invoice_date: str # "10-OCT-2026"
    invoice_type: str = "B2B" # 'B2B', 'B2CS', 'B2CL'
    customer_name: str
    customer_gstin: Optional[str] = None
    place_of_supply: str = "21-Odisha"
    hsn_sac_code: str = "996311"
    taxable_value: float
    cgst_rate: float = 6.0
    cgst_amount: float
    sgst_rate: float = 6.0
    sgst_amount: float
    igst_rate: float = 0.0
    igst_amount: float = 0.0
    total_invoice_value: float
    filing_status: str = "Ready for Upload"

class Gstr1FilingResponse(Gstr1FilingCreate):
    id: int
    acknowledgement_num: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class Gstr1SummaryResponse(BaseModel):
    return_period: str
    total_invoices: int
    b2b_invoices_count: int
    b2cs_invoices_count: int
    total_taxable_value: float
    total_cgst: float
    total_sgst: float
    total_igst: float
    total_tax_liability: float
    total_invoice_value: float
    hsn_breakdown: List[dict]


# -------------------------------------------------------------
# Staff Attendance Schemas
# -------------------------------------------------------------
class StaffAttendanceCreate(BaseModel):
    staff_id: str
    staff_name: str
    department: str
    designation: str
    shift: str = "Morning (07:00-15:00)"
    attendance_date: str
    punch_in_time: Optional[str] = None
    punch_out_time: Optional[str] = None
    status: str = "Present"
    remarks: Optional[str] = None

class StaffAttendanceResponse(StaffAttendanceCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class StaffRosterMember(BaseModel):
    staff_id: str
    name: str
    department: str
    designation: str
    phone: str
    shift: str
    status: str = "Active"


# -------------------------------------------------------------
# Laundry Order Schemas
# -------------------------------------------------------------
class LaundryOrderCreate(BaseModel):
    reference_number: str
    room_number: str
    guest_name: str
    service_type: str = "Normal"
    items_detail: Optional[str] = None
    total_pieces: int = 1
    rate_amount: float
    express_surcharge: float = 0.0
    tax_amount: float = 0.0
    total_amount: float
    order_status: str = "Received"
    billing_status: str = "Billed to Room"
    received_date: str
    expected_delivery: Optional[str] = None
    attendant: str = "Sunil Mohapatra"

class LaundryOrderStatusUpdate(BaseModel):
    order_status: str # 'Received', 'In-Process', 'Ready', 'Delivered'
    delivered_at: Optional[datetime] = None

class LaundryOrderResponse(LaundryOrderCreate):
    id: int
    delivered_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

