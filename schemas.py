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
