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
    room_number: Optional[str] = None
    cost_center: Optional[str] = None
    auth_officer: Optional[str] = None
    reason: Optional[str] = None
    is_management_nc: bool = False
    month: Optional[str] = None

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


# -------------------------------------------------------------
# IDS FortuneNext PMS Schemas (67 Modals Backend Support)
# -------------------------------------------------------------

# 1. Folio Transactions
class FolioTransactionCreate(BaseModel):
    room_number: str
    folio_number: int = 1
    guest_name: str
    transaction_type: str # 'Room Charge', 'POS F&B', 'Laundry', 'Advance Deposit', 'Allowance', 'Paid Out'
    voucher_or_bill_no: Optional[str] = None
    particulars: str
    sac_code: str = "996311"
    debit_amount: float = 0.0
    credit_amount: float = 0.0
    tax_amount: float = 0.0
    posting_date: str
    posted_by: str = "MANAGER"

class FolioTransactionResponse(FolioTransactionCreate):
    id: int
    is_settled: bool
    created_at: datetime

    class Config:
        from_attributes = True

class FolioSummaryResponse(BaseModel):
    room_number: str
    folio_number: int
    guest_name: str
    total_debit: float
    total_credit: float
    net_balance: float
    transactions: List[FolioTransactionResponse]

# 2. Advance Deposits
class AdvanceDepositCreate(BaseModel):
    receipt_number: str
    room_number: str
    guest_name: str
    amount: float
    payment_mode: str = "Cash"
    reference_no: Optional[str] = None
    remarks: str = "Room Advance Deposit"
    status: str = "Active"
    date: str

class AdvanceDepositResponse(AdvanceDepositCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 3. Paid-Out Cash Vouchers
class PaidOutVoucherCreate(BaseModel):
    voucher_number: str
    room_number: str
    guest_name: str
    paid_amount: float
    purpose: str
    authorized_by: str = "Duty Manager"
    date: str

class PaidOutVoucherResponse(PaidOutVoucherCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 4. Foreign Exchange Encashment
class ForexEncashmentCreate(BaseModel):
    encashment_no: str
    room_number: str
    guest_name: str
    passport_number: str
    nationality: str = "USA"
    currency_code: str
    foreign_amount: float
    exchange_rate: float
    inr_value: float
    gst_amount: float = 0.0
    net_payable: float
    date: str

class ForexEncashmentResponse(ForexEncashmentCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# 5. Lost & Found Items
class LostAndFoundItemCreate(BaseModel):
    tracking_no: str
    item_description: str
    room_number: Optional[str] = None
    found_location: str = "Room"
    found_by: str = "Housekeeping Attendant"
    found_date: str
    status: str = "Found/Stored"

class LostAndFoundItemClaim(BaseModel):
    claimed_by: str
    claim_date: str

class LostAndFoundItemResponse(LostAndFoundItemCreate):
    id: int
    claimed_by: Optional[str] = None
    claim_date: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# 6. Room Transfer Logs & Stay Amendments
class RoomTransferLogCreate(BaseModel):
    guest_name: str
    from_room: str
    to_room: str
    reason: str = "Guest Preference / Maintenance Move"
    authorized_by: str = "Front Office Duty Manager"
    transfer_date: str

class RoomTransferLogResponse(RoomTransferLogCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class StayAmendRequest(BaseModel):
    room_number: str
    new_departure_date: str
    reason: str = "Extended Stay on Guest Request"
    revised_rate: Optional[float] = None

# 7. Corporate Contract Rates
class CorporateRateLinkCreate(BaseModel):
    company_code: str
    company_name: str
    rate_table_no: str
    description: str
    valid_from: str
    valid_to: str
    status: str = "Active"

class CorporateRateLinkResponse(CorporateRateLinkCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 8. Monthly Sales Reports Schemas (June Month Audited Data)
class HotelSaleRecordCreate(BaseModel):
    serial_no: int
    date: str
    bill_no: str
    room_number: str
    rent: float = 0.0
    cgst: float = 0.0
    sgst: float = 0.0
    misc: float = 0.0
    laundry: float = 0.0
    minibar: float = 0.0
    room_service: float = 0.0
    net_amount: float = 0.0
    advance: float = 0.0
    discount: float = 0.0
    complimentary: float = 0.0
    void_amount: float = 0.0
    allowances: float = 0.0
    paid_out: float = 0.0
    cash: float = 0.0
    btc: float = 0.0
    credit_card: float = 0.0
    online: float = 0.0
    remark: Optional[str] = ""
    guest_name: Optional[str] = ""
    company: Optional[str] = "FIT"
    gstin: Optional[str] = None
    month: str = "JUNE-2026"

class HotelSaleRecordResponse(HotelSaleRecordCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class RestaurantSaleRecordCreate(BaseModel):
    running_no: int
    date: str
    bill_no: str
    amount: float = 0.0
    food: float = 0.0
    beverage: float = 0.0
    cgst: float = 0.0
    sgst: float = 0.0
    discount: float = 0.0
    total: float = 0.0
    pos_outlet: str = "RESTAURANT"
    table_room: str = ""
    cost_center: Optional[str] = ""
    auth_officer: Optional[str] = ""
    reason: Optional[str] = ""
    settlement_mode: Optional[str] = "Cash"
    is_management_nc: bool = False
    month: str = "JUNE-2026"

class RestaurantSaleRecordResponse(RestaurantSaleRecordCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Gstr3bStatutorySummaryResponse(BaseModel):
    month: str
    property_name: str
    gstin: str
    state_code: str
    room_taxable_turnover: float
    room_cgst: float
    room_sgst: float
    room_service_in_hotel: float
    fnb_taxable_turnover: float
    fnb_cgst: float
    fnb_sgst: float
    fnb_gross_production: float
    management_nc_valuation: float
    total_taxable_outward_supplies: float
    total_central_tax_cgst: float
    total_state_tax_sgst: float
    total_tax_liability: float
    grand_consolidated_turnover: float
    hotel_bills_count: int
    restaurant_orders_count: int
    nc_orders_count: int


class StorePurchaseCreate(BaseModel):
    purchase_id: Optional[str] = None
    vendor_name: str
    invoice_no: Optional[str] = None
    purchase_date: Optional[str] = None
    category: str = "Groceries"
    items_summary: Optional[str] = None
    total_amount: float = 0.0
    payment_status: str = "Cash Paid"
    received_by: str = "STORE INCHARGE"


class StorePurchaseResponse(BaseModel):
    id: int
    purchase_id: str
    vendor_name: str
    invoice_no: Optional[str] = None
    purchase_date: str
    category: str
    items_summary: Optional[str] = None
    total_amount: float
    payment_status: str
    received_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class KitchenRequisitionCreate(BaseModel):
    requisition_id: Optional[str] = None
    issue_date: Optional[str] = None
    target_outlet: str = "Main Kitchen"
    item_name: str
    quantity_issued: float = 0.0
    unit: str = "KG"
    approx_cost: float = 0.0
    issued_to: str = "HEAD CHEF"
    issued_by: str = "STORE KEEPER"


class KitchenRequisitionResponse(BaseModel):
    id: int
    requisition_id: str
    issue_date: str
    target_outlet: str
    item_name: str
    quantity_issued: float
    unit: str
    approx_cost: float
    issued_to: str
    issued_by: str
    created_at: datetime

    class Config:
        from_attributes = True


class VendorPayableCreate(BaseModel):
    vendor_name: str
    category: str = "General Supplier"
    contact: Optional[str] = None
    supplies_amount: float = 0.0
    paid_amount: float = 0.0


class VendorPayableResponse(BaseModel):
    id: int
    vendor_name: str
    category: str
    contact: Optional[str] = None
    supplies_amount: float
    paid_amount: float
    outstanding: float = 0.0
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================
# Category 1: Front Office PMS & Guest Management Schemas
# =============================================================
class PoliceManifestCreate(BaseModel):
    room_no: str
    name: str
    mobile: str
    age: int = 30
    gender: str = "Male"
    id_proof_type: str = "Aadhaar Card"
    id_proof_no: str
    address: str
    arrived_from: str = "Rayagada"
    destination: str = "Muniguda"
    purpose: str = "Business Visit"
    vehicle_no: Optional[str] = None
    check_in_time: str
    expected_check_out: Optional[str] = None
    status: str = "In-House"
    guest_type: str = "Corporate"

class PoliceManifestResponse(PoliceManifestCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class ForeignerFormCCreate(BaseModel):
    form_c_no: Optional[str] = None
    room_no: str
    guest_name: str
    passport_no: str
    visa_no: str
    nationality: str = "Foreign"
    arrival_date: str
    departure_date: Optional[str] = None
    purpose_of_visit: str = "Technical Consultant"
    indian_ref_contact: Optional[str] = None

class ForeignerFormCResponse(ForeignerFormCCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class GuestKycDocumentCreate(BaseModel):
    room_number: str
    guest_name: str
    doc_type: str = "Aadhaar Card"
    doc_number_masked: str
    id_file_url: Optional[str] = None
    verified_by: str = "FRONT DESK"

class GuestKycDocumentResponse(GuestKycDocumentCreate):
    id: int
    verified_at: datetime
    class Config:
        from_attributes = True

class CashierShiftOpenRequest(BaseModel):
    shift_id: str
    shift_name: str
    cashier_name: str
    cashier_code: str
    accounting_date: str
    drawer_float: float = 2000.0

class CashierShiftCloseRequest(BaseModel):
    safe_drop: float = 0.0
    denominations: Optional[dict] = None
    physical_cash: float = 2000.0
    collections: Optional[dict] = None
    fnb_split: Optional[dict] = None
    handover_notes: Optional[str] = ""
    manager_pin: str = "7650"

class CashierShiftResponse(BaseModel):
    id: int
    shift_id: str
    shift_name: str
    cashier_name: str
    cashier_code: str
    accounting_date: str
    status: str
    drawer_float: float
    safe_drop: float
    denominations_json: str
    physical_cash: float
    collections_json: str
    fnb_split_json: str
    handover_notes: str
    closed_at: Optional[datetime] = None
    created_at: datetime
    class Config:
        from_attributes = True

# =============================================================
# Category 2: Folio Accounting & Adjustments Schemas
# =============================================================
class FolioChargeTransferRequest(BaseModel):
    from_room: str
    to_room: str
    from_folio: int = 1
    to_folio: int = 1
    amount: float
    charge_type: str = "Room Charge"
    reason: str = "Guest Request / Combined Billing"
    authorized_by: str = "Duty Manager"
    manager_pin: str = "4321"

class BillAllowanceCreate(BaseModel):
    room_number: str
    folio_number: int = 1
    bill_no: Optional[str] = None
    allowance_amount: float
    tax_reversed: float = 0.0
    reason: str
    approved_by: str = "GENERAL MANAGER"
    date: str
    manager_pin: str = "4321"

class CorporateSplitBillingRequest(BaseModel):
    room_number: str
    corporate_id: Optional[int] = None
    company_name: str
    btc_amount: float
    personal_amount: float
    billing_date: str

class RoomBlockCreate(BaseModel):
    room_number: str
    block_type: str = "Maintenance"
    reason: str
    start_date: str
    end_date: str
    blocked_by: str = "MAINTENANCE ENGINEER"

class RoomBlockResponse(RoomBlockCreate):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

# =============================================================
# Category 3: POS, F&B & Banquet Schemas
# =============================================================
class SplitTenderPaymentItem(BaseModel):
    mode: str
    amount: float
    details: Optional[str] = None

class SplitTenderRequest(BaseModel):
    payments: List[SplitTenderPaymentItem]
    manager_pin: str = "4321"
    month: Optional[str] = "OCTOBER-2026"

class PosDiscountApplyRequest(BaseModel):
    discount_amount: float
    discount_percentage: Optional[float] = 0.0
    reason: str = "Manager Courtesy Discount"
    manager_pin: str = "4321"

class TenderReclassifyRequest(BaseModel):
    old_mode: str
    new_mode: str
    reason: str
    manager_pin: str = "4321"

class BanquetEventCreate(BaseModel):
    event_id: Optional[str] = None
    event_name: str
    host_name: str
    host_phone: str
    event_date: str
    slot: str = "Full Day"
    pax: int = 50
    hall_name: str = "Grand Ballroom / Conference Hall"
    hall_rental: float = 15000.0
    food_package_rate: float = 650.0
    menu_summary: str = "Buffet Lunch + Hi-Tea + Dinner"
    subtotal: float = 0.0
    gst_amount: float = 0.0
    total_amount: float = 0.0
    advance_paid: float = 0.0
    balance_due: float = 0.0
    status: str = "Confirmed"

class BanquetEventResponse(BanquetEventCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class PosServerCreate(BaseModel):
    server_code: str
    name: str
    role: str = "Steward"
    section: str = "Restaurant"
    active: bool = True

class PosServerResponse(PosServerCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class RestaurantTableCreate(BaseModel):
    table_number: str
    capacity: int = 4
    status: str = "available"

# =============================================================
# Category 4: Store, Materials & Inventory Schemas
# =============================================================
class PurchaseOrderCreate(BaseModel):
    po_number: Optional[str] = None
    vendor_name: str
    order_date: str
    expected_delivery: Optional[str] = None
    total_amount: float = 0.0
    items_detail: Optional[list] = []
    approved_by: str = "STORE MANAGER"

class PurchaseOrderResponse(BaseModel):
    id: int
    po_number: str
    vendor_name: str
    order_date: str
    expected_delivery: Optional[str] = None
    status: str
    total_amount: float
    items_detail_json: str
    approved_by: str
    created_at: datetime
    class Config:
        from_attributes = True

class GoodsReceiptNoteCreate(BaseModel):
    grn_number: Optional[str] = None
    po_number: Optional[str] = None
    vendor_name: str
    challan_no: Optional[str] = None
    invoice_no: Optional[str] = None
    received_date: str
    total_val: float = 0.0
    verified_by: str = "STORE INCHARGE"
    items_received: Optional[list] = []

class GoodsReceiptNoteResponse(BaseModel):
    id: int
    grn_number: str
    po_number: Optional[str] = None
    vendor_name: str
    challan_no: Optional[str] = None
    invoice_no: Optional[str] = None
    received_date: str
    total_val: float
    verified_by: str
    items_received_json: str
    created_at: datetime
    class Config:
        from_attributes = True

class StoreIssueVoucherCreate(BaseModel):
    voucher_no: Optional[str] = None
    department: str
    target_outlet: str = "Main Kitchen"
    item_name: str
    quantity: float
    unit: str = "KG"
    cost: float = 0.0
    issued_by: str = "STORE KEEPER"
    received_by: str = "HEAD CHEF"
    issue_date: str

class StoreIssueVoucherResponse(BaseModel):
    id: int
    voucher_no: str
    department: str
    target_outlet: str
    item_name: str
    quantity: float
    unit: str
    cost: float
    issued_by: str
    received_by: str
    issue_date: str
    created_at: datetime
    class Config:
        from_attributes = True

# =============================================================
# Category 5: Housekeeping, Linen & Asset Schemas
# =============================================================
class LinenInventoryCreate(BaseModel):
    item_name: str
    category: str = "Bed Linen"
    total_stock: int = 100
    in_use: int = 54
    in_laundry: int = 20
    discard_count: int = 0
    unit_cost: float = 450.0
    par_stock: int = 120

class LinenInventoryResponse(LinenInventoryCreate):
    id: int
    last_audited: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True

class RoomAmenityTrackerResponse(BaseModel):
    id: int
    item_name: str
    par_stock: int
    current_stock: int
    unit: str
    daily_consumption: int
    last_updated: datetime
    class Config:
        from_attributes = True

class HousekeepingInspectionCreate(BaseModel):
    room_number: str
    inspector: str = "HK Executive"
    inspection_date: str
    score: float = 100.0
    remarks: str = "Sanitized & ready"
    checklist: Optional[dict] = {}

class HousekeepingInspectionResponse(BaseModel):
    id: int
    room_number: str
    inspector: str
    inspection_date: str
    score: float
    remarks: str
    checklist_json: str
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

# =============================================================
# Category 7: Corporate BTC, Aging, TDS & Bank Recon Schemas
# =============================================================
class BankReconciliationCreate(BaseModel):
    statement_date: str
    bank_name: str = "State Bank of India (SBI) - Muniguda Branch"
    account_number: str = "38910294812"
    statement_balance: float
    book_balance: float
    uncredited_cheques: float = 0.0
    unpresented_cheques: float = 0.0
    reconciled_balance: float = 0.0
    reconciled_by: str = "CHIEF ACCOUNTANT"

class BankReconciliationResponse(BaseModel):
    id: int
    statement_date: str
    bank_name: str
    account_number: str
    statement_balance: float
    book_balance: float
    uncredited_cheques: float
    unpresented_cheques: float
    reconciled_balance: float
    difference: float
    status: str
    reconciled_by: str
    created_at: datetime
    class Config:
        from_attributes = True

class TdsTcsRecordCreate(BaseModel):
    invoice_no: str
    corporate_name: str
    gstin: Optional[str] = None
    tan_no: Optional[str] = None
    section: str = "194C"
    gross_amount: float
    tds_rate: float = 2.0
    financial_year: str = "2026-27"
    quarter: str = "Q3"

class TdsTcsRecordResponse(BaseModel):
    id: int
    invoice_no: str
    corporate_name: str
    gstin: Optional[str] = None
    tan_no: Optional[str] = None
    section: str
    gross_amount: float
    tds_rate: float
    tds_amount: float
    net_receivable: float
    financial_year: str
    quarter: str
    created_at: datetime
    class Config:
        from_attributes = True

# Tables & Menu Management
class TableCreate(BaseModel):
    table_number: str
    capacity: int = 4
    status: str = "available"

class TableUpdate(BaseModel):
    table_number: Optional[str] = None
    capacity: Optional[int] = None
    status: Optional[str] = None

class MenuItemCreate(BaseModel):
    item_code: str
    name: str
    category: str
    price: float
    is_veg: bool = True
    description: Optional[str] = None

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    is_veg: Optional[bool] = None
    description: Optional[str] = None

# Railway Transit Slot Schemas
class TransitSlotCreate(BaseModel):
    room_number: str
    guest_name: str
    mobile: str
    age: int = 30
    train_number: str
    pnr_number: Optional[str] = None
    destination: Optional[str] = None
    rate_bracket: float = 500.0
    check_in_time: str
    expected_check_out: str
    status: str = "Occupied"

class TransitSlotResponse(TransitSlotCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Sales Promotion Schemas
class SalesPromotionCreate(BaseModel):
    promo_code: str
    description: str
    discount_percentage: float = 0.0
    flat_discount_amount: float = 0.0
    applicable_outlet: str = "ALL"
    min_order_amount: float = 0.0
    valid_from: str
    valid_to: str
    is_active: bool = True

class SalesPromotionResponse(SalesPromotionCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

# Corporate Account Master Schemas
class CorporateAccountCreate(BaseModel):
    company_name: str
    gst_number: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    credit_limit: float = 100000.0

class CorporateAccountUpdate(BaseModel):
    company_name: Optional[str] = None
    gst_number: Optional[str] = None
    contact_person: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    credit_limit: Optional[float] = None



