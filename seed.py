from datetime import datetime
from database import SessionLocal, engine, Base
from models import (
    Room, RestaurantTable, InventoryItem, CorporateAccount, RoomDefect
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Rooms if empty
        if db.query(Room).count() == 0:
            rooms_data = [
                # First Floor
                {"number": "101", "category": "Deluxe Room", "base_price": 2499.0, "floor": 1, "status": "clean"},
                {"number": "102", "category": "Deluxe Room", "base_price": 2499.0, "floor": 1, "status": "occupied"},
                {"number": "103", "category": "Super Deluxe", "base_price": 3299.0, "floor": 1, "status": "clean"},
                {"number": "104", "category": "Super Deluxe", "base_price": 3299.0, "floor": 1, "status": "maintenance"},
                {"number": "105", "category": "Executive Suite", "base_price": 4499.0, "floor": 1, "status": "occupied"},
                {"number": "106", "category": "Executive Suite", "base_price": 4499.0, "floor": 1, "status": "clean"},
                {"number": "107", "category": "Deluxe Room", "base_price": 2499.0, "floor": 1, "status": "dirty"},
                {"number": "108", "category": "Super Deluxe", "base_price": 3299.0, "floor": 1, "status": "clean"},
                # Second Floor
                {"number": "201", "category": "Deluxe Room", "base_price": 2499.0, "floor": 2, "status": "clean"},
                {"number": "202", "category": "Deluxe Room", "base_price": 2499.0, "floor": 2, "status": "clean"},
                {"number": "203", "category": "Super Deluxe", "base_price": 3299.0, "floor": 2, "status": "occupied"},
                {"number": "204", "category": "Super Deluxe", "base_price": 3299.0, "floor": 2, "status": "clean"},
                {"number": "205", "category": "Executive Suite", "base_price": 4499.0, "floor": 2, "status": "clean"},
                {"number": "206", "category": "Executive Suite", "base_price": 4499.0, "floor": 2, "status": "occupied"},
                {"number": "207", "category": "Deluxe Room", "base_price": 2499.0, "floor": 2, "status": "dirty"},
                {"number": "208", "category": "Super Deluxe", "base_price": 3299.0, "floor": 2, "status": "clean"},
                # Third Floor
                {"number": "301", "category": "Deluxe Room", "base_price": 2499.0, "floor": 3, "status": "clean"},
                {"number": "302", "category": "Deluxe Room", "base_price": 2499.0, "floor": 3, "status": "clean"},
                {"number": "303", "category": "Super Deluxe", "base_price": 3299.0, "floor": 3, "status": "clean"},
                {"number": "304", "category": "Super Deluxe", "base_price": 3299.0, "floor": 3, "status": "clean"},
                {"number": "305", "category": "Executive Suite", "base_price": 4499.0, "floor": 3, "status": "clean"},
                {"number": "306", "category": "Executive Suite", "base_price": 4499.0, "floor": 3, "status": "clean"},
                {"number": "307", "category": "Deluxe Room", "base_price": 2499.0, "floor": 3, "status": "clean"},
                {"number": "308", "category": "Executive Suite", "base_price": 4499.0, "floor": 3, "status": "clean"},
            ]
            for r in rooms_data:
                db.add(Room(**r))
            print(f"✓ Seeded {len(rooms_data)} Hotel Rooms.")

        # 2. Seed Restaurant Tables if empty
        if db.query(RestaurantTable).count() == 0:
            tables_data = [
                {"table_number": "T-1", "capacity": 4, "status": "occupied"},
                {"table_number": "T-2", "capacity": 2, "status": "available"},
                {"table_number": "T-3", "capacity": 4, "status": "occupied"},
                {"table_number": "T-4", "capacity": 6, "status": "available"},
                {"table_number": "T-5", "capacity": 4, "status": "occupied"},
                {"table_number": "T-6", "capacity": 2, "status": "available"},
                {"table_number": "T-7", "capacity": 8, "status": "available"},
                {"table_number": "T-8", "capacity": 4, "status": "available"},
                {"table_number": "T-9", "capacity": 4, "status": "available"},
                {"table_number": "T-10", "capacity": 6, "status": "available"},
                {"table_number": "T-11", "capacity": 4, "status": "available"},
                {"table_number": "T-12", "capacity": 2, "status": "available"},
            ]
            for t in tables_data:
                db.add(RestaurantTable(**t))
            print(f"✓ Seeded {len(tables_data)} Restaurant Tables.")

        # 3. Seed Inventory Items if empty
        if db.query(InventoryItem).count() == 0:
            inventory_data = [
                {"item_code": "INV-RIC-01", "item_name": "Premium Basmati Rice", "category": "Kitchen Raw Food", "unit": "KG", "current_stock": 42.0, "min_reorder_level": 50.0, "cost_per_unit": 98.0},
                {"item_code": "INV-CHK-02", "item_name": "Fresh Andhra Chicken", "category": "Kitchen Raw Food", "unit": "KG", "current_stock": 18.5, "min_reorder_level": 25.0, "cost_per_unit": 220.0},
                {"item_code": "INV-OIL-03", "item_name": "Refined Sunflower Oil", "category": "Kitchen Raw Food", "unit": "Ltr", "current_stock": 14.0, "min_reorder_level": 30.0, "cost_per_unit": 135.0},
                {"item_code": "INV-MLK-04", "item_name": "Fresh Dairy Milk (OMFED)", "category": "Dairy & Poultry", "unit": "Ltr", "current_stock": 28.0, "min_reorder_level": 15.0, "cost_per_unit": 54.0},
                {"item_code": "INV-PNR-05", "item_name": "Fresh Malai Paneer", "category": "Dairy & Poultry", "unit": "KG", "current_stock": 8.0, "min_reorder_level": 10.0, "cost_per_unit": 360.0},
                {"item_code": "INV-GAS-06", "item_name": "Commercial LPG 19KG Cylinder", "category": "Gas & Fuel", "unit": "Cylinders", "current_stock": 3.0, "min_reorder_level": 4.0, "cost_per_unit": 1850.0},
            ]
            for inv in inventory_data:
                db.add(InventoryItem(**inv))
            print(f"✓ Seeded {len(inventory_data)} Inventory Items.")

        # 4. Seed Corporate Accounts if empty
        if db.query(CorporateAccount).count() == 0:
            corporate_data = [
                {"company_name": "Ashok Leyland Logistics", "gst_number": "21AABCA1234F1Z1", "contact_person": "Sunil Mohanty (Fleet Mgr)", "contact_phone": "+91 94370 12345", "credit_limit": 150000.0, "current_outstanding": 64500.0, "billing_cycle_days": 30},
                {"company_name": "Utkal Alumina Int. Ltd (Aditya Birla)", "gst_number": "21AAACU4567G1Z8", "contact_person": "P. K. Verma (Admin VP)", "contact_phone": "+91 94371 98765", "credit_limit": 250000.0, "current_outstanding": 32400.0, "billing_cycle_days": 30},
                {"company_name": "Linde India Industrial Gases", "gst_number": "21AABCL7890H1Z3", "contact_person": "Ramesh Rao (Site Eng)", "contact_phone": "+91 98610 54321", "credit_limit": 100000.0, "current_outstanding": 38900.0, "billing_cycle_days": 15},
                {"company_name": "JK Paper Mills Ltd (Rayagada)", "gst_number": "21AAACJ1122K1Z9", "contact_person": "Corporate Accounts Desk", "contact_phone": "+91 6856 222000", "credit_limit": 300000.0, "current_outstanding": 0.0, "billing_cycle_days": 30},
            ]
            for corp in corporate_data:
                db.add(CorporateAccount(**corp))
            print(f"✓ Seeded {len(corporate_data)} Corporate Accounts.")

        # 5. Seed Room Defects if empty
        if db.query(RoomDefect).count() == 0:
            defects_data = [
                {"room_number": "104", "defect_type": "AC / Cooling Defect", "description": "Split AC coil frost leak; cooling trip after 15 mins (Audio 3)", "severity": "High", "status": "reported"},
                {"room_number": "207", "defect_type": "Geyser / Plumbing", "description": "Bathroom geyser thermostat tripping; lukewarm water (Audio 3)", "severity": "Medium", "status": "in_progress"},
            ]
            for d in defects_data:
                db.add(RoomDefect(**d))
            print(f"✓ Seeded {len(defects_data)} Room Defects.")

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
