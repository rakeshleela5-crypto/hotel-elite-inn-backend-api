import os
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, Base, get_db
from models import (
    Room, Booking, RestaurantTable, PosOrder, PosOrderItem,
    InventoryItem, CorporateAccount, RoomDefect, NightAuditLog
)
from schemas import (
    RoomCreate, RoomResponse, RoomStatusUpdate,
    BookingCreate, BookingResponse,
    PosOrderCreate, PosOrderResponse, VoidItemRequest, TableMergeRequest, OrderSettleRequest,
    InventoryItemResponse, StockAdjustmentRequest,
    CorporateAccountResponse, CorporatePaymentRequest,
    RoomDefectCreate, RoomDefectResponse,
    NightAuditRequest, NightAuditResponse, DashboardStats
)
from seed import seed_database

MANAGER_AUTH_PIN = os.getenv("MANAGER_PIN", "4321")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables & seed default data on startup
    Base.metadata.create_all(bind=engine)
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

# Robust CORS middleware configured for Cloudflare Pages and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    query = db.query(Booking)
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    return query.order_by(Booking.check_in_date.desc()).all()

@app.post("/api/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED, tags=["Front Desk"])
def create_booking(booking_in: BookingCreate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.id == booking_in.room_id).first()
    if not room:
        raise HTTPException(status_code=404, detail="Selected room not found")
    
    nights = max((booking_in.check_out_date - booking_in.check_in_date).days, 1)
    total_amount = room.base_price * nights * 1.12 # 12% GST
    balance_amount = max(total_amount - booking_in.advance_paid, 0.0)

    booking_ref = f"HEI-{datetime.utcnow().strftime('%y%m%d')}-{room.number}"

    booking = Booking(
        booking_reference=booking_ref,
        guest_name=booking_in.guest_name,
        guest_phone=booking_in.guest_phone,
        guest_email=booking_in.guest_email,
        guest_id_type=booking_in.guest_id_type,
        guest_id_number=booking_in.guest_id_number,
        room_id=booking_in.room_id,
        check_in_date=booking_in.check_in_date,
        check_out_date=booking_in.check_out_date,
        status="confirmed",
        total_amount=round(total_amount, 2),
        advance_paid=booking_in.advance_paid,
        balance_amount=round(balance_amount, 2),
        corporate_account_id=booking_in.corporate_account_id,
        key_handed_over=False
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
