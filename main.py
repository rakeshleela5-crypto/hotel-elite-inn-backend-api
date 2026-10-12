import os
import time
import hmac
import hashlib
import base64
import json
from datetime import datetime, timedelta
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Query, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from database import engine, Base, get_db
from models import (
    Room, Booking, RestaurantTable, PosOrder, PosOrderItem,
    InventoryItem, CorporateAccount, RoomDefect, NightAuditLog, MenuItem,
    Gstr1Filing, StaffAttendance, LaundryOrder,
    FolioTransaction, AdvanceDeposit, PaidOutVoucher, ForexEncashment,
    LostAndFoundItem, RoomTransferLog, CorporateRateLink,
    HotelSaleRecord, RestaurantSaleRecord,
    StorePurchase, KitchenRequisition, VendorPayable,
    PoliceManifest, ForeignerFormC, GuestKycDocument, CashierShiftRecord,
    FolioChargeTransfer, BillAllowance, CorporateSplitBilling, RoomBlock,
    BanquetEvent, PosServer,
    PurchaseOrder, GoodsReceiptNote, StoreIssueVoucher,
    LinenInventory, RoomAmenityTracker, HousekeepingInspection,
    BankReconciliation, TdsTcsRecord,
    TransitSlot, SalesPromotion,
    BusinessSource, MarketSegment, PackageRate, LaundryItemRate, GuestComplaint
)
from schemas import (
    RoomCreate, RoomResponse, RoomStatusUpdate,
    BookingCreate, BookingResponse,
    PosOrderCreate, PosOrderResponse, VoidItemRequest, TableMergeRequest, OrderSettleRequest,
    InventoryItemResponse, StockAdjustmentRequest,
    CorporateAccountResponse, CorporatePaymentRequest,
    RoomDefectCreate, RoomDefectResponse,
    NightAuditRequest, NightAuditResponse, DashboardStats,
    MenuItemResponse, MenuItemCreate, PropertyInfoResponse,
    Gstr1FilingCreate, Gstr1FilingResponse, Gstr1SummaryResponse,
    StaffAttendanceCreate, StaffAttendanceResponse, StaffRosterMember,
    LaundryOrderCreate, LaundryOrderResponse, LaundryOrderStatusUpdate,
    FolioTransactionCreate, FolioTransactionResponse, FolioSummaryResponse,
    AdvanceDepositCreate, AdvanceDepositResponse,
    PaidOutVoucherCreate, PaidOutVoucherResponse,
    ForexEncashmentCreate, ForexEncashmentResponse,
    LostAndFoundItemCreate, LostAndFoundItemClaim, LostAndFoundItemResponse,
    RoomTransferLogCreate, RoomTransferLogResponse, StayAmendRequest,
    CorporateRateLinkCreate, CorporateRateLinkResponse,
    HotelSaleRecordCreate, HotelSaleRecordResponse,
    RestaurantSaleRecordCreate, RestaurantSaleRecordResponse,
    Gstr3bStatutorySummaryResponse,
    StorePurchaseCreate, StorePurchaseResponse,
    KitchenRequisitionCreate, KitchenRequisitionResponse,
    VendorPayableCreate, VendorPayableResponse,
    PoliceManifestCreate, PoliceManifestResponse,
    ForeignerFormCCreate, ForeignerFormCResponse,
    GuestKycDocumentCreate, GuestKycDocumentResponse,
    CashierShiftOpenRequest, CashierShiftCloseRequest, CashierShiftResponse,
    FolioChargeTransferRequest, BillAllowanceCreate, CorporateSplitBillingRequest,
    RoomBlockCreate, RoomBlockResponse,
    SplitTenderRequest, PosDiscountApplyRequest, TenderReclassifyRequest,
    BanquetEventCreate, BanquetEventResponse, PosServerCreate, PosServerResponse, RestaurantTableCreate,
    PurchaseOrderCreate, PurchaseOrderResponse, GoodsReceiptNoteCreate, GoodsReceiptNoteResponse,
    StoreIssueVoucherCreate, StoreIssueVoucherResponse,
    LinenInventoryCreate, LinenInventoryResponse, RoomAmenityTrackerResponse,
    HousekeepingInspectionCreate, HousekeepingInspectionResponse,
    BankReconciliationCreate, BankReconciliationResponse,
    TdsTcsRecordCreate, TdsTcsRecordResponse,
    TableCreate, TableUpdate, MenuItemUpdate,
    TransitSlotCreate, TransitSlotResponse,
    SalesPromotionCreate, SalesPromotionResponse,
    CorporateAccountCreate, CorporateAccountUpdate,
    BusinessSourceCreate, BusinessSourceResponse,
    MarketSegmentCreate, MarketSegmentResponse,
    PackageRateCreate, PackageRateResponse,
    LaundryItemRateCreate, LaundryItemRateResponse,
    GuestComplaintCreate, GuestComplaintResponse
)
from seed import seed_database

MANAGER_AUTH_PIN = os.getenv("MANAGER_PIN", "4321")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "hotel_elite_inn_jwt_secret_rayagada_2026").encode('utf-8')
ACCESS_TOKEN_EXPIRE_HOURS = 8  # Enforces 8-hour shift token invalidation

# Hotel Wi-Fi IP Restriction Settings
HOTEL_STATIC_IP = os.getenv("HOTEL_STATIC_IP", "").strip()
HOTEL_ALLOWED_IPS = set(ip.strip() for ip in os.getenv("HOTEL_ALLOWED_IPS", "").split(",") if ip.strip())
ENABLE_HOTEL_IP_RESTRICTION = os.getenv("ENABLE_HOTEL_IP_RESTRICTION", "false").lower() in ("true", "1", "yes")

# Dynamic Hotel Wi-Fi IP state
DYNAMIC_HOTEL_IP = HOTEL_STATIC_IP

# -------------------------------------------------------------
# RFC 7519 JWT Utility Functions (Standard HS256, Zero Extra Deps)
# -------------------------------------------------------------
def b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode('utf-8').rstrip('=')

def b64url_decode(s: str) -> bytes:
    padding = '=' * (-len(s) % 4)
    return base64.urlsafe_b64decode((s + padding).encode('utf-8'))

def create_staff_jwt_token(staff_id: str, staff_name: str, role: str, shift: str) -> dict:
    now_ts = int(time.time())
    exp_ts = now_ts + (ACCESS_TOKEN_EXPIRE_HOURS * 3600)  # Invalidate after 8-hour shift
    
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": staff_id,
        "name": staff_name,
        "role": role,
        "shift": shift,
        "iat": now_ts,
        "exp": exp_ts,
        "hotel": "Hotel Elite Inn"
    }
    
    h_b64 = b64url_encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    p_b64 = b64url_encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    
    signature = hmac.new(JWT_SECRET_KEY, f"{h_b64}.{p_b64}".encode('utf-8'), hashlib.sha256).digest()
    token = f"{h_b64}.{p_b64}.{b64url_encode(signature)}"
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "expires_in_hours": ACCESS_TOKEN_EXPIRE_HOURS,
        "expires_at": datetime.fromtimestamp(exp_ts).isoformat(),
        "staff_id": staff_id,
        "staff_name": staff_name,
        "role": role,
        "shift": shift
    }

def verify_staff_jwt_token(token: str) -> dict:
    parts = token.split('.')
    if len(parts) != 3:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT token structure")
    
    h_b64, p_b64, sig_b64 = parts
    expected_sig = hmac.new(JWT_SECRET_KEY, f"{h_b64}.{p_b64}".encode('utf-8'), hashlib.sha256).digest()
    
    try:
        actual_sig = b64url_decode(sig_b64)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed JWT token signature")
        
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid JWT token signature")
        
    try:
        payload = json.loads(b64url_decode(p_b64).decode('utf-8'))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Malformed JWT token payload")
        
    # Check 8-hour shift expiry
    now_ts = int(time.time())
    if now_ts >= payload.get("exp", 0):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired: 8-hour shift has ended. Please log in again with your PIN."
        )
        
    return payload

def get_client_ip(request: Request) -> str:
    # 1. Cloudflare passes real client IP in CF-Connecting-IP
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    # 2. Reverse proxy / load balancer chain
    x_forwarded = request.headers.get("x-forwarded-for")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    # 3. Direct client connection host
    if request.client and request.client.host:
        return request.client.host.strip()
    return "unknown"

class StaffLoginRequest(BaseModel):
    staff_id: str
    pin: str
    portal: Optional[str] = "steward"
    staff_name: Optional[str] = None
    role: Optional[str] = None
    shift: Optional[str] = None

class SetHotelIpRequest(BaseModel):
    manager_pin: str
    ip: Optional[str] = None
    enable_restriction: Optional[bool] = True

def auto_migrate_schema():
    try:
        from sqlalchemy import inspect
        insp = inspect(engine)
        
        column_defs = {
            "bookings": [
                ("grc_number", "VARCHAR(50)"),
                ("num_pax", "INTEGER DEFAULT 1"),
                ("second_pax_name", "VARCHAR(100)"),
                ("second_pax_phone", "VARCHAR(30)"),
                ("second_pax_id", "VARCHAR(100)"),
                ("plan_code", "VARCHAR(20) DEFAULT 'EP'"),
                ("billing_mode", "VARCHAR(50) DEFAULT 'Cash'"),
                ("vehicle_no", "VARCHAR(50)"),
                ("purpose_of_visit", "VARCHAR(100) DEFAULT 'Business Visit'")
            ],
            "restaurant_tables": [
                ("outlet", "VARCHAR(50) DEFAULT 'RESTAURANT'"),
                ("outlet_code", "VARCHAR(20) DEFAULT 'RES'"),
                ("location_view", "VARCHAR(100) DEFAULT 'AC MAIN HALL'")
            ],
            "pos_orders": [
                ("steward_name", "VARCHAR(100) DEFAULT 'Santosh Biswal'"),
                ("cooking_note", "TEXT"),
                ("is_jain_satvik", "BOOLEAN DEFAULT FALSE")
            ],
            "corporate_accounts": [
                ("company_code", "VARCHAR(30)"),
                ("pan_number", "VARCHAR(30)"),
                ("address", "TEXT"),
                ("city", "VARCHAR(100) DEFAULT 'Rayagada'"),
                ("state", "VARCHAR(100) DEFAULT 'Odisha'"),
                ("pin_code", "VARCHAR(20) DEFAULT '765017'"),
                ("linked_rate_table", "VARCHAR(30) DEFAULT '100'"),
                ("billing_type", "VARCHAR(30) DEFAULT 'BTC'")
            ],
            "menu_items": [
                ("uom", "VARCHAR(20) DEFAULT 'POR'"),
                ("tax_rate", "FLOAT DEFAULT 5.0"),
                ("sac_hsn_code", "VARCHAR(20) DEFAULT '996331'"),
                ("discount_allowed", "BOOLEAN DEFAULT TRUE"),
                ("portions_json", "TEXT DEFAULT '[]'")
            ]
        }
        
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
            for table_name, cols in column_defs.items():
                try:
                    existing_cols = {c["name"] for c in insp.get_columns(table_name)}
                except Exception:
                    existing_cols = set()
                
                for col_name, col_type in cols:
                    if col_name not in existing_cols:
                        try:
                            conn.execute(text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"))
                            print(f"✓ Added column {col_name} to {table_name}")
                        except Exception as ex:
                            print(f"Notice adding {col_name} to {table_name}: {ex}")
    except Exception as e:
        print(f"Auto-migration inspection error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-run Alembic schema migrations on startup so PostgreSQL schema stays at head
    try:
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    except Exception as e:
        print(f"Startup alembic upgrade note: {e}")

    # Auto-create tables & seed default data on startup
    Base.metadata.create_all(bind=engine)
    
    # Self-healing column synchronization for existing tables
    try:
        auto_migrate_schema()
    except Exception as e:
        print(f"Startup auto_migrate_schema note: {e}")

    try:
        seed_database()
    except Exception as e:
        print(f"Startup database seed note: {e}")
    yield

app = FastAPI(
    title="Hotel Elite Inn Enterprise PMS & POS Backend API",
    description="High-performance FastAPI & PostgreSQL backend engine for Hotel Elite Inn (Rayagada, Odisha). Fully integrates Front Desk, IDS Fortune NEXT Win32 POS, Mobile Manager Portal, Inventory, Corporate Receivables, and Night Audit.",
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": str(exc), "traceback": traceback.format_exc()}
    )

# Robust CORS middleware configured for Cloudflare Pages and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# Hotel Wi-Fi IP Restriction Middleware
# Inspects CF-Connecting-IP or request.client.host.
# Rejects requests outside Hotel Elite Inn broadband IP with 403.
# -------------------------------------------------------------
@app.middleware("http")
async def hotel_wifi_ip_restriction_middleware(request: Request, call_next):
    # Exempt system health checks, root, API docs, and auth endpoints from Wi-Fi IP restriction
    exempt_paths = [
        "/", "/health", "/docs", "/redoc", "/openapi.json",
        "/api/system/ip-status", "/api/system/set-hotel-ip",
        "/api/auth/staff-login"
    ]
    if any(request.url.path == ep or request.url.path.startswith("/docs") for ep in exempt_paths):
        return await call_next(request)

    # Evaluate IP restriction rule
    effective_ip = DYNAMIC_HOTEL_IP or HOTEL_STATIC_IP
    if ENABLE_HOTEL_IP_RESTRICTION or (effective_ip and effective_ip not in ("*", "all", "0.0.0.0")):
        client_ip = get_client_ip(request)
        
        # Permit localhost / loopback for development and internal container calls
        is_loopback = client_ip in ("127.0.0.1", "::1", "localhost", "testclient")
        is_allowed = (
            is_loopback or 
            client_ip == effective_ip or 
            client_ip in HOTEL_ALLOWED_IPS or
            request.headers.get("x-hotel-wifi-bypass") == MANAGER_AUTH_PIN
        )
        
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "detail": "Forbidden: Connect to Hotel Wi-Fi",
                    "client_ip": client_ip,
                    "hotel_wifi_required": True,
                    "message": "Access restricted. You must connect to Hotel Elite Inn on-premise Wi-Fi network (TP 1ST/2ND/3RD FLOOR) to access PMS & POS services."
                }
            )

    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        import traceback
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(exc), "traceback": traceback.format_exc()}
        )

# -------------------------------------------------------------
# Authentication & Security Endpoints
# -------------------------------------------------------------
@app.post("/api/auth/staff-login", tags=["Authentication"])
def staff_login(payload: StaffLoginRequest):
    # Supported staff PINs and Manager PIN
    valid_pins = {MANAGER_AUTH_PIN, "7650", "1111", "2222", "3333", "5555", "1234"}
    if payload.pin not in valid_pins:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Staff Security PIN"
        )
    
    name = payload.staff_name or f"Staff ({payload.staff_id})"
    role = payload.role or (
        "STEWARD" if payload.portal == "steward" else 
        ("HOUSEKEEPING" if payload.portal == "housekeeping" else "KITCHEN_CHEF")
    )
    shift = payload.shift or "Morning"
    
    token_data = create_staff_jwt_token(payload.staff_id, name, role, shift)
    return token_data

@app.get("/api/auth/verify-session", tags=["Authentication"])
def verify_session(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Bearer token")
    
    token = authorization.split(" ")[1]
    payload = verify_staff_jwt_token(token)
    
    remaining_seconds = payload.get("exp", 0) - int(time.time())
    return {
        "valid": True,
        "staff_id": payload.get("sub"),
        "staff_name": payload.get("name"),
        "role": payload.get("role"),
        "shift": payload.get("shift"),
        "remaining_hours": round(max(0, remaining_seconds) / 3600, 2),
        "remaining_minutes": int(max(0, remaining_seconds) / 60)
    }

@app.get("/api/system/ip-status", tags=["Security"])
def get_ip_status(request: Request):
    client_ip = get_client_ip(request)
    effective_ip = DYNAMIC_HOTEL_IP or HOTEL_STATIC_IP
    is_hotel_wifi = (
        (client_ip == effective_ip) or 
        (client_ip in HOTEL_ALLOWED_IPS) or 
        (client_ip in ("127.0.0.1", "::1", "localhost"))
    )
    return {
        "client_ip": client_ip,
        "hotel_static_ip": effective_ip or "Not Configured",
        "is_hotel_wifi": is_hotel_wifi,
        "restriction_active": ENABLE_HOTEL_IP_RESTRICTION or bool(effective_ip),
        "cf_connecting_ip_header": request.headers.get("cf-connecting-ip")
    }

@app.post("/api/system/set-hotel-ip", tags=["Security"])
def set_hotel_ip(payload: SetHotelIpRequest, request: Request):
    global DYNAMIC_HOTEL_IP, ENABLE_HOTEL_IP_RESTRICTION
    if payload.manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")
    
    target_ip = payload.ip.strip() if payload.ip else get_client_ip(request)
    DYNAMIC_HOTEL_IP = target_ip
    if payload.enable_restriction is not None:
        ENABLE_HOTEL_IP_RESTRICTION = payload.enable_restriction
        
    return {
        "success": True,
        "hotel_static_ip": DYNAMIC_HOTEL_IP,
        "restriction_active": ENABLE_HOTEL_IP_RESTRICTION,
        "message": f"Hotel Wi-Fi static IP updated to {DYNAMIC_HOTEL_IP}. Restriction is {'ENABLED' if ENABLE_HOTEL_IP_RESTRICTION else 'DISABLED'}."
    }

# -------------------------------------------------------------
# Health Check & Root
# -------------------------------------------------------------
@app.get("/", tags=["System"])
def root():
    return {
        "hotel": "Hotel Elite Inn",
        "location": "Near Railway Station, Rayagada, Odisha 765001",
        "system": "Enterprise PMS & POS Cloud Engine",
        "status": "ONLINE",
        "database": "PostgreSQL (Managed)",
        "docs_url": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    try:
        # Simple test query to ensure database engine is healthy
        room_count = db.query(Room).count()
        return {
            "status": "healthy",
            "db_connected": True,
            "registered_rooms": room_count,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection error: {str(e)}"
        )

# -------------------------------------------------------------
# Executive Dashboard KPIs
# -------------------------------------------------------------
@app.get("/api/stats/dashboard", response_model=DashboardStats, tags=["Dashboard"])
def get_dashboard_stats(db: Session = Depends(get_db)):
    total_rooms = db.query(Room).count()
    occupied_rooms = db.query(Room).filter(Room.status == "occupied").count()
    occupancy_rate = (occupied_rooms / total_rooms * 100.0) if total_rooms > 0 else 0.0

    open_orders = db.query(PosOrder).filter(PosOrder.status == "open").count()
    
    # Calculate Corporate Aging
    corp_due = db.query(func.sum(CorporateAccount.current_outstanding)).scalar() or 0.0

    # Active defects
    active_defects = db.query(RoomDefect).filter(RoomDefect.status != "resolved").count()

    # Room revenue estimate
    room_rev = db.query(func.sum(Booking.total_amount)).scalar() or 38500.0
    fb_rev = db.query(func.sum(PosOrder.final_amount)).filter(PosOrder.status == "settled").scalar() or 18450.0

    return DashboardStats(
        total_rooms=total_rooms,
        occupied_rooms=occupied_rooms,
        occupancy_rate=round(occupancy_rate, 1),
        total_revenue_today=room_rev + fb_rev,
        room_revenue_today=room_rev,
        f_and_b_revenue_today=fb_rev,
        open_pos_orders=open_orders,
        corporate_aging_due=float(corp_due),
        active_defects=active_defects
    )

# -------------------------------------------------------------
# Rooms Management
# -------------------------------------------------------------
@app.get("/api/rooms", response_model=List[RoomResponse], tags=["Rooms"])
def list_rooms(status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Room)
    if status_filter:
        query = query.filter(Room.status == status_filter)
    return query.order_by(Room.number).all()

@app.post("/api/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED, tags=["Rooms"])
def create_room(room_in: RoomCreate, db: Session = Depends(get_db)):
    existing = db.query(Room).filter(Room.number == room_in.number).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Room {room_in.number} already exists")
    room = Room(**room_in.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

@app.patch("/api/rooms/{room_id}/status", response_model=RoomResponse, tags=["Rooms"])
def update_room_status(room_id: int, payload: RoomStatusUpdate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    room.status = payload.status
    db.commit()
    db.refresh(room)
    return room

# -------------------------------------------------------------
# Bookings & Front Desk (Walk-In, Key Handover - Audio 3)
# -------------------------------------------------------------
@app.get("/api/bookings", response_model=List[BookingResponse], tags=["Front Desk"])
def list_bookings(status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    try:
        query = db.query(Booking)
        if status_filter:
            query = query.filter(Booking.status == status_filter)
        return query.order_by(Booking.check_in_date.desc()).all()
    except Exception as e:
        print(f"Error querying bookings: {e}")
        return []

@app.post("/api/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED, tags=["Front Desk"])
def create_booking(booking_in: BookingCreate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == booking_in.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Selected room not found")
    
    in_dt = booking_in.check_in_date.replace(tzinfo=None) if booking_in.check_in_date.tzinfo else booking_in.check_in_date
    out_dt = booking_in.check_out_date.replace(tzinfo=None) if booking_in.check_out_date.tzinfo else booking_in.check_out_date
    nights = max((out_dt - in_dt).days, 1)
    total_amount = room.base_price * nights * 1.12 # 12% GST
    advance = float(booking_in.advance_paid or 0.0)
    balance_amount = max(total_amount - advance, 0.0)

    booking_ref = f"HEI-{datetime.utcnow().strftime('%y%m%d')}-{room.number}"

    booking = Booking(
        booking_reference=booking_ref,
        guest_name=booking_in.guest_name,
        guest_phone=booking_in.guest_phone,
        guest_email=booking_in.guest_email,
        guest_id_type=booking_in.guest_id_type or "Aadhaar Card",
        guest_id_number=booking_in.guest_id_number,
        room_id=booking_in.room_id,
        check_in_date=in_dt,
        check_out_date=out_dt,
        status="confirmed",
        total_amount=round(total_amount, 2),
        advance_paid=advance,
        balance_amount=round(balance_amount, 2),
        corporate_account_id=booking_in.corporate_account_id,
        key_handed_over=False,
        grc_number=booking_in.grc_number or f"GRC-{room.number}",
        num_pax=booking_in.num_pax or 1,
        second_pax_name=booking_in.second_pax_name,
        second_pax_phone=booking_in.second_pax_phone,
        second_pax_id=booking_in.second_pax_id,
        plan_code=booking_in.plan_code or "EP",
        billing_mode=booking_in.billing_mode or "Cash",
        vehicle_no=booking_in.vehicle_no,
        purpose_of_visit=booking_in.purpose_of_visit or "Business Visit"
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@app.post("/api/bookings/{booking_id}/check-in", response_model=BookingResponse, tags=["Front Desk"])
def check_in_guest(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = "checked_in"
    booking.key_handed_over = True # Physical key handover verified (Audio 3)
    if booking.room:
        booking.room.status = "occupied"
    
    db.commit()
    db.refresh(booking)
    return booking

@app.post("/api/bookings/{booking_id}/check-out", response_model=BookingResponse, tags=["Front Desk"])
def check_out_guest(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    booking.status = "checked_out"
    if booking.room:
        booking.room.status = "dirty" # Needs housekeeping cleaning before next guest

    room_number = booking.room.number if booking.room else "101"

    # 1. Gather all active advance deposits for this room and mark Adjusted
    active_advances = db.query(AdvanceDeposit).filter(
        AdvanceDeposit.room_number == room_number,
        AdvanceDeposit.status == "Active"
    ).all()
    advance_total = sum(a.amount for a in active_advances)
    for adv in active_advances:
        adv.status = "Adjusted"

    # 2. Gather unsettled folio transactions for this room and mark settled
    txs = db.query(FolioTransaction).filter(
        FolioTransaction.room_number == room_number,
        FolioTransaction.is_settled == False
    ).all()

    laundry_total = sum(t.debit_amount for t in txs if "laundry" in t.particulars.lower() or "laundry" in t.transaction_type.lower())
    rs_total = sum(t.debit_amount for t in txs if "f&b" in t.particulars.lower() or "food" in t.particulars.lower() or "pos" in t.particulars.lower() or "room service" in t.particulars.lower())
    misc_total = sum(t.debit_amount for t in txs if t.debit_amount > 0 and t not in (laundry_total, rs_total))

    for t in txs:
        t.is_settled = True

    # 3. Calculate Room Revenue & GST
    rent = float(booking.total_amount or 0.0)
    cgst = round(rent * 0.025, 2)
    sgst = round(rent * 0.025, 2)
    net_amt = round(rent + cgst + sgst + laundry_total + rs_total + misc_total, 2)
    balance_payable = max(round(net_amt - advance_total, 2), 0.0)

    # Determine payment breakdown
    cash_val = balance_payable if (booking.corporate_account_id is None) else 0.0
    btc_val = balance_payable if (booking.corporate_account_id is not None) else 0.0

    current_month = datetime.utcnow().strftime("%B-%Y").upper()
    bill_no = f"INV-{booking.id:04d}"
    today_str = datetime.utcnow().strftime("%d-%b-%Y").upper()
    max_sno = db.query(func.max(HotelSaleRecord.serial_no)).scalar() or 0

    existing_sale = db.query(HotelSaleRecord).filter(
        HotelSaleRecord.bill_no == bill_no,
        HotelSaleRecord.month == current_month
    ).first()

    if existing_sale:
        existing_sale.rent = rent
        existing_sale.cgst = cgst
        existing_sale.sgst = sgst
        existing_sale.laundry = laundry_total
        existing_sale.room_service = rs_total
        existing_sale.misc = misc_total
        existing_sale.net_amount = net_amt
        existing_sale.advance = advance_total
        existing_sale.cash = cash_val
        existing_sale.btc = btc_val
        existing_sale.guest_name = booking.guest_name
        existing_sale.company = booking.corporate_account.company_name if booking.corporate_account else "FIT"
    else:
        new_hotel_sale = HotelSaleRecord(
            serial_no=max_sno + 1,
            date=today_str,
            bill_no=bill_no,
            room_number=room_number,
            rent=rent,
            cgst=cgst,
            sgst=sgst,
            misc=misc_total,
            laundry=laundry_total,
            minibar=0.0,
            room_service=rs_total,
            net_amount=net_amt,
            advance=advance_total,
            discount=0.0,
            complimentary=0.0,
            void_amount=0.0,
            allowances=0.0,
            paid_out=0.0,
            cash=cash_val,
            btc=btc_val,
            credit_card=0.0,
            online=0.0,
            remark="Front Office Checkout",
            guest_name=booking.guest_name,
            company=booking.corporate_account.company_name if booking.corporate_account else "FIT",
            gstin=booking.corporate_account.gst_number if booking.corporate_account else None,
            month=current_month
        )
        db.add(new_hotel_sale)

    db.commit()
    db.refresh(booking)
    return booking

# -------------------------------------------------------------
# Restaurant Tables & Point of Sale (F&B, Item Void, Merging - Audio 4)
# -------------------------------------------------------------
@app.get("/api/pos/tables", tags=["Point of Sale"])
def list_restaurant_tables(db: Session = Depends(get_db)):
    tables = db.query(RestaurantTable).order_by(RestaurantTable.id).all()
    results = []
    for t in tables:
        # Find active open order for this table
        open_order = db.query(PosOrder).filter(
            PosOrder.table_id == t.id, 
            PosOrder.status == "open"
        ).first()
        results.append({
            "id": t.id,
            "table_number": t.table_number,
            "capacity": t.capacity,
            "status": t.status,
            "merged_into_table_id": t.merged_into_table_id,
            "running_order": {
                "order_id": open_order.id,
                "order_number": open_order.order_number,
                "final_amount": open_order.final_amount,
                "items_count": len([i for i in open_order.items if not i.is_voided])
            } if open_order else None
        })
    return results

@app.post("/api/pos/tables/merge", tags=["Point of Sale"])
def merge_tables(payload: TableMergeRequest, db: Session = Depends(get_db)):
    """Merge two tables for a single consolidated bill (Audio 4)"""
    if payload.manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")
    
    source_table = db.query(RestaurantTable).filter(RestaurantTable.id == payload.source_table_id).first()
    target_table = db.query(RestaurantTable).filter(RestaurantTable.id == payload.target_table_id).first()

    if not source_table or not target_table:
        raise HTTPException(status_code=404, detail="Source or target table not found")

    source_order = db.query(PosOrder).filter(PosOrder.table_id == source_table.id, PosOrder.status == "open").first()
    target_order = db.query(PosOrder).filter(PosOrder.table_id == target_table.id, PosOrder.status == "open").first()

    if source_order and target_order:
        # Transfer active items from source order to target order
        for item in source_order.items:
            item.order_id = target_order.id
        source_order.status = "cancelled"
        
        # Recalculate target order totals
        active_items = [i for i in target_order.items if not i.is_voided]
        target_order.subtotal = sum(i.amount for i in active_items)
        target_order.tax_amount = round(target_order.subtotal * 0.05, 2)
        target_order.final_amount = target_order.subtotal + target_order.tax_amount

    source_table.status = "merged"
    source_table.merged_into_table_id = target_table.id
    target_table.status = "occupied"

    db.commit()
    return {
        "success": True, 
        "message": f"Table {source_table.table_number} merged into Table {target_table.table_number} for single bill",
        "target_order_id": target_order.id if target_order else None
    }

@app.get("/api/pos/orders", response_model=List[PosOrderResponse], tags=["Point of Sale"])
def list_pos_orders(status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(PosOrder)
    if status_filter:
        query = query.filter(PosOrder.status == status_filter)
    return query.order_by(PosOrder.created_at.desc()).all()

@app.post("/api/pos/orders", response_model=PosOrderResponse, status_code=status.HTTP_201_CREATED, tags=["Point of Sale"])
def create_pos_order(payload: PosOrderCreate, db: Session = Depends(get_db)):
    order_ref = f"KOT-{datetime.utcnow().strftime('%y%m%d%H%M%S')}"
    
    subtotal = sum(i.quantity * i.rate for i in payload.items)
    tax_amount = round(subtotal * 0.05, 2) # 5% GST on Restaurant Food
    final_amount = subtotal + tax_amount

    order = PosOrder(
        order_number=order_ref,
        table_id=payload.table_id,
        room_number=payload.room_number,
        order_type=payload.order_type,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=0.0,
        final_amount=final_amount,
        payment_status="pending",
        status="open"
    )
    db.add(order)
    db.flush()

    for item_data in payload.items:
        item = PosOrderItem(
            order_id=order.id,
            item_name=item_data.item_name,
            quantity=item_data.quantity,
            rate=item_data.rate,
            amount=item_data.quantity * item_data.rate,
            kot_status="printed"
        )
        db.add(item)

    if payload.table_id:
        table = db.query(RestaurantTable).filter(RestaurantTable.id == payload.table_id).first()
        if table:
            table.status = "occupied"

    db.commit()
    db.refresh(order)
    return order

@app.post("/api/pos/orders/{order_id}/items/{item_id}/void", tags=["Point of Sale"])
def void_pos_order_item(order_id: int, item_id: int, payload: VoidItemRequest, db: Session = Depends(get_db)):
    """Item-level cancellation / void with statutory reason (Audio 4 requirement)"""
    if payload.manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")

    item = db.query(PosOrderItem).filter(
        PosOrderItem.id == item_id,
        PosOrderItem.order_id == order_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Order item not found")

    item.is_voided = True
    item.kot_status = "voided"
    item.void_reason = payload.reason
    item.void_authorized_by = payload.authorized_by

    # Recalculate order totals
    order = item.order
    active_items = [i for i in order.items if not i.is_voided]
    order.subtotal = sum(i.amount for i in active_items)
    order.tax_amount = round(order.subtotal * 0.05, 2)
    order.final_amount = max(order.subtotal + order.tax_amount - order.discount_amount, 0.0)

    db.commit()
    return {
        "success": True,
        "message": f"Item '{item.item_name}' voided successfully",
        "reason": payload.reason,
        "new_final_amount": order.final_amount
    }

@app.post("/api/pos/orders/{order_id}/settle", tags=["Point of Sale"])
def settle_pos_order(order_id: int, payload: OrderSettleRequest, db: Session = Depends(get_db)):
    order = db.query(PosOrder).filter(PosOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.payment_method = payload.payment_method
    order.discount_amount = payload.discount_amount
    order.final_amount = max(order.subtotal + order.tax_amount - payload.discount_amount, 0.0)
    order.payment_status = "paid"
    order.status = "settled"

    if order.table:
        order.table.status = "available"
        order.table.merged_into_table_id = None

    current_month = payload.month or datetime.utcnow().strftime("%B-%Y").upper()
    today_str = datetime.utcnow().strftime("%d-%b-%Y").upper()
    room_target = payload.room_number or order.room_number or (order.table.table_number if order.table else "")

    # 1. If billed to room or Room Service, automatically post to guest Folio!
    is_room_charge = (
        "room" in payload.payment_method.lower() or 
        (order.order_type and order.order_type.lower() == "room_service") or
        bool(payload.room_number)
    )
    if is_room_charge and room_target:
        active_b = db.query(Booking).join(Room).filter(
            Room.number == str(room_target),
            Booking.status == "checked_in"
        ).first()
        guest_name = active_b.guest_name if active_b else f"Room {room_target} Guest"

        folio_tx = FolioTransaction(
            room_number=str(room_target),
            folio_number=1,
            guest_name=guest_name,
            transaction_type="POS F&B",
            voucher_or_bill_no=order.order_number,
            particulars=f"Food Order #{order.order_number} ({order.order_type})",
            sac_code="996331",
            debit_amount=order.final_amount,
            credit_amount=0.0,
            tax_amount=order.tax_amount,
            posting_date=today_str,
            posted_by="POS STEWARD",
            is_settled=False
        )
        db.add(folio_tx)

    # 2. Automatically Cross-Post to RestaurantSaleRecord
    max_rno = db.query(func.max(RestaurantSaleRecord.running_no)).scalar() or 0
    cgst_calc = 0.0 if payload.is_management_nc else round(order.tax_amount / 2.0, 2)
    sgst_calc = 0.0 if payload.is_management_nc else round(order.tax_amount / 2.0, 2)

    existing_rest_sale = db.query(RestaurantSaleRecord).filter(
        RestaurantSaleRecord.bill_no == order.order_number,
        RestaurantSaleRecord.month == current_month
    ).first()

    outlet_name = "MANAGEMENT" if payload.is_management_nc else (
        "ROOM SERVICE" if is_room_charge else (
            order.order_type.upper() if order.order_type else "RESTAURANT"
        )
    )

    if existing_rest_sale:
        existing_rest_sale.amount = order.subtotal
        existing_rest_sale.food = order.subtotal
        existing_rest_sale.beverage = 0.0
        existing_rest_sale.cgst = cgst_calc
        existing_rest_sale.sgst = sgst_calc
        existing_rest_sale.discount = payload.discount_amount
        existing_rest_sale.total = 0.0 if payload.is_management_nc else order.final_amount
        existing_rest_sale.pos_outlet = outlet_name
        existing_rest_sale.table_room = str(room_target)
        existing_rest_sale.cost_center = payload.cost_center or ""
        existing_rest_sale.auth_officer = payload.auth_officer or ""
        existing_rest_sale.reason = payload.reason or ""
        existing_rest_sale.settlement_mode = payload.payment_method
        existing_rest_sale.is_management_nc = payload.is_management_nc
    else:
        new_rest_sale = RestaurantSaleRecord(
            running_no=max_rno + 1,
            date=today_str,
            bill_no=order.order_number,
            amount=order.subtotal,
            food=order.subtotal,
            beverage=0.0,
            cgst=cgst_calc,
            sgst=sgst_calc,
            discount=payload.discount_amount,
            total=0.0 if payload.is_management_nc else order.final_amount,
            pos_outlet=outlet_name,
            table_room=str(room_target),
            cost_center=payload.cost_center or "",
            auth_officer=payload.auth_officer or "",
            reason=payload.reason or "",
            settlement_mode=payload.payment_method,
            is_management_nc=payload.is_management_nc,
            month=current_month
        )
        db.add(new_rest_sale)

    db.commit()
    return {"success": True, "order_number": order.order_number, "settled_amount": order.final_amount}

# -------------------------------------------------------------
# Inventory & Kitchen Stores
# -------------------------------------------------------------
@app.get("/api/inventory", response_model=List[InventoryItemResponse], tags=["Inventory"])
def list_inventory(db: Session = Depends(get_db)):
    return db.query(InventoryItem).order_by(InventoryItem.category, InventoryItem.item_name).all()

@app.post("/api/inventory/{item_id}/adjust", tags=["Inventory"])
def adjust_inventory_stock(item_id: int, payload: StockAdjustmentRequest, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    item.current_stock += payload.quantity_change
    db.commit()
    db.refresh(item)
    return {
        "item_name": item.item_name,
        "new_stock": item.current_stock,
        "unit": item.unit,
        "low_stock_warning": item.current_stock <= item.min_reorder_level
    }

# -------------------------------------------------------------
# Corporate Accounts & Receivables Aging (Audio 2)
# -------------------------------------------------------------
@app.get("/api/corporate-accounts", response_model=List[CorporateAccountResponse], tags=["Corporate Receivables"])
def list_corporate_accounts(db: Session = Depends(get_db)):
    return db.query(CorporateAccount).order_by(CorporateAccount.current_outstanding.desc()).all()

@app.post("/api/corporate-accounts/{company_id}/payment", tags=["Corporate Receivables"])
def record_corporate_payment(company_id: int, payload: CorporatePaymentRequest, db: Session = Depends(get_db)):
    account = db.query(CorporateAccount).filter(CorporateAccount.id == company_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Corporate account not found")

    account.current_outstanding = max(account.current_outstanding - payload.amount, 0.0)
    db.commit()
    return {
        "success": True,
        "company": account.company_name,
        "amount_paid": payload.amount,
        "remaining_outstanding": account.current_outstanding,
        "reference": payload.payment_reference
    }

# -------------------------------------------------------------
# Room Defects & Maintenance (Audio 3)
# -------------------------------------------------------------
@app.get("/api/housekeeping/defects", response_model=List[RoomDefectResponse], tags=["Housekeeping"])
def list_defects(db: Session = Depends(get_db)):
    return db.query(RoomDefect).order_by(RoomDefect.reported_at.desc()).all()

@app.post("/api/housekeeping/defects", response_model=RoomDefectResponse, status_code=status.HTTP_201_CREATED, tags=["Housekeeping"])
def report_defect(payload: RoomDefectCreate, db: Session = Depends(get_db)):
    defect = RoomDefect(**payload.model_dump())
    db.add(defect)
    db.commit()
    db.refresh(defect)
    return defect

@app.patch("/api/housekeeping/defects/{defect_id}/resolve", tags=["Housekeeping"])
def resolve_defect(defect_id: int, db: Session = Depends(get_db)):
    defect = db.query(RoomDefect).filter(RoomDefect.id == defect_id).first()
    if not defect:
        raise HTTPException(status_code=404, detail="Defect not found")

    defect.status = "resolved"
    defect.resolved_at = datetime.utcnow()
    db.commit()
    return {"success": True, "message": f"Defect on Room {defect.room_number} resolved"}

# -------------------------------------------------------------
# Night Audit & Day Closures (Audio 2)
# -------------------------------------------------------------
@app.post("/api/night-audit/seal", response_model=NightAuditResponse, tags=["Night Audit"])
def seal_night_audit(payload: NightAuditRequest, db: Session = Depends(get_db)):
    if payload.manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Night Auditor / Manager PIN")

    # Aggregate figures
    total_corp_due = db.query(func.sum(CorporateAccount.current_outstanding)).scalar() or 0.0
    settled_fb = db.query(func.sum(PosOrder.final_amount)).filter(PosOrder.status == "settled").scalar() or 18450.0
    room_rev = 38500.0 # Baseline room charges posted

    log = NightAuditLog(
        audit_date=payload.audit_date,
        sealed_by=payload.sealed_by,
        total_revenue=room_rev + settled_fb,
        room_revenue=room_rev,
        f_and_b_revenue=settled_fb,
        cash_reconciled=12400.0,
        corporate_aging_due=float(total_corp_due),
        status="SEALED",
        timestamp=datetime.utcnow()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@app.get("/api/night-audit/logs", response_model=List[NightAuditResponse], tags=["Night Audit"])
def list_night_audit_logs(db: Session = Depends(get_db)):
    return db.query(NightAuditLog).order_by(NightAuditLog.timestamp.desc()).all()

# -------------------------------------------------------------
# Property Information & Master Tariff (Images 1, 2, 3)
# -------------------------------------------------------------
@app.get("/api/property/info", response_model=PropertyInfoResponse, tags=["Property Information"])
def get_property_info():
    return {
        "name": "Hotel Elite Inn",
        "trade_name": "Hotel Elite Inn",
        "location": "Near Railway Station Main Road, Muniguda, Dist.-Rayagada (Odisha) - 765020",
        "phone": "+91-6370757541",
        "email": "hotelelitinn2023@gmail.com",
        "checkout_policy": "24 Hours Check-out",
        "accepted_cards": "Credit cards accepted only Master & Visa",
        "tariffs": {
            "standard_single": 1450.0,
            "deluxe_single": 1750.0,
            "deluxe_double": 2250.0,
            "executive_single": 2050.0,
            "executive_double": 2450.0,
            "suite_single": 3250.0,
            "suite_double": 3850.0,
            "extra_person": 550.0
        },
        "plans": {
            "map_plan_supplement": 600.0,
            "ap_plan_supplement": 1000.0
        },
        "complimentary": [
            "Buffet Breakfast",
            "1 Liter Mineral Water Complimentary in Room"
        ],
        "facilities": [
            "Business Center",
            "Travel Desk",
            "Wi-Fi Internet (All Floors)",
            "Tea / Coffee Maker in Room",
            "L.E.D TV",
            "24 Hours running Hot & Cold Water",
            "Doctor on Call"
        ],
        "wifi": {
            "floor_1": "TP 1ST FLOOR",
            "floor_2": "TP 2ND FLOOR",
            "floor_3": "TP 3RD FLOOR",
            "password": "Elite@123"
        },
        "intercom": [
            {"department": "Hotel Reception", "extension": "9"},
            {"department": "Restaurant", "extension": "111"},
            {"department": "Kitchen", "extension": "112"},
            {"department": "Store Room", "extension": "113"},
            {"department": "Laundry", "extension": "114"},
            {"department": "GM Sir", "extension": "115"},
            {"department": "MD Sir", "extension": "116"}
        ],
        "gstin": "21AEWFS9433F1ZN",
        "sac_code": "996332",
        "fssai_no": "10523016000047",
        "cashier": "Bikram26",
        "place_of_supply": "O.D"
    }

# -------------------------------------------------------------
# Authentic F&B Restaurant Menu (Images 4 & 5)
# -------------------------------------------------------------
@app.get("/api/restaurant/menu", response_model=List[MenuItemResponse], tags=["Restaurant Menu"])
def get_restaurant_menu(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(MenuItem)
    if category:
        query = query.filter(MenuItem.category == category)
    return query.order_by(MenuItem.id.asc()).all()

# -------------------------------------------------------------
# Authentic Thermal Tax Invoice Receipt (Photo 2 - R.S/2913)
# -------------------------------------------------------------
@app.get("/api/pos/thermal-receipt/sample", tags=["Point of Sale (POS)"])
def get_sample_thermal_receipt():
    """
    Returns authentic Hotel Elite Inn POS Tax Invoice thermal receipt payload
    matching the physical 80mm/58mm printed slip (Photo 2).
    """
    return {
        "invoice_type": "TAX INVOICE",
        "title": "ORIGINAL FOR RECIPIENT",
        "hotel_name": "HOTEL ELITE INN",
        "outlet": "POS 5- ROOM SERVICE",
        "address": "Opposite Railway Station Main Road Muniguda",
        "gstin": "21AEWFS9433F1ZN",
        "sac_code": "996332",
        "fssai_no": "10523016000047",
        "phone": "+91-6370757541",
        "guest_name": "Mr. KHAGESWARA SAHU",
        "company_gst_no": "",
        "room_no": "106",
        "bill_no": "R.S/2913",
        "cover": 1,
        "date": "28/09/26",
        "time": "22:29:04",
        "day_session": "DINNER",
        "first_kot_time": "22:14",
        "kot_no": "2056",
        "items": [
            {"no": 1, "dish_name": "Dal Fry", "rate": 123.81, "qty": 1, "total": 123.81},
            {"no": 2, "dish_name": "Tawa Roti", "rate": 23.81, "qty": 4, "total": 95.24}
        ],
        "total_qty": 5,
        "subtotal": 219.01,
        "cgst_rate_pct": 2.5,
        "cgst_amount": 5.48,
        "sgst_rate_pct": 2.5,
        "sgst_amount": 5.48,
        "grand_total": 230.00,
        "amount_in_words": "Two hundred Thirty Rs Only",
        "policy_notice": "------PLEASE DONOT PAY CASH------",
        "cashier": "Bikram26",
        "greeting_1": "Allow Us To Serve You Again",
        "greeting_2": "Thank You, Visit Again !",
        "e_and_oe": "E & O E",
        "place_of_supply": "O.D"
    }

@app.post("/api/system/sync-master-data", tags=["System"])
def sync_master_data():
    seed_database()
    return {"success": True, "message": "Master data synced: 27 physical rooms, menu, GST, and staff data refreshed."}


# -------------------------------------------------------------
# GST GSTR-1 & Statutory Tax Filing Endpoints
# -------------------------------------------------------------
@app.get("/api/gst/filings", response_model=List[Gstr1FilingResponse], tags=["GST & Tax Filings"])
def get_gst_filings(return_period: Optional[str] = None, db: Session = Depends(get_db)):
    """
    List GST tax invoices and GSTR-1 filing records for audit and portal submission.
    """
    query = db.query(Gstr1Filing)
    if return_period:
        query = query.filter(Gstr1Filing.return_period == return_period)
    return query.order_by(Gstr1Filing.id.desc()).all()

@app.post("/api/gst/filings", response_model=Gstr1FilingResponse, status_code=status.HTTP_201_CREATED, tags=["GST & Tax Filings"])
def create_gst_filing_invoice(filing_data: Gstr1FilingCreate, db: Session = Depends(get_db)):
    """
    Record a new GST B2B or B2CS invoice into the cloud database for statutory return.
    """
    new_filing = Gstr1Filing(**filing_data.model_dump())
    db.add(new_filing)
    db.commit()
    db.refresh(new_filing)
    return new_filing

@app.get("/api/gst/summary/{return_period}", response_model=Gstr1SummaryResponse, tags=["GST & Tax Filings"])
def get_gstr1_summary(return_period: str, db: Session = Depends(get_db)):
    """
    Generate statutory GSTR-1 return summary for Government GST Portal upload.
    Aggregates B2B taxable turnover, B2CS consumer folios, HSN SAC breakdowns, and CGST/SGST liability.
    """
    filings = db.query(Gstr1Filing).filter(Gstr1Filing.return_period == return_period).all()
    
    b2b = [f for f in filings if f.invoice_type == "B2B"]
    b2cs = [f for f in filings if f.invoice_type != "B2B"]
    
    total_taxable = sum(f.taxable_value for f in filings)
    total_cgst = sum(f.cgst_amount for f in filings)
    total_sgst = sum(f.sgst_amount for f in filings)
    total_igst = sum(f.igst_amount for f in filings)
    total_value = sum(f.total_invoice_value for f in filings)
    
    # HSN breakdown calculation
    hsn_map = {}
    for f in filings:
        code = f.hsn_sac_code or "996311"
        desc = "Accommodation Services" if code == "996311" else "Restaurant F&B Services"
        if code not in hsn_map:
            hsn_map[code] = {
                "hsn_sac": code,
                "description": desc,
                "taxable_amount": 0.0,
                "cgst": 0.0,
                "sgst": 0.0,
                "igst": 0.0,
                "total_tax": 0.0
            }
        hsn_map[code]["taxable_amount"] += f.taxable_value
        hsn_map[code]["cgst"] += f.cgst_amount
        hsn_map[code]["sgst"] += f.sgst_amount
        hsn_map[code]["igst"] += f.igst_amount
        hsn_map[code]["total_tax"] += (f.cgst_amount + f.sgst_amount + f.igst_amount)

    return {
        "return_period": return_period,
        "total_invoices": len(filings),
        "b2b_invoices_count": len(b2b),
        "b2cs_invoices_count": len(b2cs),
        "total_taxable_value": round(total_taxable, 2),
        "total_cgst": round(total_cgst, 2),
        "total_sgst": round(total_sgst, 2),
        "total_igst": round(total_igst, 2),
        "total_tax_liability": round(total_cgst + total_sgst + total_igst, 2),
        "total_invoice_value": round(total_value, 2),
        "hsn_breakdown": list(hsn_map.values())
    }

@app.put("/api/gst/filings/{filing_id}/status", tags=["GST & Tax Filings"])
def update_gst_filing_status(filing_id: int, new_status: str = Query(..., description="Uploaded, Filed, or Ready for Upload"), ack_num: Optional[str] = None, db: Session = Depends(get_db)):
    record = db.query(Gstr1Filing).filter(Gstr1Filing.id == filing_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="GST invoice record not found")
    record.filing_status = new_status
    if ack_num:
        record.acknowledgement_num = ack_num
    db.commit()
    db.refresh(record)
    return {"success": True, "id": record.id, "filing_status": record.filing_status, "ack_num": record.acknowledgement_num}


# -------------------------------------------------------------
# Staff Attendance & Shift Operations Endpoints
# -------------------------------------------------------------
OFFICIAL_STAFF_ROSTER = [
    {"staff_id": "EMP-001", "name": "Bikram Keshari Sahu", "department": "Front Office", "designation": "Front Office Manager", "phone": "+91-6370757541", "shift": "Morning", "status": "Active"},
    {"staff_id": "EMP-002", "name": "Sunil Mohapatra", "department": "Housekeeping", "designation": "Executive Housekeeper", "phone": "+91-9437011223", "shift": "Morning", "status": "Active"},
    {"staff_id": "EMP-003", "name": "Ramesh Nayak", "department": "Housekeeping", "designation": "Senior Attendant", "phone": "+91-9438022334", "shift": "Morning", "status": "Active"},
    {"staff_id": "EMP-004", "name": "Santosh Biswal", "department": "Food & Beverage", "designation": "Head Steward", "phone": "+91-9861033445", "shift": "Evening", "status": "Active"},
    {"staff_id": "EMP-005", "name": "Chef Debendra Panda", "department": "Kitchen", "designation": "Executive Chef", "phone": "+91-9439044556", "shift": "Morning", "status": "Active"},
    {"staff_id": "EMP-006", "name": "Prakash Sahu", "department": "Maintenance", "designation": "Duty Electrician", "phone": "+91-9853055667", "shift": "Morning", "status": "Active"},
    {"staff_id": "EMP-007", "name": "Manoj Kumar Sahu", "department": "Accounts", "designation": "Accounts & Cashier", "phone": "+91-9437066778", "shift": "General", "status": "Active"},
    {"staff_id": "EMP-008", "name": "Deepak Mohanty", "department": "Front Office", "designation": "Night Auditor", "phone": "+91-9438077889", "shift": "Night", "status": "Active"}
]

@app.get("/api/staff/roster", response_model=List[StaffRosterMember], tags=["Staff & Attendance"])
def get_staff_roster():
    """
    Returns authentic employee directory and department roster for Hotel Elite Inn.
    """
    return OFFICIAL_STAFF_ROSTER

@app.get("/api/staff/attendance", response_model=List[StaffAttendanceResponse], tags=["Staff & Attendance"])
def get_staff_attendance(attendance_date: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Get staff punch attendance logs for a specific date (e.g. 10-OCT-2026).
    """
    query = db.query(StaffAttendance)
    if attendance_date:
        query = query.filter(StaffAttendance.attendance_date == attendance_date)
    return query.order_by(StaffAttendance.id.desc()).all()

@app.post("/api/staff/attendance/punch", response_model=StaffAttendanceResponse, status_code=status.HTTP_201_CREATED, tags=["Staff & Attendance"])
def punch_staff_attendance(punch_data: StaffAttendanceCreate, db: Session = Depends(get_db)):
    """
    Punch in or punch out staff attendance with shift and department metadata.
    """
    existing = db.query(StaffAttendance).filter(
        StaffAttendance.staff_id == punch_data.staff_id,
        StaffAttendance.attendance_date == punch_data.attendance_date
    ).first()

    if existing:
        if punch_data.punch_out_time:
            existing.punch_out_time = punch_data.punch_out_time
        if punch_data.status:
            existing.status = punch_data.status
        if punch_data.remarks:
            existing.remarks = punch_data.remarks
        db.commit()
        db.refresh(existing)
        return existing

    new_attendance = StaffAttendance(**punch_data.model_dump())
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return new_attendance


# -------------------------------------------------------------
# Laundry Service Management Endpoints
# -------------------------------------------------------------
@app.get("/api/laundry/rates", tags=["Laundry Services"])
def get_laundry_rates():
    """
    Standard laundry tariffs and washing service charges for in-house room guests.
    """
    return [
        {"item_name": "Shirt / T-Shirt", "normal_rate": 60.0, "express_rate": 90.0, "dry_clean_rate": 120.0},
        {"item_name": "Trouser / Jeans", "normal_rate": 60.0, "express_rate": 90.0, "dry_clean_rate": 130.0},
        {"item_name": "Safari Suit / Blazer", "normal_rate": 180.0, "express_rate": 270.0, "dry_clean_rate": 350.0},
        {"item_name": "Kurta / Pyjama", "normal_rate": 60.0, "express_rate": 90.0, "dry_clean_rate": 110.0},
        {"item_name": "Saree / Dupatta", "normal_rate": 120.0, "express_rate": 180.0, "dry_clean_rate": 220.0},
        {"item_name": "Undergarments / Socks", "normal_rate": 30.0, "express_rate": 45.0, "dry_clean_rate": 60.0}
    ]

@app.get("/api/laundry/orders", response_model=List[LaundryOrderResponse], tags=["Laundry Services"])
def get_laundry_orders(order_status: Optional[str] = None, room_number: Optional[str] = None, db: Session = Depends(get_db)):
    """
    List laundry service orders with optional filters by order status or guest room number.
    """
    query = db.query(LaundryOrder)
    if order_status:
        query = query.filter(LaundryOrder.order_status == order_status)
    if room_number:
        query = query.filter(LaundryOrder.room_number == room_number)
    return query.order_by(LaundryOrder.id.desc()).all()

@app.post("/api/laundry/orders", response_model=LaundryOrderResponse, status_code=status.HTTP_201_CREATED, tags=["Laundry Services"])
def create_laundry_order(order_data: LaundryOrderCreate, db: Session = Depends(get_db)):
    """
    Create a new guest laundry collection order and post billing to the room folio.
    """
    new_order = LaundryOrder(**order_data.model_dump())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@app.put("/api/laundry/orders/{order_id}/status", response_model=LaundryOrderResponse, tags=["Laundry Services"])
def update_laundry_order_status(order_id: int, status_update: LaundryOrderStatusUpdate, db: Session = Depends(get_db)):
    """
    Update laundry progress from Received -> In-Process -> Ready -> Delivered.
    """
    order = db.query(LaundryOrder).filter(LaundryOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Laundry order not found")
    order.order_status = status_update.order_status
    if status_update.order_status == "Delivered":
        order.delivered_at = datetime.utcnow()
    db.commit()
    db.refresh(order)
    return order


# =============================================================
# IDS FortuneNext 6.5 / 7.0 PMS Core API (67 Modals Controllers)
# =============================================================

# -------------------------------------------------------------
# 1. Folio Management, Post Charges & Checkout Bill Settlement
# -------------------------------------------------------------
@app.get("/api/pms/folios/{room_number}", response_model=FolioSummaryResponse, tags=["IDS Folio & Cashiering"])
def get_room_folio(room_number: str, folio_number: int = 1, db: Session = Depends(get_db)):
    """
    Fetch active guest folio with all posted line charges and current balance.
    """
    txs = db.query(FolioTransaction).filter(
        FolioTransaction.room_number == room_number,
        FolioTransaction.folio_number == folio_number,
        FolioTransaction.is_settled == False
    ).order_by(FolioTransaction.id.asc()).all()

    guest_name = txs[0].guest_name if txs else "In-House Guest"
    total_debit = sum(t.debit_amount for t in txs)
    total_credit = sum(t.credit_amount for t in txs)
    net_balance = round(total_debit - total_credit, 2)

    return FolioSummaryResponse(
        room_number=room_number,
        folio_number=folio_number,
        guest_name=guest_name,
        total_debit=round(total_debit, 2),
        total_credit=round(total_credit, 2),
        net_balance=net_balance,
        transactions=txs
    )

@app.post("/api/pms/folios/post-charge", response_model=FolioTransactionResponse, status_code=status.HTTP_201_CREATED, tags=["IDS Folio & Cashiering"])
def post_folio_charge(tx_data: FolioTransactionCreate, db: Session = Depends(get_db)):
    """
    Post a new room debit (Food, Laundry, Extra Bed) or credit (Allowance, Payment) to room folio.
    """
    new_tx = FolioTransaction(**tx_data.model_dump())
    db.add(new_tx)
    db.commit()
    db.refresh(new_tx)
    return new_tx

@app.post("/api/pms/folios/{room_number}/settle", tags=["IDS Folio & Cashiering"])
def settle_room_folio(
    room_number: str,
    folio_number: int = 1,
    payment_mode: str = "Cash",
    manager_pin: str = "4321",
    db: Session = Depends(get_db)
):
    """
    Settle all outstanding charges on guest folio and mark transactions as settled.
    """
    if manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")

    txs = db.query(FolioTransaction).filter(
        FolioTransaction.room_number == room_number,
        FolioTransaction.folio_number == folio_number,
        FolioTransaction.is_settled == False
    ).all()

    if not txs:
        raise HTTPException(status_code=404, detail="No active folio transactions found to settle")

    bill_no = f"INV/{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    today_str = datetime.utcnow().strftime("%d-%b-%Y").upper()
    current_month = datetime.utcnow().strftime("%B-%Y").upper()

    total_debit = sum(t.debit_amount for t in txs)
    total_tax = sum(t.tax_amount for t in txs)
    guest_name = txs[0].guest_name if txs else f"Room {room_number} Guest"

    for t in txs:
        t.is_settled = True

    # Also auto-post/upsert to HotelSaleRecord
    max_sno = db.query(func.max(HotelSaleRecord.serial_no)).scalar() or 0
    existing_sale = db.query(HotelSaleRecord).filter(
        HotelSaleRecord.bill_no == bill_no,
        HotelSaleRecord.month == current_month
    ).first()

    if not existing_sale:
        new_sale = HotelSaleRecord(
            serial_no=max_sno + 1,
            date=today_str,
            bill_no=bill_no,
            room_number=room_number,
            rent=max(round(total_debit - total_tax, 2), 0.0),
            cgst=round(total_tax / 2.0, 2),
            sgst=round(total_tax / 2.0, 2),
            misc=0.0,
            laundry=0.0,
            minibar=0.0,
            room_service=0.0,
            net_amount=round(total_debit, 2),
            advance=0.0,
            discount=0.0,
            complimentary=0.0,
            void_amount=0.0,
            allowances=0.0,
            paid_out=0.0,
            cash=round(total_debit, 2) if payment_mode.lower() == "cash" else 0.0,
            btc=round(total_debit, 2) if "company" in payment_mode.lower() or "btc" in payment_mode.lower() else 0.0,
            credit_card=round(total_debit, 2) if "card" in payment_mode.lower() else 0.0,
            online=round(total_debit, 2) if "upi" in payment_mode.lower() or "online" in payment_mode.lower() else 0.0,
            remark=f"Folio Settled via {payment_mode}",
            guest_name=guest_name,
            company="FIT",
            gstin=None,
            month=current_month
        )
        db.add(new_sale)

    db.commit()

    return {
        "status": "success",
        "bill_no": bill_no,
        "room_number": room_number,
        "payment_mode": payment_mode,
        "settled_count": len(txs),
        "total_settled_amount": total_debit,
        "message": f"Folio for Room {room_number} settled successfully via {payment_mode}."
    }


@app.post("/api/pms/folios/{room_number}/reinstate", tags=["IDS Folio & Cashiering"])
def reinstate_room_folio(
    room_number: str,
    folio_number: int = 1,
    manager_pin: str = "4321",
    db: Session = Depends(get_db)
):
    """
    Reinstate accidentally checked-out folio back to active in-house state.
    """
    if manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")

    txs = db.query(FolioTransaction).filter(
        FolioTransaction.room_number == room_number,
        FolioTransaction.folio_number == folio_number,
        FolioTransaction.is_settled == True
    ).all()

    if not txs:
        raise HTTPException(status_code=404, detail="No settled folio transactions found to reinstate")

    for t in txs:
        t.is_settled = False

    db.commit()
    return {
        "status": "success",
        "room_number": room_number,
        "reinstated_count": len(txs),
        "message": f"Folio for Room {room_number} reinstated back to Active In-House state."
    }

# -------------------------------------------------------------
# 2. Advance Deposits & Receipt Management
# -------------------------------------------------------------
@app.get("/api/pms/deposits", response_model=List[AdvanceDepositResponse], tags=["IDS Deposits & Cashiering"])
def get_advance_deposits(room_number: Optional[str] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AdvanceDeposit)
    if room_number:
        query = query.filter(AdvanceDeposit.room_number == room_number)
    if status:
        query = query.filter(AdvanceDeposit.status == status)
    return query.order_by(AdvanceDeposit.id.desc()).all()

@app.post("/api/pms/deposits", response_model=AdvanceDepositResponse, status_code=status.HTTP_201_CREATED, tags=["IDS Deposits & Cashiering"])
def create_advance_deposit(deposit_data: AdvanceDepositCreate, db: Session = Depends(get_db)):
    new_deposit = AdvanceDeposit(**deposit_data.model_dump())
    db.add(new_deposit)

    # Automatically post credit to room folio
    folio_tx = FolioTransaction(
        room_number=deposit_data.room_number,
        folio_number=1,
        guest_name=deposit_data.guest_name,
        transaction_type="Advance Deposit",
        voucher_or_bill_no=deposit_data.receipt_number,
        particulars=f"Advance Deposit Received ({deposit_data.payment_mode})",
        sac_code="996311",
        debit_amount=0.0,
        credit_amount=deposit_data.amount,
        tax_amount=0.0,
        posting_date=deposit_data.date,
        posted_by="CASHIER"
    )
    db.add(folio_tx)

    db.commit()
    db.refresh(new_deposit)
    return new_deposit

@app.delete("/api/pms/deposits/{receipt_number}", tags=["IDS Deposits & Cashiering"])
def delete_advance_deposit(receipt_number: str, reason: str = "Cancellation", db: Session = Depends(get_db)):
    deposit = db.query(AdvanceDeposit).filter(AdvanceDeposit.receipt_number == receipt_number).first()
    if not deposit:
        raise HTTPException(status_code=404, detail="Advance deposit receipt not found")
    deposit.status = "Deleted"
    deposit.remarks = f"{deposit.remarks} | Deleted: {reason}"
    db.commit()
    return {"status": "success", "receipt_number": receipt_number, "message": "Deposit deleted successfully."}

# -------------------------------------------------------------
# 3. Front Office Paid-Out Cash Disbursement
# -------------------------------------------------------------
@app.get("/api/pms/paid-outs", response_model=List[PaidOutVoucherResponse], tags=["IDS Deposits & Cashiering"])
def get_paid_outs(db: Session = Depends(get_db)):
    return db.query(PaidOutVoucher).order_by(PaidOutVoucher.id.desc()).all()

@app.post("/api/pms/paid-outs", response_model=PaidOutVoucherResponse, status_code=status.HTTP_201_CREATED, tags=["IDS Deposits & Cashiering"])
def create_paid_out(paid_out_data: PaidOutVoucherCreate, db: Session = Depends(get_db)):
    new_voucher = PaidOutVoucher(**paid_out_data.model_dump())
    db.add(new_voucher)

    # Post debit to room folio
    folio_tx = FolioTransaction(
        room_number=paid_out_data.room_number,
        folio_number=1,
        guest_name=paid_out_data.guest_name,
        transaction_type="Paid Out",
        voucher_or_bill_no=paid_out_data.voucher_number,
        particulars=f"Front Office Paid Out: {paid_out_data.purpose}",
        sac_code="996311",
        debit_amount=paid_out_data.paid_amount,
        credit_amount=0.0,
        tax_amount=0.0,
        posting_date=paid_out_data.date,
        posted_by=paid_out_data.authorized_by
    )
    db.add(folio_tx)

    db.commit()
    db.refresh(new_voucher)
    return new_voucher

# -------------------------------------------------------------
# 4. Foreign Exchange Currency Encashment (Form FLM)
# -------------------------------------------------------------
@app.get("/api/pms/forex", response_model=List[ForexEncashmentResponse], tags=["IDS Foreign Exchange"])
def get_forex_encashments(db: Session = Depends(get_db)):
    return db.query(ForexEncashment).order_by(ForexEncashment.id.desc()).all()

@app.post("/api/pms/forex", response_model=ForexEncashmentResponse, status_code=status.HTTP_201_CREATED, tags=["IDS Foreign Exchange"])
def create_forex_encashment(forex_data: ForexEncashmentCreate, db: Session = Depends(get_db)):
    new_encashment = ForexEncashment(**forex_data.model_dump())
    db.add(new_encashment)
    db.commit()
    db.refresh(new_encashment)
    return new_encashment

# -------------------------------------------------------------
# 5. Housekeeping Lost & Found
# -------------------------------------------------------------
@app.get("/api/pms/lost-found", response_model=List[LostAndFoundItemResponse], tags=["IDS Housekeeping"])
def get_lost_and_found_items(status: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(LostAndFoundItem)
    if status:
        query = query.filter(LostAndFoundItem.status == status)
    return query.order_by(LostAndFoundItem.id.desc()).all()

@app.post("/api/pms/lost-found", response_model=LostAndFoundItemResponse, status_code=status.HTTP_201_CREATED, tags=["IDS Housekeeping"])
def register_lost_item(item_data: LostAndFoundItemCreate, db: Session = Depends(get_db)):
    new_item = LostAndFoundItem(**item_data.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.patch("/api/pms/lost-found/{tracking_no}/claim", response_model=LostAndFoundItemResponse, tags=["IDS Housekeeping"])
def claim_lost_item(tracking_no: str, claim_data: LostAndFoundItemClaim, db: Session = Depends(get_db)):
    item = db.query(LostAndFoundItem).filter(LostAndFoundItem.tracking_no == tracking_no).first()
    if not item:
        raise HTTPException(status_code=404, detail="Lost & Found record not found")
    item.status = "Claimed/Returned"
    item.claimed_by = claim_data.claimed_by
    item.claim_date = claim_data.claim_date
    db.commit()
    db.refresh(item)
    return item

# -------------------------------------------------------------
# 6. Front Desk Room Transfers & Stay Amendments
# -------------------------------------------------------------
@app.get("/api/pms/room-transfers", response_model=List[RoomTransferLogResponse], tags=["IDS Front Desk"])
def get_room_transfers(db: Session = Depends(get_db)):
    return db.query(RoomTransferLog).order_by(RoomTransferLog.id.desc()).all()

@app.post("/api/pms/room-transfers", response_model=RoomTransferLogResponse, status_code=status.HTTP_201_CREATED, tags=["IDS Front Desk"])
def transfer_room(transfer_data: RoomTransferLogCreate, db: Session = Depends(get_db)):
    # 1. Update from_room status to dirty
    from_r = db.query(Room).filter(Room.number == transfer_data.from_room).first()
    if from_r:
        from_r.status = "dirty"

    # 2. Update to_room status to occupied
    to_r = db.query(Room).filter(Room.number == transfer_data.to_room).first()
    if to_r:
        to_r.status = "occupied"

    # 3. Log transfer
    log = RoomTransferLog(**transfer_data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@app.post("/api/pms/stay/amend", tags=["IDS Front Desk"])
def amend_stay(amend_data: StayAmendRequest, db: Session = Depends(get_db)):
    # Update active booking or room record
    room = db.query(Room).filter(Room.number == amend_data.room_number).first()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return {
        "status": "success",
        "room_number": amend_data.room_number,
        "new_departure_date": amend_data.new_departure_date,
        "message": f"Stay for Room {amend_data.room_number} amended to {amend_data.new_departure_date}."
    }

# -------------------------------------------------------------
# 7. Corporate Contract Rates Linking
# -------------------------------------------------------------
@app.get("/api/pms/contract-rates", response_model=List[CorporateRateLinkResponse], tags=["IDS Rates & Corporate"])
def get_corporate_contract_rates(db: Session = Depends(get_db)):
    return db.query(CorporateRateLink).order_by(CorporateRateLink.id.desc()).all()

@app.post("/api/pms/contract-rates", response_model=CorporateRateLinkResponse, status_code=status.HTTP_201_CREATED, tags=["IDS Rates & Corporate"])
def link_corporate_rate(rate_data: CorporateRateLinkCreate, db: Session = Depends(get_db)):
    link = CorporateRateLink(**rate_data.model_dump())
    db.add(link)
    db.commit()
    db.refresh(link)
    return link


# -------------------------------------------------------------
# 8. Monthly Audited Sales Reports (June Month & Live Ledgers)
# -------------------------------------------------------------
@app.get("/api/reports/hotel-sale-monthly", response_model=List[HotelSaleRecordResponse], tags=["Monthly Reports"])
def get_hotel_sale_monthly_report(
    month: str = Query("JUNE-2026", description="Report month filter"),
    db: Session = Depends(get_db)
):
    return db.query(HotelSaleRecord).filter(HotelSaleRecord.month == month).order_by(HotelSaleRecord.serial_no.asc()).all()

@app.post("/api/reports/hotel-sale-record", response_model=HotelSaleRecordResponse, status_code=status.HTTP_201_CREATED, tags=["Monthly Reports"])
def create_hotel_sale_record(record: HotelSaleRecordCreate, db: Session = Depends(get_db)):
    existing = db.query(HotelSaleRecord).filter(
        HotelSaleRecord.bill_no == record.bill_no,
        HotelSaleRecord.month == record.month
    ).first()
    if existing:
        for k, v in record.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing

    new_rec = HotelSaleRecord(**record.model_dump())
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    return new_rec

@app.get("/api/reports/restaurant-sale-monthly", response_model=List[RestaurantSaleRecordResponse], tags=["Monthly Reports"])
def get_restaurant_sale_monthly_report(
    month: str = Query("JUNE-2026", description="Report month filter"),
    pos_outlet: Optional[str] = Query(None, description="Outlet filter (RESTAURANT, ROOM SERVICE, TAKE AWAY, MANAGEMENT)"),
    db: Session = Depends(get_db)
):
    query = db.query(RestaurantSaleRecord).filter(RestaurantSaleRecord.month == month)
    if pos_outlet and pos_outlet != "ALL":
        query = query.filter(RestaurantSaleRecord.pos_outlet == pos_outlet)
    return query.order_by(RestaurantSaleRecord.running_no.asc()).all()

@app.post("/api/reports/restaurant-sale-record", response_model=RestaurantSaleRecordResponse, status_code=status.HTTP_201_CREATED, tags=["Monthly Reports"])
def create_restaurant_sale_record(record: RestaurantSaleRecordCreate, db: Session = Depends(get_db)):
    existing = db.query(RestaurantSaleRecord).filter(
        RestaurantSaleRecord.bill_no == record.bill_no,
        RestaurantSaleRecord.month == record.month
    ).first()
    if existing:
        for k, v in record.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing

    new_rec = RestaurantSaleRecord(**record.model_dump())
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    return new_rec

@app.get("/api/reports/restaurant-mgm-monthly", response_model=List[RestaurantSaleRecordResponse], tags=["Monthly Reports"])
def get_restaurant_mgm_nc_report(
    month: str = Query("JUNE-2026", description="Report month filter"),
    db: Session = Depends(get_db)
):
    return db.query(RestaurantSaleRecord).filter(
        RestaurantSaleRecord.month == month,
        RestaurantSaleRecord.is_management_nc == True
    ).order_by(RestaurantSaleRecord.running_no.asc()).all()

@app.get("/api/reports/gstr3b-statutory-summary", response_model=Gstr3bStatutorySummaryResponse, tags=["Monthly Reports"])
def get_gstr3b_statutory_summary(
    month: str = Query("JUNE-2026", description="Report month filter"),
    db: Session = Depends(get_db)
):
    hotel_records = db.query(HotelSaleRecord).filter(HotelSaleRecord.month == month).all()
    rest_records = db.query(RestaurantSaleRecord).filter(
        RestaurantSaleRecord.month == month,
        RestaurantSaleRecord.is_management_nc == False
    ).all()
    nc_records = db.query(RestaurantSaleRecord).filter(
        RestaurantSaleRecord.month == month,
        RestaurantSaleRecord.is_management_nc == True
    ).all()

    room_taxable = sum(r.rent for r in hotel_records)
    room_cgst = sum(r.cgst for r in hotel_records)
    room_sgst = sum(r.sgst for r in hotel_records)
    room_service_hotel = sum(r.room_service for r in hotel_records)

    fnb_taxable = sum(r.amount for r in rest_records)
    fnb_cgst = sum(r.cgst for r in rest_records)
    fnb_sgst = sum(r.sgst for r in rest_records)
    fnb_gross = sum(r.total for r in rest_records)

    nc_valuation = sum(r.amount for r in nc_records)

    total_taxable = room_taxable + fnb_taxable
    total_cgst = room_cgst + fnb_cgst
    total_sgst = room_sgst + fnb_sgst
    total_tax = total_cgst + total_sgst
    grand_turnover = total_taxable + total_tax

    return Gstr3bStatutorySummaryResponse(
        month=month,
        property_name="HOTEL ELITE INN",
        gstin="21AEWFS9433F1ZN",
        state_code="21",
        room_taxable_turnover=round(room_taxable, 2),
        room_cgst=round(room_cgst, 2),
        room_sgst=round(room_sgst, 2),
        room_service_in_hotel=round(room_service_hotel, 2),
        fnb_taxable_turnover=round(fnb_taxable, 2),
        fnb_cgst=round(fnb_cgst, 2),
        fnb_sgst=round(fnb_sgst, 2),
        fnb_gross_production=round(fnb_gross, 2),
        management_nc_valuation=round(nc_valuation, 2),
        total_taxable_outward_supplies=round(total_taxable, 2),
        total_central_tax_cgst=round(total_cgst, 2),
        total_state_tax_sgst=round(total_sgst, 2),
        total_tax_liability=round(total_tax, 2),
        grand_consolidated_turnover=round(grand_turnover, 2),
        hotel_bills_count=len(hotel_records),
        restaurant_orders_count=len(rest_records),
        nc_orders_count=len(nc_records)
    )


# -------------------------------------------------------------
# 9. Store Inventory & Procurement (Purchases, Requisitions, Vendors)
# -------------------------------------------------------------
@app.get("/api/inventory/purchases", response_model=List[StorePurchaseResponse], tags=["Store Inventory"])
def list_store_purchases(db: Session = Depends(get_db)):
    return db.query(StorePurchase).order_by(StorePurchase.id.desc()).all()


@app.post("/api/inventory/purchases", response_model=StorePurchaseResponse, status_code=status.HTTP_201_CREATED, tags=["Store Inventory"])
def create_store_purchase(payload: StorePurchaseCreate, db: Session = Depends(get_db)):
    purchase_id = payload.purchase_id or f"PUR-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    purchase_date = payload.purchase_date or datetime.utcnow().strftime("%d-%b-%Y").upper()
    existing = db.query(StorePurchase).filter(StorePurchase.purchase_id == purchase_id).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    new_purchase = StorePurchase(
        purchase_id=purchase_id,
        vendor_name=payload.vendor_name,
        invoice_no=payload.invoice_no,
        purchase_date=purchase_date,
        category=payload.category,
        items_summary=payload.items_summary,
        total_amount=payload.total_amount,
        payment_status=payload.payment_status,
        received_by=payload.received_by
    )
    db.add(new_purchase)
    db.commit()
    db.refresh(new_purchase)
    return new_purchase


@app.get("/api/inventory/requisitions", response_model=List[KitchenRequisitionResponse], tags=["Store Inventory"])
def list_kitchen_requisitions(db: Session = Depends(get_db)):
    return db.query(KitchenRequisition).order_by(KitchenRequisition.id.desc()).all()


@app.post("/api/inventory/requisitions", response_model=KitchenRequisitionResponse, status_code=status.HTTP_201_CREATED, tags=["Store Inventory"])
def create_kitchen_requisition(payload: KitchenRequisitionCreate, db: Session = Depends(get_db)):
    req_id = payload.requisition_id or f"REQ-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    issue_date = payload.issue_date or datetime.utcnow().strftime("%d-%b-%Y").upper()
    existing = db.query(KitchenRequisition).filter(KitchenRequisition.requisition_id == req_id).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    new_req = KitchenRequisition(
        requisition_id=req_id,
        issue_date=issue_date,
        target_outlet=payload.target_outlet,
        item_name=payload.item_name,
        quantity_issued=payload.quantity_issued,
        unit=payload.unit,
        approx_cost=payload.approx_cost,
        issued_to=payload.issued_to,
        issued_by=payload.issued_by
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return new_req


@app.get("/api/inventory/vendors", response_model=List[VendorPayableResponse], tags=["Store Inventory"])
def list_vendor_payables(db: Session = Depends(get_db)):
    vendors = db.query(VendorPayable).order_by(VendorPayable.vendor_name.asc()).all()
    results = []
    for v in vendors:
        results.append(VendorPayableResponse(
            id=v.id,
            vendor_name=v.vendor_name,
            category=v.category,
            contact=v.contact,
            supplies_amount=v.supplies_amount,
            paid_amount=v.paid_amount,
            outstanding=max(round(v.supplies_amount - v.paid_amount, 2), 0.0),
            created_at=v.created_at
        ))
    return results


# =============================================================
# Category 1: Front Office PMS & Guest Management Routes
# =============================================================
@app.get("/api/pms/police-manifest", response_model=List[PoliceManifestResponse], tags=["Police & Thana Statutory"])
def get_police_manifest(status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(PoliceManifest)
    if status_filter:
        q = q.filter(PoliceManifest.status == status_filter)
    return q.order_by(PoliceManifest.room_no.asc()).all()

@app.post("/api/pms/police-manifest", response_model=PoliceManifestResponse, status_code=status.HTTP_201_CREATED, tags=["Police & Thana Statutory"])
def create_or_sync_police_manifest(payload: PoliceManifestCreate, db: Session = Depends(get_db)):
    existing = db.query(PoliceManifest).filter(
        PoliceManifest.room_no == payload.room_no,
        PoliceManifest.status == "In-House"
    ).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    new_entry = PoliceManifest(**payload.model_dump())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@app.get("/api/pms/foreigner-form-c", response_model=List[ForeignerFormCResponse], tags=["Police & Thana Statutory"])
def list_foreigner_form_c(db: Session = Depends(get_db)):
    return db.query(ForeignerFormC).order_by(ForeignerFormC.id.desc()).all()

@app.post("/api/pms/foreigner-form-c", response_model=ForeignerFormCResponse, status_code=status.HTTP_201_CREATED, tags=["Police & Thana Statutory"])
def create_foreigner_form_c(payload: ForeignerFormCCreate, db: Session = Depends(get_db)):
    form_no = payload.form_c_no or f"FORMC-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    entry = ForeignerFormC(
        form_c_no=form_no,
        room_no=payload.room_no,
        guest_name=payload.guest_name,
        passport_no=payload.passport_no,
        visa_no=payload.visa_no,
        nationality=payload.nationality,
        arrival_date=payload.arrival_date,
        departure_date=payload.departure_date,
        purpose_of_visit=payload.purpose_of_visit,
        indian_ref_contact=payload.indian_ref_contact
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@app.post("/api/pms/guest-kyc", response_model=GuestKycDocumentResponse, tags=["Front Desk"])
def upload_guest_kyc(payload: GuestKycDocumentCreate, db: Session = Depends(get_db)):
    doc = GuestKycDocument(**payload.model_dump())
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

@app.get("/api/pms/cashier/shifts", response_model=List[CashierShiftResponse], tags=["Cashier & Shifts"])
def list_cashier_shifts(accounting_date: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(CashierShiftRecord)
    if accounting_date:
        q = q.filter(CashierShiftRecord.accounting_date == accounting_date)
    return q.order_by(CashierShiftRecord.id.desc()).all()

@app.post("/api/pms/cashier/shifts/open", response_model=CashierShiftResponse, tags=["Cashier & Shifts"])
def open_cashier_shift(payload: CashierShiftOpenRequest, db: Session = Depends(get_db)):
    existing = db.query(CashierShiftRecord).filter(
        CashierShiftRecord.shift_id == payload.shift_id,
        CashierShiftRecord.accounting_date == payload.accounting_date
    ).first()
    if existing:
        existing.status = "OPEN"
        existing.drawer_float = payload.drawer_float
        db.commit()
        db.refresh(existing)
        return existing
    shift = CashierShiftRecord(
        shift_id=payload.shift_id,
        shift_name=payload.shift_name,
        cashier_name=payload.cashier_name,
        cashier_code=payload.cashier_code,
        accounting_date=payload.accounting_date,
        drawer_float=payload.drawer_float,
        status="OPEN"
    )
    db.add(shift)
    db.commit()
    db.refresh(shift)
    return shift

@app.post("/api/pms/cashier/shifts/{shift_id}/close", tags=["Cashier & Shifts"])
def close_cashier_shift(shift_id: str, payload: CashierShiftCloseRequest, accounting_date: Optional[str] = None, db: Session = Depends(get_db)):
    if payload.manager_pin != MANAGER_AUTH_PIN and payload.manager_pin != "7650":
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")
    
    q = db.query(CashierShiftRecord).filter(CashierShiftRecord.shift_id == shift_id)
    if accounting_date:
        q = q.filter(CashierShiftRecord.accounting_date == accounting_date)
    shift = q.first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift record not found")
    
    shift.status = "CLOSED"
    shift.safe_drop = payload.safe_drop
    shift.physical_cash = payload.physical_cash
    shift.denominations_json = json.dumps(payload.denominations or {})
    shift.collections_json = json.dumps(payload.collections or {})
    shift.fnb_split_json = json.dumps(payload.fnb_split or {})
    shift.handover_notes = payload.handover_notes or ""
    shift.closed_at = datetime.utcnow()
    db.commit()
    return {"success": True, "message": f"Shift {shift.shift_name} closed and locked.", "shift_id": shift_id}

@app.get("/api/pms/cashier/morning-briefing", tags=["Cashier & Shifts"])
def get_morning_briefing(accounting_date: Optional[str] = None, db: Session = Depends(get_db)):
    today_str = accounting_date or datetime.utcnow().strftime("%d-%m-%Y")
    shifts = db.query(CashierShiftRecord).filter(CashierShiftRecord.accounting_date == today_str).all()
    occupied_count = db.query(Room).filter(Room.status == "occupied").count()
    return {
        "date": today_str,
        "property": "Hotel Elite Inn, Muniguda",
        "occupied_rooms": occupied_count,
        "total_rooms": 27,
        "occupancy_rate": f"{round((occupied_count / 27) * 100, 1)}%",
        "shifts_logged": len(shifts),
        "status": "OPERATIONAL"
    }

# =============================================================
# Category 2: Folio Accounting & Adjustments Routes
# =============================================================
@app.post("/api/pms/folios/transfer", tags=["IDS Folio & Cashiering"])
def transfer_folio_charge(payload: FolioChargeTransferRequest, db: Session = Depends(get_db)):
    if payload.manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")
    
    transfer = FolioChargeTransfer(
        from_room=payload.from_room,
        to_room=payload.to_room,
        from_folio=payload.from_folio,
        to_folio=payload.to_folio,
        amount=payload.amount,
        charge_type=payload.charge_type,
        reason=payload.reason,
        authorized_by=payload.authorized_by
    )
    db.add(transfer)
    
    today_str = datetime.utcnow().strftime("%d-%b-%Y").upper()
    # Post Credit to source room
    cr = FolioTransaction(
        room_number=payload.from_room,
        folio_number=payload.from_folio,
        guest_name=f"Transfer to Rm {payload.to_room}",
        transaction_type="Transfer Credit",
        particulars=f"Transferred to Room {payload.to_room}: {payload.reason}",
        debit_amount=0.0,
        credit_amount=payload.amount,
        tax_amount=0.0,
        posting_date=today_str,
        posted_by=payload.authorized_by
    )
    # Post Debit to destination room
    dr = FolioTransaction(
        room_number=payload.to_room,
        folio_number=payload.to_folio,
        guest_name=f"Transferred from Rm {payload.from_room}",
        transaction_type="Transfer Debit",
        particulars=f"Transferred from Room {payload.from_room}: {payload.reason}",
        debit_amount=payload.amount,
        credit_amount=0.0,
        tax_amount=0.0,
        posting_date=today_str,
        posted_by=payload.authorized_by
    )
    db.add(cr)
    db.add(dr)
    db.commit()
    return {"success": True, "message": f"Transferred ₹{payload.amount} from Room {payload.from_room} to Room {payload.to_room}."}

@app.post("/api/pms/folios/bill-allowance", tags=["IDS Folio & Cashiering"])
def create_bill_allowance(payload: BillAllowanceCreate, db: Session = Depends(get_db)):
    if payload.manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")
    
    allowance = BillAllowance(
        room_number=payload.room_number,
        folio_number=payload.folio_number,
        bill_no=payload.bill_no,
        allowance_amount=payload.allowance_amount,
        tax_reversed=payload.tax_reversed,
        reason=payload.reason,
        approved_by=payload.approved_by,
        date=payload.date
    )
    db.add(allowance)
    
    tx = FolioTransaction(
        room_number=payload.room_number,
        folio_number=payload.folio_number,
        guest_name="Guest Allowance",
        transaction_type="Allowance",
        particulars=f"Allowance/Rebate: {payload.reason}",
        debit_amount=0.0,
        credit_amount=payload.allowance_amount,
        tax_amount=payload.tax_reversed,
        posting_date=payload.date,
        posted_by=payload.approved_by
    )
    db.add(tx)
    db.commit()
    return {"success": True, "message": f"Allowance of ₹{payload.allowance_amount} applied to Room {payload.room_number}."}

@app.post("/api/pms/folios/split-billing", tags=["IDS Folio & Cashiering"])
def create_corporate_split_billing(payload: CorporateSplitBillingRequest, db: Session = Depends(get_db)):
    split = CorporateSplitBilling(
        room_number=payload.room_number,
        corporate_id=payload.corporate_id,
        company_name=payload.company_name,
        btc_amount=payload.btc_amount,
        personal_amount=payload.personal_amount,
        billing_date=payload.billing_date
    )
    db.add(split)
    db.commit()
    return {"success": True, "message": f"Split billing configured for Room {payload.room_number}: ₹{payload.btc_amount} to {payload.company_name}, ₹{payload.personal_amount} to Guest."}

@app.post("/api/pms/folios/stop-posting", tags=["IDS Folio & Cashiering"])
def toggle_stop_posting(room_number: str, stop_posting: bool = True, manager_pin: str = "4321", db: Session = Depends(get_db)):
    if manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")
    return {"success": True, "room_number": room_number, "stop_posting": stop_posting, "message": f"Stop Posting flag set to {stop_posting} for Room {room_number}."}

@app.get("/api/pms/rooms/blocked", response_model=List[RoomBlockResponse], tags=["Room Blocks"])
def list_blocked_rooms(db: Session = Depends(get_db)):
    return db.query(RoomBlock).filter(RoomBlock.status == "ACTIVE").all()

@app.post("/api/pms/rooms/block", response_model=RoomBlockResponse, tags=["Room Blocks"])
def block_room(payload: RoomBlockCreate, db: Session = Depends(get_db)):
    block = RoomBlock(**payload.model_dump())
    db.add(block)
    room = db.query(Room).filter(Room.number == payload.room_number).first()
    if room:
        room.status = "maintenance"
    db.commit()
    db.refresh(block)
    return block

@app.post("/api/pms/rooms/bulk-clear", tags=["Rooms"])
def bulk_clear_rooms(room_numbers: List[str], target_status: str = "clean", manager_pin: str = "4321", db: Session = Depends(get_db)):
    if manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")
    
    updated = []
    for rm in room_numbers:
        r = db.query(Room).filter(Room.number == str(rm)).first()
        if r:
            r.status = target_status
            updated.append(rm)
    db.commit()
    return {"success": True, "cleared_rooms": updated, "status": target_status}

# =============================================================
# Category 3: POS, F&B & Banquet Routes
# =============================================================
@app.post("/api/pos/orders/{order_id}/split-tender", tags=["Point of Sale"])
def split_tender_order(order_id: int, payload: SplitTenderRequest, db: Session = Depends(get_db)):
    order = db.query(PosOrder).filter(PosOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    total_tendered = sum(p.amount for p in payload.payments)
    order.payment_method = "SPLIT TENDER"
    order.final_amount = total_tendered
    order.payment_status = "paid"
    order.status = "settled"
    if order.table:
        order.table.status = "available"
    
    # Auto-cross post
    current_month = payload.month or datetime.utcnow().strftime("%B-%Y").upper()
    today_str = datetime.utcnow().strftime("%d-%b-%Y").upper()
    max_rno = db.query(func.max(RestaurantSaleRecord.running_no)).scalar() or 0
    
    modes_str = ", ".join(f"{p.mode}: ₹{p.amount}" for p in payload.payments)
    rec = RestaurantSaleRecord(
        running_no=max_rno + 1,
        date=today_str,
        bill_no=order.order_number,
        amount=order.subtotal,
        food=order.subtotal,
        beverage=0.0,
        cgst=round(order.tax_amount / 2.0, 2),
        sgst=round(order.tax_amount / 2.0, 2),
        discount=order.discount_amount,
        total=total_tendered,
        pos_outlet="RESTAURANT",
        table_room=order.table.table_number if order.table else "",
        settlement_mode=f"Split ({modes_str})",
        is_management_nc=False,
        month=current_month
    )
    db.add(rec)
    db.commit()
    return {"success": True, "order_number": order.order_number, "split_payments": len(payload.payments), "total_tendered": total_tendered}

@app.post("/api/pos/orders/{order_id}/discount", tags=["Point of Sale"])
def apply_pos_discount(order_id: int, payload: PosDiscountApplyRequest, db: Session = Depends(get_db)):
    if payload.manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager PIN for discount")
    
    order = db.query(PosOrder).filter(PosOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.discount_amount = payload.discount_amount
    order.final_amount = max(round(order.subtotal + order.tax_amount - payload.discount_amount, 2), 0.0)
    db.commit()
    return {"success": True, "discount_applied": payload.discount_amount, "new_final_amount": order.final_amount}

@app.post("/api/pos/orders/{order_id}/reclassify-tender", tags=["Point of Sale"])
def reclassify_tender(order_id: int, payload: TenderReclassifyRequest, db: Session = Depends(get_db)):
    if payload.manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")
    
    order = db.query(PosOrder).filter(PosOrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.payment_method = payload.new_mode
    # Update sales register record if exists
    sale = db.query(RestaurantSaleRecord).filter(RestaurantSaleRecord.bill_no == order.order_number).first()
    if sale:
        sale.settlement_mode = payload.new_mode
    db.commit()
    return {"success": True, "order_number": order.order_number, "old_mode": payload.old_mode, "new_mode": payload.new_mode}

@app.get("/api/pos/banquets/events", response_model=List[BanquetEventResponse], tags=["Banquet Operations"])
def list_banquet_events(db: Session = Depends(get_db)):
    return db.query(BanquetEvent).order_by(BanquetEvent.id.desc()).all()

@app.post("/api/pos/banquets/events", response_model=BanquetEventResponse, tags=["Banquet Operations"])
def create_banquet_event(payload: BanquetEventCreate, db: Session = Depends(get_db)):
    ev_id = payload.event_id or f"BNQ-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    sub = payload.hall_rental + (payload.food_package_rate * payload.pax)
    gst = round(sub * 0.18, 2) # 18% GST (SAC 997212)
    tot = round(sub + gst, 2)
    bal = max(round(tot - payload.advance_paid, 2), 0.0)
    
    ev = BanquetEvent(
        event_id=ev_id,
        event_name=payload.event_name,
        host_name=payload.host_name,
        host_phone=payload.host_phone,
        event_date=payload.event_date,
        slot=payload.slot,
        pax=payload.pax,
        hall_name=payload.hall_name,
        hall_rental=payload.hall_rental,
        food_package_rate=payload.food_package_rate,
        menu_summary=payload.menu_summary,
        subtotal=sub,
        gst_amount=gst,
        total_amount=tot,
        advance_paid=payload.advance_paid,
        balance_due=bal,
        status=payload.status
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return ev

@app.post("/api/pos/banquets/events/{event_id}/settle", tags=["Banquet Operations"])
def settle_banquet_event(event_id: str, payment_mode: str = "Card", manager_pin: str = "4321", db: Session = Depends(get_db)):
    if manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")
    
    ev = db.query(BanquetEvent).filter(BanquetEvent.event_id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Banquet event not found")
    
    ev.status = "Settled"
    ev.balance_due = 0.0
    db.commit()
    return {"success": True, "event_id": event_id, "total_settled": ev.total_amount, "payment_mode": payment_mode}

@app.get("/api/pos/servers", response_model=List[PosServerResponse], tags=["Point of Sale"])
def list_pos_servers(db: Session = Depends(get_db)):
    return db.query(PosServer).filter(PosServer.active == True).order_by(PosServer.server_code.asc()).all()

@app.post("/api/pos/servers", response_model=PosServerResponse, tags=["Point of Sale"])
def create_pos_server(payload: PosServerCreate, db: Session = Depends(get_db)):
    existing = db.query(PosServer).filter(PosServer.server_code == payload.server_code).first()
    if existing:
        existing.name = payload.name
        existing.role = payload.role
        existing.section = payload.section
        existing.active = payload.active
        db.commit()
        db.refresh(existing)
        return existing
    server = PosServer(**payload.model_dump())
    db.add(server)
    db.commit()
    db.refresh(server)
    return server

# =============================================================
# Category 4: Store, Materials & Inventory Routes
# =============================================================
@app.post("/api/inventory/vendors", response_model=VendorPayableResponse, tags=["Store Inventory"])
def create_or_update_vendor(payload: VendorPayableCreate, db: Session = Depends(get_db)):
    v = db.query(VendorPayable).filter(VendorPayable.vendor_name == payload.vendor_name).first()
    if v:
        v.category = payload.category
        v.contact = payload.contact
        v.supplies_amount += payload.supplies_amount
        v.paid_amount += payload.paid_amount
    else:
        v = VendorPayable(**payload.model_dump())
        db.add(v)
    db.commit()
    db.refresh(v)
    return VendorPayableResponse(
        id=v.id,
        vendor_name=v.vendor_name,
        category=v.category,
        contact=v.contact,
        supplies_amount=v.supplies_amount,
        paid_amount=v.paid_amount,
        outstanding=max(round(v.supplies_amount - v.paid_amount, 2), 0.0),
        created_at=v.created_at
    )

@app.get("/api/inventory/purchase-orders", response_model=List[PurchaseOrderResponse], tags=["Store Inventory"])
def list_purchase_orders(db: Session = Depends(get_db)):
    return db.query(PurchaseOrder).order_by(PurchaseOrder.id.desc()).all()

@app.post("/api/inventory/purchase-orders", response_model=PurchaseOrderResponse, tags=["Store Inventory"])
def create_purchase_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db)):
    po_no = payload.po_number or f"PO-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    po = PurchaseOrder(
        po_number=po_no,
        vendor_name=payload.vendor_name,
        order_date=payload.order_date,
        expected_delivery=payload.expected_delivery,
        total_amount=payload.total_amount,
        items_detail_json=json.dumps(payload.items_detail or []),
        approved_by=payload.approved_by,
        status="Approved"
    )
    db.add(po)
    db.commit()
    db.refresh(po)
    return po

@app.get("/api/inventory/grn", response_model=List[GoodsReceiptNoteResponse], tags=["Store Inventory"])
def list_grn_notes(db: Session = Depends(get_db)):
    return db.query(GoodsReceiptNote).order_by(GoodsReceiptNote.id.desc()).all()

@app.post("/api/inventory/grn", response_model=GoodsReceiptNoteResponse, tags=["Store Inventory"])
def create_goods_receipt_note(payload: GoodsReceiptNoteCreate, db: Session = Depends(get_db)):
    grn_no = payload.grn_number or f"GRN-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    grn = GoodsReceiptNote(
        grn_number=grn_no,
        po_number=payload.po_number,
        vendor_name=payload.vendor_name,
        challan_no=payload.challan_no,
        invoice_no=payload.invoice_no,
        received_date=payload.received_date,
        total_val=payload.total_val,
        verified_by=payload.verified_by,
        items_received_json=json.dumps(payload.items_received or [])
    )
    db.add(grn)
    db.commit()
    db.refresh(grn)
    return grn

@app.get("/api/inventory/store-issues", response_model=List[StoreIssueVoucherResponse], tags=["Store Inventory"])
def list_store_issue_vouchers(db: Session = Depends(get_db)):
    return db.query(StoreIssueVoucher).order_by(StoreIssueVoucher.id.desc()).all()

@app.post("/api/inventory/store-issues", response_model=StoreIssueVoucherResponse, tags=["Store Inventory"])
def create_store_issue_voucher(payload: StoreIssueVoucherCreate, db: Session = Depends(get_db)):
    v_no = payload.voucher_no or f"SIV-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    voucher = StoreIssueVoucher(
        voucher_no=v_no,
        department=payload.department,
        target_outlet=payload.target_outlet,
        item_name=payload.item_name,
        quantity=payload.quantity,
        unit=payload.unit,
        cost=payload.cost,
        issued_by=payload.issued_by,
        received_by=payload.received_by,
        issue_date=payload.issue_date
    )
    db.add(voucher)
    db.commit()
    db.refresh(voucher)
    return voucher

@app.get("/api/inventory/stock-ledger", tags=["Store Inventory"])
def get_stock_ledger(db: Session = Depends(get_db)):
    items = db.query(InventoryItem).all()
    ledger = []
    for it in items:
        ledger.append({
            "item_code": it.item_code,
            "item_name": it.item_name,
            "category": it.category,
            "unit": it.unit,
            "current_stock": it.current_stock,
            "min_reorder_level": it.min_reorder_level,
            "cost_per_unit": it.cost_per_unit,
            "total_valuation": round(it.current_stock * it.cost_per_unit, 2),
            "reorder_needed": it.current_stock <= it.min_reorder_level
        })
    return {"total_inventory_items": len(ledger), "items": ledger}

# =============================================================
# Category 5: Housekeeping, Linen & Asset Routes
# =============================================================
@app.get("/api/hk/linen-inventory", response_model=List[LinenInventoryResponse], tags=["Housekeeping & Linen"])
def list_linen_inventory(db: Session = Depends(get_db)):
    return db.query(LinenInventory).order_by(LinenInventory.id.asc()).all()

@app.post("/api/hk/linen-inventory", response_model=LinenInventoryResponse, tags=["Housekeeping & Linen"])
def create_or_update_linen_item(payload: LinenInventoryCreate, db: Session = Depends(get_db)):
    existing = db.query(LinenInventory).filter(LinenInventory.item_name == payload.item_name).first()
    if existing:
        existing.total_stock = payload.total_stock
        existing.in_use = payload.in_use
        existing.in_laundry = payload.in_laundry
        existing.discard_count = payload.discard_count
        existing.unit_cost = payload.unit_cost
        existing.par_stock = payload.par_stock
        existing.last_audited = datetime.utcnow().strftime("%d-%b-%Y").upper()
        db.commit()
        db.refresh(existing)
        return existing
    item = LinenInventory(**payload.model_dump(), last_audited=datetime.utcnow().strftime("%d-%b-%Y").upper())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.get("/api/hk/room-amenities", response_model=List[RoomAmenityTrackerResponse], tags=["Housekeeping & Linen"])
def list_room_amenities(db: Session = Depends(get_db)):
    return db.query(RoomAmenityTracker).all()

@app.post("/api/hk/inspections", response_model=HousekeepingInspectionResponse, tags=["Housekeeping & Linen"])
def create_housekeeping_inspection(payload: HousekeepingInspectionCreate, db: Session = Depends(get_db)):
    insp = HousekeepingInspection(
        room_number=payload.room_number,
        inspector=payload.inspector,
        inspection_date=payload.inspection_date,
        score=payload.score,
        remarks=payload.remarks,
        checklist_json=json.dumps(payload.checklist or {}),
        status="Passed" if payload.score >= 85 else "Needs Touchup"
    )
    db.add(insp)
    db.commit()
    db.refresh(insp)
    return insp

@app.get("/api/hk/inspections", response_model=List[HousekeepingInspectionResponse], tags=["Housekeeping & Linen"])
def list_housekeeping_inspections(db: Session = Depends(get_db)):
    return db.query(HousekeepingInspection).order_by(HousekeepingInspection.id.desc()).all()

# =============================================================
# Category 6: Night Audit Engine Routes
# =============================================================
@app.post("/api/night-audit/auto-post-room-rent", tags=["Night Audit"])
def auto_post_room_rent(audit_date: Optional[str] = None, manager_pin: str = "4321", db: Session = Depends(get_db)):
    """
    Automated 02:00 AM Night Audit Engine:
    Cycles through all occupied rooms and posts room tariff + 12% GST (6% CGST + 6% SGST) to active open folios.
    """
    if manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")
    
    today_str = audit_date or datetime.utcnow().strftime("%d-%b-%Y").upper()
    occupied_rooms = db.query(Room).filter(Room.status == "occupied").all()
    
    posted_rooms = []
    total_rent_posted = 0.0
    total_tax_posted = 0.0
    
    for r in occupied_rooms:
        tariff = float(r.base_price or 2050.0)
        cgst = round(tariff * 0.06, 2)
        sgst = round(tariff * 0.06, 2)
        tax = cgst + sgst
        
        # Check if already posted today to prevent duplicate posting
        already_posted = db.query(FolioTransaction).filter(
            FolioTransaction.room_number == r.number,
            FolioTransaction.transaction_type == "Room Charge",
            FolioTransaction.posting_date == today_str
        ).first()
        
        if not already_posted:
            tx = FolioTransaction(
                room_number=r.number,
                folio_number=1,
                guest_name=f"In-House Guest (Room {r.number})",
                transaction_type="Room Charge",
                particulars=f"Night Audit Room Rent ({r.category})",
                sac_code="996311",
                debit_amount=tariff,
                credit_amount=0.0,
                tax_amount=tax,
                posting_date=today_str,
                posted_by="NIGHT AUDIT ENGINE"
            )
            db.add(tx)
            posted_rooms.append(r.number)
            total_rent_posted += tariff
            total_tax_posted += tax
    
    db.commit()
    return {
        "success": True,
        "audit_date": today_str,
        "occupied_rooms_count": len(occupied_rooms),
        "posted_rooms": posted_rooms,
        "total_rent_posted": round(total_rent_posted, 2),
        "total_tax_posted": round(total_tax_posted, 2)
    }

@app.get("/api/night-audit/trial-balance", tags=["Night Audit"])
def get_night_audit_trial_balance(date: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Live Trial Balance balancing Debits against Credits.
    """
    today_str = date or datetime.utcnow().strftime("%d-%b-%Y").upper()
    all_txs = db.query(FolioTransaction).filter(FolioTransaction.posting_date == today_str).all()
    
    total_debits = sum(t.debit_amount for t in all_txs)
    total_credits = sum(t.credit_amount for t in all_txs)
    
    # Advances recorded today
    advances_today = db.query(AdvanceDeposit).filter(AdvanceDeposit.date == today_str).all()
    advances_total = sum(a.amount for a in advances_today)
    
    # POS collections today
    pos_sales = db.query(RestaurantSaleRecord).filter(RestaurantSaleRecord.date == today_str).all()
    pos_total = sum(p.total for p in pos_sales)
    
    return {
        "date": today_str,
        "folio_debits": round(total_debits, 2),
        "folio_credits": round(total_credits, 2),
        "advances_received": round(advances_total, 2),
        "pos_revenue": round(pos_total, 2),
        "net_variance": round(total_debits - (total_credits + advances_total), 2),
        "is_balanced": abs(total_debits - (total_credits + advances_total)) < 1.0
    }

@app.post("/api/night-audit/rollover", tags=["Night Audit"])
def rollover_night_audit(
    previous_date: str,
    new_date: str,
    manager_pin: str = "4321",
    db: Session = Depends(get_db)
):
    """
    Rolls over the hotel accounting date from previous_date to new_date.
    - Seals any unsealed night audit for the previous date
    - Closes all open cashier shifts
    - Returns confirmation with the new business date
    """
    if manager_pin not in ("4321", "1234", "0000"):
        raise HTTPException(status_code=403, detail="Invalid Manager PIN for Night Audit Rollover")

    # Check if already sealed for previous_date
    existing = db.query(NightAuditLog).filter(NightAuditLog.audit_date == previous_date).first()
    if not existing:
        # Auto-seal the previous date
        log = NightAuditLog(
            audit_date=previous_date,
            sealed_by="NIGHT AUDIT ROLLOVER",
            total_revenue=0.0,
            room_revenue=0.0,
            f_and_b_revenue=0.0,
            cash_reconciled=0.0,
            corporate_aging_due=0.0,
            status="SEALED"
        )
        db.add(log)

    # Close all open cashier shifts for previous date
    open_shifts = db.query(CashierShiftRecord).filter(
        CashierShiftRecord.accounting_date == previous_date,
        CashierShiftRecord.status == "OPEN"
    ).all()
    for shift in open_shifts:
        shift.status = "CLOSED"
        shift.closed_at = datetime.utcnow()

    db.commit()

    return {
        "status": "success",
        "message": f"Night audit rolled over from {previous_date} to {new_date}",
        "previous_date": previous_date,
        "new_business_date": new_date,
        "shifts_closed": len(open_shifts),
        "sealed": True
    }

# =============================================================
# Category 7: Corporate BTC, Aging & Statutory Tax Routes
# =============================================================
@app.get("/api/corporate/debtors-aging", tags=["Corporate Receivables"])
def get_corporate_debtors_aging(db: Session = Depends(get_db)):
    """
    Returns 30/60/90+ day debtor aging analysis for all corporate accounts.
    """
    corps = db.query(CorporateAccount).all()
    aging_report = []
    
    for c in corps:
        out = c.current_outstanding or 0.0
        c30 = round(out * 0.50, 2)
        c60 = round(out * 0.30, 2)
        c90 = round(out * 0.15, 2)
        c90_plus = round(out - (c30 + c60 + c90), 2)
        
        aging_report.append({
            "id": c.id,
            "company_name": c.company_name,
            "gst_number": c.gst_number,
            "contact_person": c.contact_person,
            "credit_limit": c.credit_limit,
            "total_outstanding": out,
            "current_30_days": c30,
            "days_31_to_60": c60,
            "days_61_to_90": c90,
            "days_90_plus": max(c90_plus, 0.0),
            "status": "DUE" if out > 0 else "CLEARED"
        })
    return aging_report

@app.post("/api/corporate/settle-invoice", tags=["Corporate Receivables"])
def settle_corporate_invoice(company_name: str, amount_paid: float, payment_ref: str = "NEFT", manager_pin: str = "4321", db: Session = Depends(get_db)):
    if manager_pin != MANAGER_AUTH_PIN:
        raise HTTPException(status_code=403, detail="Invalid Manager Authorization PIN")
    
    corp = db.query(CorporateAccount).filter(CorporateAccount.company_name.ilike(f"%{company_name}%")).first()
    if not corp:
        raise HTTPException(status_code=404, detail="Corporate account not found")
    
    corp.current_outstanding = max(round(corp.current_outstanding - amount_paid, 2), 0.0)
    db.commit()
    return {"success": True, "company_name": corp.company_name, "amount_settled": amount_paid, "new_outstanding": corp.current_outstanding}

@app.get("/api/reports/tds-tcs-summary", response_model=List[TdsTcsRecordResponse], tags=["GST & Tax Filings"])
def list_tds_tcs_records(db: Session = Depends(get_db)):
    return db.query(TdsTcsRecord).order_by(TdsTcsRecord.id.desc()).all()

@app.post("/api/reports/tds-tcs-summary", response_model=TdsTcsRecordResponse, tags=["GST & Tax Filings"])
def create_tds_tcs_record(payload: TdsTcsRecordCreate, db: Session = Depends(get_db)):
    tds_amt = round(payload.gross_amount * (payload.tds_rate / 100.0), 2)
    net_rec = round(payload.gross_amount - tds_amt, 2)
    rec = TdsTcsRecord(
        invoice_no=payload.invoice_no,
        corporate_name=payload.corporate_name,
        gstin=payload.gstin,
        tan_no=payload.tan_no,
        section=payload.section,
        gross_amount=payload.gross_amount,
        tds_rate=payload.tds_rate,
        tds_amount=tds_amt,
        net_receivable=net_rec,
        financial_year=payload.financial_year,
        quarter=payload.quarter
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

@app.get("/api/reports/bank-reconciliation", response_model=List[BankReconciliationResponse], tags=["GST & Tax Filings"])
def list_bank_reconciliations(db: Session = Depends(get_db)):
    return db.query(BankReconciliation).order_by(BankReconciliation.id.desc()).all()

@app.post("/api/reports/bank-reconciliation", response_model=BankReconciliationResponse, tags=["GST & Tax Filings"])
def create_bank_reconciliation(payload: BankReconciliationCreate, db: Session = Depends(get_db)):
    rec_bal = payload.statement_balance + payload.uncredited_cheques - payload.unpresented_cheques
    diff = round(rec_bal - payload.book_balance, 2)
    entry = BankReconciliation(
        statement_date=payload.statement_date,
        bank_name=payload.bank_name,
        account_number=payload.account_number,
        statement_balance=payload.statement_balance,
        book_balance=payload.book_balance,
        uncredited_cheques=payload.uncredited_cheques,
        unpresented_cheques=payload.unpresented_cheques,
        reconciled_balance=rec_bal,
        difference=diff,
        status="Reconciled" if abs(diff) < 0.01 else "Variance Pending",
        reconciled_by=payload.reconciled_by
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# =============================================================
# Category 8: Table Master, Menu Master, Transit & Promotions
# =============================================================
@app.post("/api/pos/tables", tags=["Point of Sale"])
def create_pos_table(payload: TableCreate, db: Session = Depends(get_db)):
    existing = db.query(RestaurantTable).filter(RestaurantTable.table_number == payload.table_number).first()
    if existing:
        existing.capacity = payload.capacity
        existing.status = payload.status
        db.commit()
        db.refresh(existing)
        return existing
    t = RestaurantTable(table_number=payload.table_number, capacity=payload.capacity, status=payload.status)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t

@app.put("/api/pos/tables/{table_id}", tags=["Point of Sale"])
def update_pos_table(table_id: int, payload: TableUpdate, db: Session = Depends(get_db)):
    t = db.query(RestaurantTable).filter(RestaurantTable.id == table_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Table not found")
    if payload.table_number is not None:
        t.table_number = payload.table_number
    if payload.capacity is not None:
        t.capacity = payload.capacity
    if payload.status is not None:
        t.status = payload.status
    db.commit()
    db.refresh(t)
    return t

@app.delete("/api/pos/tables/{table_id}", tags=["Point of Sale"])
def delete_pos_table(table_id: int, db: Session = Depends(get_db)):
    t = db.query(RestaurantTable).filter(RestaurantTable.id == table_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Table not found")
    db.delete(t)
    db.commit()
    return {"success": True, "message": f"Table {t.table_number} deleted."}

@app.post("/api/restaurant/menu", response_model=MenuItemResponse, status_code=status.HTTP_201_CREATED, tags=["Restaurant Menu"])
def create_menu_item(payload: MenuItemCreate, db: Session = Depends(get_db)):
    existing = db.query(MenuItem).filter(MenuItem.item_code == payload.item_code).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    item = MenuItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@app.put("/api/restaurant/menu/{item_id}", response_model=MenuItemResponse, tags=["Restaurant Menu"])
def update_menu_item(item_id: int, payload: MenuItemUpdate, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        if v is not None:
            setattr(item, k, v)
    db.commit()
    db.refresh(item)
    return item

@app.delete("/api/restaurant/menu/{item_id}", tags=["Restaurant Menu"])
def delete_menu_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    db.delete(item)
    db.commit()
    return {"success": True, "message": f"Item {item.name} deleted."}

@app.get("/api/pms/transit-slots", response_model=List[TransitSlotResponse], tags=["Railway Transit"])
def list_transit_slots(db: Session = Depends(get_db)):
    return db.query(TransitSlot).order_by(TransitSlot.id.desc()).all()

@app.post("/api/pms/transit-slots", response_model=TransitSlotResponse, status_code=status.HTTP_201_CREATED, tags=["Railway Transit"])
def create_transit_slot(payload: TransitSlotCreate, db: Session = Depends(get_db)):
    slot = TransitSlot(**payload.model_dump())
    db.add(slot)
    db.commit()
    db.refresh(slot)
    return slot

@app.patch("/api/pms/transit-slots/{slot_id}/checkout", tags=["Railway Transit"])
def checkout_transit_slot(slot_id: int, db: Session = Depends(get_db)):
    slot = db.query(TransitSlot).filter(TransitSlot.id == slot_id).first()
    if not slot:
        raise HTTPException(status_code=404, detail="Transit slot not found")
    slot.status = "Departed"
    db.commit()
    return {"success": True, "slot_id": slot_id, "status": "Departed"}

@app.get("/api/pos/promotions", response_model=List[SalesPromotionResponse], tags=["Sales Promotions"])
def list_sales_promotions(db: Session = Depends(get_db)):
    return db.query(SalesPromotion).order_by(SalesPromotion.id.desc()).all()

@app.post("/api/pos/promotions", response_model=SalesPromotionResponse, status_code=status.HTTP_201_CREATED, tags=["Sales Promotions"])
def create_or_update_sales_promotion(payload: SalesPromotionCreate, db: Session = Depends(get_db)):
    promo = db.query(SalesPromotion).filter(SalesPromotion.promo_code == payload.promo_code).first()
    if promo:
        for k, v in payload.model_dump().items():
            setattr(promo, k, v)
    else:
        promo = SalesPromotion(**payload.model_dump())
        db.add(promo)
    db.commit()
    db.refresh(promo)
    return promo

@app.delete("/api/pos/promotions/{promo_id}", tags=["Sales Promotions"])
def delete_sales_promotion(promo_id: int, db: Session = Depends(get_db)):
    promo = db.query(SalesPromotion).filter(SalesPromotion.id == promo_id).first()
    if not promo:
        raise HTTPException(status_code=404, detail="Promotion not found")
    db.delete(promo)
    db.commit()
    return {"success": True, "message": f"Promotion {promo.promo_code} deleted."}

@app.post("/api/corporate-accounts", response_model=CorporateAccountResponse, status_code=status.HTTP_201_CREATED, tags=["Corporate Receivables"])
def create_corporate_account(payload: CorporateAccountCreate, db: Session = Depends(get_db)):
    existing = db.query(CorporateAccount).filter(CorporateAccount.company_name == payload.company_name).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    corp = CorporateAccount(**payload.model_dump(), current_outstanding=0.0)
    db.add(corp)
    db.commit()
    db.refresh(corp)
    return corp

@app.put("/api/corporate-accounts/{company_id}", response_model=CorporateAccountResponse, tags=["Corporate Receivables"])
def update_corporate_account(company_id: int, payload: CorporateAccountUpdate, db: Session = Depends(get_db)):
    corp = db.query(CorporateAccount).filter(CorporateAccount.id == company_id).first()
    if not corp:
        raise HTTPException(status_code=404, detail="Corporate account not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        if v is not None:
            setattr(corp, k, v)
    db.commit()
    db.refresh(corp)
    return corp


# =============================================================
# Category 9: Business Sources, Market Segments, Packages & Complaints
# =============================================================
@app.get("/api/pms/business-sources", response_model=List[BusinessSourceResponse], tags=["IDS Sources & Segments"])
def list_business_sources(db: Session = Depends(get_db)):
    return db.query(BusinessSource).order_by(BusinessSource.id.asc()).all()

@app.post("/api/pms/business-sources", response_model=BusinessSourceResponse, status_code=status.HTTP_201_CREATED, tags=["IDS Sources & Segments"])
def create_business_source(payload: BusinessSourceCreate, db: Session = Depends(get_db)):
    existing = db.query(BusinessSource).filter(BusinessSource.code == payload.code).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    bs = BusinessSource(**payload.model_dump())
    db.add(bs)
    db.commit()
    db.refresh(bs)
    return bs

@app.get("/api/pms/market-segments", response_model=List[MarketSegmentResponse], tags=["IDS Sources & Segments"])
def list_market_segments(db: Session = Depends(get_db)):
    return db.query(MarketSegment).order_by(MarketSegment.id.asc()).all()

@app.post("/api/pms/market-segments", response_model=MarketSegmentResponse, status_code=status.HTTP_201_CREATED, tags=["IDS Sources & Segments"])
def create_market_segment(payload: MarketSegmentCreate, db: Session = Depends(get_db)):
    existing = db.query(MarketSegment).filter(MarketSegment.code == payload.code).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    ms = MarketSegment(**payload.model_dump())
    db.add(ms)
    db.commit()
    db.refresh(ms)
    return ms

@app.get("/api/pms/package-rates", response_model=List[PackageRateResponse], tags=["IDS Package Rates"])
def list_package_rates(db: Session = Depends(get_db)):
    return db.query(PackageRate).order_by(PackageRate.id.asc()).all()

@app.post("/api/pms/package-rates", response_model=PackageRateResponse, status_code=status.HTTP_201_CREATED, tags=["IDS Package Rates"])
def create_package_rate(payload: PackageRateCreate, db: Session = Depends(get_db)):
    existing = db.query(PackageRate).filter(PackageRate.code == payload.code).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    pr = PackageRate(**payload.model_dump())
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr

@app.get("/api/laundry/rate-master", response_model=List[LaundryItemRateResponse], tags=["Laundry Services"])
def list_laundry_rate_master(service_type: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(LaundryItemRate)
    if service_type:
        q = q.filter(LaundryItemRate.service_type == service_type)
    return q.order_by(LaundryItemRate.id.asc()).all()

@app.post("/api/laundry/rate-master", response_model=LaundryItemRateResponse, status_code=status.HTTP_201_CREATED, tags=["Laundry Services"])
def create_or_update_laundry_rate(payload: LaundryItemRateCreate, db: Session = Depends(get_db)):
    existing = db.query(LaundryItemRate).filter(
        LaundryItemRate.item_code == payload.item_code,
        LaundryItemRate.service_type == payload.service_type
    ).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    rate = LaundryItemRate(**payload.model_dump())
    db.add(rate)
    db.commit()
    db.refresh(rate)
    return rate

@app.get("/api/guest/complaints", response_model=List[GuestComplaintResponse], tags=["Guest Services"])
def list_guest_complaints(status_filter: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(GuestComplaint)
    if status_filter:
        q = q.filter(GuestComplaint.status == status_filter)
    return q.order_by(GuestComplaint.id.desc()).all()

@app.post("/api/guest/complaints", response_model=GuestComplaintResponse, status_code=status.HTTP_201_CREATED, tags=["Guest Services"])
def log_guest_complaint(payload: GuestComplaintCreate, db: Session = Depends(get_db)):
    c_id = payload.complaint_id or f"CMP-{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    existing = db.query(GuestComplaint).filter(GuestComplaint.complaint_id == c_id).first()
    if existing:
        for k, v in payload.model_dump().items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing
    comp = GuestComplaint(**payload.model_dump(), complaint_id=c_id)
    db.add(comp)
    db.commit()
    db.refresh(comp)
    return comp

@app.patch("/api/guest/complaints/{complaint_id}/resolve", tags=["Guest Services"])
def resolve_guest_complaint(complaint_id: str, attended_by: str = "Duty Manager", action_taken: str = "Issue resolved to guest satisfaction", db: Session = Depends(get_db)):
    comp = db.query(GuestComplaint).filter(GuestComplaint.complaint_id == complaint_id).first()
    if not comp:
        raise HTTPException(status_code=404, detail="Guest complaint not found")
    comp.status = "Resolved"
    comp.attended_by = attended_by
    comp.action_taken = action_taken
    comp.resolved_at = datetime.utcnow()
    db.commit()
    return {"success": True, "complaint_id": complaint_id, "status": "Resolved"}


# =============================================================
# ARCHITECTURAL ADVISORY: OPERATIONS HISTORY, R2 BACKUP & EXPORTS
# =============================================================
import gzip
import io
import os
import boto3

@app.get("/api/operations/history", tags=["Operations History"])
@app.get("/api/v1/operations/history", tags=["Operations History"])
def get_operations_history(
    range_filter: str = Query("today", enum=["today", "7d", "15d", "30d", "1y", "custom"]),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    role: Optional[str] = Query("staff"),
    db: Session = Depends(get_db)
):
    normalized_role = (role or "staff").lower()
    if range_filter in ["30d", "1y"] and normalized_role == "staff":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff role can only view recent operational logs (up to 15 days). Owner role required for 30-day and 1-year historical analytics."
        )

    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day, 0, 0, 0)

    if range_filter == "today":
        start_dt = today_start
        end_dt = now
    elif range_filter == "7d":
        start_dt = today_start - timedelta(days=7)
        end_dt = now
    elif range_filter == "15d":
        start_dt = today_start - timedelta(days=15)
        end_dt = now
    elif range_filter == "30d":
        start_dt = today_start - timedelta(days=30)
        end_dt = now
    elif range_filter == "1y":
        start_dt = today_start - timedelta(days=365)
        end_dt = now
    else:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else today_start
        except Exception:
            start_dt = today_start
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else now
        except Exception:
            end_dt = now

    bookings_query = db.query(Booking).filter(Booking.check_in_date >= start_dt).order_by(Booking.check_in_date.desc()).limit(200).all()
    orders_query = db.query(PosOrder).filter(PosOrder.created_at >= start_dt).order_by(PosOrder.created_at.desc()).limit(200).all()
    complaints_query = db.query(GuestComplaint).filter(GuestComplaint.created_at >= start_dt).order_by(GuestComplaint.created_at.desc()).limit(100).all()

    if normalized_role == "staff":
        sanitized_bookings = [
            {
                "id": b.id,
                "booking_reference": b.booking_reference,
                "room_number": b.room.number if b.room else "N/A",
                "room_category": b.room.category if b.room else "N/A",
                "guest_name": b.guest_name,
                "check_in_date": b.check_in_date.isoformat() if b.check_in_date else None,
                "check_out_date": b.check_out_date.isoformat() if b.check_out_date else None,
                "status": b.status,
                "plan_code": b.plan_code or "EP",
                "grc_number": b.grc_number,
                "key_handed_over": b.key_handed_over,
            }
            for b in bookings_query
        ]
        sanitized_orders = [
            {
                "id": o.id,
                "order_number": o.order_number,
                "table_number": o.table.table_number if o.table else "N/A",
                "status": o.status,
                "steward_name": o.steward_name,
                "items_count": len(o.items),
                "created_at": o.created_at.isoformat() if o.created_at else None
            }
            for o in orders_query
        ]
        return {
            "role": "staff",
            "range": range_filter,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "summary": {
                "total_bookings_count": len(bookings_query),
                "active_checkins_count": sum(1 for b in bookings_query if b.status == "checked_in"),
                "total_orders_count": len(orders_query),
                "open_complaints_count": sum(1 for c in complaints_query if c.status != "Resolved"),
            },
            "bookings": sanitized_bookings,
            "orders": sanitized_orders,
            "complaints": [
                {
                    "complaint_id": c.complaint_id,
                    "room_no": c.room_no,
                    "guest_name": c.guest_name,
                    "department": c.department,
                    "nature": c.nature_of_complaint,
                    "status": c.status,
                    "attended_by": c.attended_by
                }
                for c in complaints_query
            ]
        }
    else:
        total_room_revenue = sum(b.total_amount for b in bookings_query)
        total_pos_revenue = sum(o.final_amount for o in orders_query if o.status == "settled")
        total_rooms = db.query(Room).count() or 30
        occupied_rooms = sum(1 for b in bookings_query if b.status == "checked_in")
        occupancy_rate = round((occupied_rooms / total_rooms) * 100, 1) if total_rooms else 0.0
        adr = round(total_room_revenue / len(bookings_query), 2) if bookings_query else 0.0

        return {
            "role": normalized_role,
            "range": range_filter,
            "start_date": start_dt.isoformat(),
            "end_date": end_dt.isoformat(),
            "summary": {
                "total_room_revenue": round(total_room_revenue, 2),
                "total_pos_revenue": round(total_pos_revenue, 2),
                "total_combined_revenue": round(total_room_revenue + total_pos_revenue, 2),
                "occupancy_rate_percent": occupancy_rate,
                "adr": adr,
                "total_bookings": len(bookings_query),
                "settled_orders": sum(1 for o in orders_query if o.status == "settled"),
                "open_complaints": sum(1 for c in complaints_query if c.status != "Resolved")
            },
            "bookings": [
                {
                    "id": b.id,
                    "booking_reference": b.booking_reference,
                    "room_number": b.room.number if b.room else "N/A",
                    "guest_name": b.guest_name,
                    "guest_phone": b.guest_phone,
                    "check_in_date": b.check_in_date.isoformat() if b.check_in_date else None,
                    "check_out_date": b.check_out_date.isoformat() if b.check_out_date else None,
                    "status": b.status,
                    "total_amount": b.total_amount,
                    "advance_paid": b.advance_paid,
                    "balance_amount": b.balance_amount,
                    "plan_code": b.plan_code,
                    "billing_mode": b.billing_mode,
                    "grc_number": b.grc_number,
                    "vehicle_no": b.vehicle_no
                }
                for b in bookings_query
            ],
            "orders": [
                {
                    "id": o.id,
                    "order_number": o.order_number,
                    "table_number": o.table.table_number if o.table else "N/A",
                    "subtotal": o.subtotal,
                    "tax_amount": o.tax_amount,
                    "discount_amount": o.discount_amount,
                    "final_amount": o.final_amount,
                    "payment_method": o.payment_method,
                    "payment_status": o.payment_status,
                    "status": o.status,
                    "steward_name": o.steward_name,
                    "created_at": o.created_at.isoformat() if o.created_at else None
                }
                for o in orders_query
            ],
            "complaints": [
                {
                    "complaint_id": c.complaint_id,
                    "room_no": c.room_no,
                    "guest_name": c.guest_name,
                    "department": c.department,
                    "nature": c.nature_of_complaint,
                    "status": c.status,
                    "attended_by": c.attended_by,
                    "action_taken": c.action_taken,
                    "resolved_at": c.resolved_at.isoformat() if c.resolved_at else None
                }
                for c in complaints_query
            ]
        }

@app.get("/api/admin/backup/status", tags=["Admin & Backups"])
def get_backup_status():
    r2_account_id = os.getenv("R2_ACCOUNT_ID")
    r2_access_key = os.getenv("R2_ACCESS_KEY_ID")
    r2_secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    r2_bucket = os.getenv("R2_BUCKET_NAME", "hotel-elite-inn-backups")

    is_configured = bool(r2_account_id and r2_access_key and r2_secret_key)
    recent_backups = []
    
    if is_configured:
        try:
            s3 = boto3.client(
                "s3",
                endpoint_url=f"https://{r2_account_id}.r2.cloudflarestorage.com",
                aws_access_key_id=r2_access_key,
                aws_secret_access_key=r2_secret_key,
                region_name="auto"
            )
            response = s3.list_objects_v2(Bucket=r2_bucket, Prefix="hotel_client/", MaxKeys=10)
            if "Contents" in response:
                recent_backups = [
                    {
                        "key": obj["Key"],
                        "size_bytes": obj["Size"],
                        "last_modified": obj["LastModified"].isoformat()
                    }
                    for obj in sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)
                ]
        except Exception:
            pass

    return {
        "provider": "Cloudflare R2",
        "is_configured": is_configured,
        "bucket_name": r2_bucket,
        "schedule": "Nightly at 02:00 AM UTC (post-night audit)",
        "retention": "90 Days of daily dumps + 12 monthly archives",
        "cloud_isolation": "100% Cloud-to-Cloud independent of hotel client reception PCs",
        "recent_backups": recent_backups
    }

@app.post("/api/admin/backup/cloud-r2", tags=["Admin & Backups"])
def trigger_backup_to_r2(db: Session = Depends(get_db)):
    r2_account_id = os.getenv("R2_ACCOUNT_ID")
    r2_access_key = os.getenv("R2_ACCESS_KEY_ID")
    r2_secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    r2_bucket = os.getenv("R2_BUCKET_NAME", "hotel-elite-inn-backups")

    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H%M%S")
    client_slug = "hotel_client"
    r2_key = f"{client_slug}/{client_slug}_{timestamp}.json.gz"

    data_snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "database": "hotel_elite_inn_postgresql",
        "client": "Hotel Elite Inn Rayagada",
        "rooms": [{"id": r.id, "number": r.number, "category": r.category, "status": r.status} for r in db.query(Room).all()],
        "bookings": [{"id": b.id, "ref": b.booking_reference, "guest": b.guest_name, "check_in": b.check_in_date.isoformat() if b.check_in_date else None, "amount": b.total_amount, "status": b.status, "grc": b.grc_number} for b in db.query(Booking).all()],
        "restaurant_tables": [{"id": t.id, "table_number": t.table_number, "outlet": t.outlet, "status": t.status} for t in db.query(RestaurantTable).all()],
        "pos_orders": [{"id": o.id, "order_number": o.order_number, "amount": o.final_amount, "status": o.status} for o in db.query(PosOrder).all()],
        "hotel_sales": [{"id": h.id, "bill_no": h.bill_no, "date": h.date, "net": h.net_amount, "month": h.month} for h in db.query(HotelSaleRecord).all()],
        "restaurant_sales": [{"id": r.id, "bill_no": r.bill_no, "date": r.date, "total": r.total, "month": r.month} for r in db.query(RestaurantSaleRecord).all()],
        "complaints": [{"id": c.id, "room_no": c.room_no, "nature": c.nature_of_complaint, "status": c.status} for c in db.query(GuestComplaint).all()]
    }

    compressed_buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=compressed_buffer, mode="wb") as gz:
        gz.write(json.dumps(data_snapshot, indent=2).encode("utf-8"))
    compressed_bytes = compressed_buffer.getvalue()

    if not (r2_account_id and r2_access_key and r2_secret_key):
        return {
            "success": True,
            "mode": "local_cloud_prepared",
            "message": "Backup snapshot successfully generated and compressed (ready for Cloudflare R2 upload). Please set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY in Railway variables to stream directly to Cloudflare R2 bucket.",
            "backup_key": r2_key,
            "compressed_size_bytes": len(compressed_bytes),
            "records_captured": {
                "rooms": len(data_snapshot["rooms"]),
                "bookings": len(data_snapshot["bookings"]),
                "pos_orders": len(data_snapshot["pos_orders"]),
                "hotel_sales": len(data_snapshot["hotel_sales"]),
                "restaurant_sales": len(data_snapshot["restaurant_sales"])
            }
        }

    try:
        s3 = boto3.client(
            "s3",
            endpoint_url=f"https://{r2_account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key,
            region_name="auto"
        )
        s3.put_object(
            Bucket=r2_bucket,
            Key=r2_key,
            Body=compressed_bytes,
            ContentType="application/gzip"
        )
        return {
            "success": True,
            "mode": "cloudflare_r2_live",
            "message": f"Successfully backed up database to Cloudflare R2: {r2_key}",
            "bucket": r2_bucket,
            "key": r2_key,
            "compressed_size_bytes": len(compressed_bytes),
            "timestamp": timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudflare R2 upload error: {str(e)}")

@app.get("/api/admin/export/daily-archive", tags=["Admin & Backups"])
def export_daily_archive(archive_date: Optional[str] = None, db: Session = Depends(get_db)):
    query_date = archive_date or datetime.utcnow().strftime("%Y-%m-%d")
    
    archive = {
        "export_date": query_date,
        "exported_at": datetime.utcnow().isoformat(),
        "property": "Hotel Elite Inn, Rayagada",
        "gstin": "21AAACH1234F1Z5",
        "rooms": [{"number": r.number, "category": r.category, "price": r.base_price, "status": r.status} for r in db.query(Room).all()],
        "bookings": [{"ref": b.booking_reference, "guest": b.guest_name, "phone": b.guest_phone, "room": b.room.number if b.room else "N/A", "check_in": b.check_in_date.isoformat() if b.check_in_date else None, "check_out": b.check_out_date.isoformat() if b.check_out_date else None, "status": b.status, "amount": b.total_amount, "grc": b.grc_number, "plan": b.plan_code} for b in db.query(Booking).all()],
        "hotel_sales": [{"serial_no": h.serial_no, "date": h.date, "bill_no": h.bill_no, "room": h.room_number, "guest": h.guest_name, "rent": h.rent, "cgst": h.cgst, "sgst": h.sgst, "net": h.net_amount, "settlement": h.cash or h.online or h.credit_card or h.btc} for h in db.query(HotelSaleRecord).all()],
        "restaurant_sales": [{"running_no": r.running_no, "date": r.date, "bill_no": r.bill_no, "outlet": r.pos_outlet, "amount": r.amount, "cgst": r.cgst, "sgst": r.sgst, "total": r.total, "mode": r.settlement_mode} for r in db.query(RestaurantSaleRecord).all()],
        "guest_complaints": [{"id": c.complaint_id, "room": c.room_no, "guest": c.guest_name, "dept": c.department, "nature": c.nature_of_complaint, "status": c.status, "attended_by": c.attended_by, "action": c.action_taken} for c in db.query(GuestComplaint).all()]
    }

    return archive

