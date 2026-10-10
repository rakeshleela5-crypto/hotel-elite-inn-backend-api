from datetime import datetime
from database import SessionLocal, engine, Base
from models import (
    Room, RestaurantTable, InventoryItem, CorporateAccount, RoomDefect, MenuItem
)

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # -------------------------------------------------------------
        # 1. 27 Authentic Physical Rooms (Image 1 & 2 Operational Sheet)
        # -------------------------------------------------------------
        rooms_data = [
            # Floor 1 (9 Rooms: 101 - 109)
            {"number": "101", "category": "Executive King Bed", "base_price": 2050.0, "floor": 1, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 1ST FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "102", "category": "Deluxe King Bed", "base_price": 1750.0, "floor": 1, "status": "occupied", "amenities": "King Bed, AC, LED TV, WiFi TP 1ST FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "103", "category": "Executive King Bed", "base_price": 2050.0, "floor": 1, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 1ST FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "104", "category": "Deluxe King Bed", "base_price": 1750.0, "floor": 1, "status": "maintenance", "amenities": "King Bed, AC, LED TV, WiFi TP 1ST FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "105", "category": "Executive Twin Bed", "base_price": 2050.0, "floor": 1, "status": "occupied", "amenities": "Twin Beds, AC, LED TV, WiFi TP 1ST FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "106", "category": "Deluxe King Bed", "base_price": 1750.0, "floor": 1, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 1ST FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "107", "category": "Executive Triple Bed", "base_price": 2050.0, "floor": 1, "status": "dirty", "amenities": "Triple Bedding, AC, LED TV, WiFi TP 1ST FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "108", "category": "Standard Single Bed", "base_price": 1450.0, "floor": 1, "status": "clean", "amenities": "Single Bed, AC, LED TV, WiFi TP 1ST FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "109", "category": "Suite King Bed", "base_price": 3250.0, "floor": 1, "status": "clean", "amenities": "Plush King Bed, Living Area, AC, LED TV, WiFi TP 1ST FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},

            # Floor 2 (9 Rooms: 201 - 209)
            {"number": "201", "category": "Executive King Bed", "base_price": 2050.0, "floor": 2, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 2ND FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "202", "category": "Deluxe King Bed", "base_price": 1750.0, "floor": 2, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 2ND FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "203", "category": "Executive King Bed", "base_price": 2050.0, "floor": 2, "status": "occupied", "amenities": "King Bed, AC, LED TV, WiFi TP 2ND FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "204", "category": "Deluxe King Bed", "base_price": 1750.0, "floor": 2, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 2ND FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "205", "category": "Executive Twin Bed", "base_price": 2050.0, "floor": 2, "status": "clean", "amenities": "Twin Beds, AC, LED TV, WiFi TP 2ND FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "206", "category": "Deluxe King Bed", "base_price": 1750.0, "floor": 2, "status": "occupied", "amenities": "King Bed, AC, LED TV, WiFi TP 2ND FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "207", "category": "Executive Triple Bed", "base_price": 2050.0, "floor": 2, "status": "dirty", "amenities": "Triple Bedding, AC, LED TV, WiFi TP 2ND FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "208", "category": "Standard Single Bed", "base_price": 1450.0, "floor": 2, "status": "clean", "amenities": "Single Bed, AC, LED TV, WiFi TP 2ND FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "209", "category": "Suite King Bed", "base_price": 3250.0, "floor": 2, "status": "clean", "amenities": "Plush King Bed, Living Area, AC, LED TV, WiFi TP 2ND FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},

            # Floor 3 (9 Rooms: 301 - 309)
            {"number": "301", "category": "Executive King Bed", "base_price": 2050.0, "floor": 3, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 3RD FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "302", "category": "Executive King Bed", "base_price": 2050.0, "floor": 3, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 3RD FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "303", "category": "Executive King Bed", "base_price": 2050.0, "floor": 3, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 3RD FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "304", "category": "Executive King Bed", "base_price": 2050.0, "floor": 3, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 3RD FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "305", "category": "Executive King Bed", "base_price": 2050.0, "floor": 3, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 3RD FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "306", "category": "Executive King Bed", "base_price": 2050.0, "floor": 3, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 3RD FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "307", "category": "Executive King Bed", "base_price": 2050.0, "floor": 3, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 3RD FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "308", "category": "Executive King Bed", "base_price": 2050.0, "floor": 3, "status": "clean", "amenities": "King Bed, AC, LED TV, WiFi TP 3RD FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
            {"number": "309", "category": "Premium King Bed", "base_price": 2450.0, "floor": 3, "status": "clean", "amenities": "Premium King Bed, AC, LED TV, WiFi TP 3RD FLOOR, 24h Hot Water, Compl. Breakfast, 1L Water"},
        ]

        # Upsert all 27 rooms
        for r in rooms_data:
            existing = db.query(Room).filter(Room.number == r["number"]).first()
            if existing:
                existing.category = r["category"]
                existing.base_price = r["base_price"]
                existing.floor = r["floor"]
                existing.amenities = r["amenities"]
            else:
                db.add(Room(**r))
        db.commit()
        print(f"✓ Synchronized 27 Hotel Elite Inn Physical Rooms.")

        # -------------------------------------------------------------
        # 2. Restaurant Tables
        # -------------------------------------------------------------
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
            db.commit()
            print(f"✓ Seeded {len(tables_data)} Restaurant Tables.")

        # -------------------------------------------------------------
        # 3. Authentic F&B Menu (Images 4 & 5 Official Menu Card)
        # -------------------------------------------------------------
        if db.query(MenuItem).count() == 0:
            menu_data = [
                # Hot & Cold Beverages
                {"item_code": "BEV-01", "name": "TEA", "category": "Hot & Cold Beverages", "price": 25.0, "is_veg": True},
                {"item_code": "BEV-02", "name": "BLACK TEA", "category": "Hot & Cold Beverages", "price": 20.0, "is_veg": True},
                {"item_code": "BEV-03", "name": "LEMON TEA", "category": "Hot & Cold Beverages", "price": 25.0, "is_veg": True},
                {"item_code": "BEV-04", "name": "GREEN TEA", "category": "Hot & Cold Beverages", "price": 30.0, "is_veg": True},
                {"item_code": "BEV-05", "name": "COFFEE", "category": "Hot & Cold Beverages", "price": 35.0, "is_veg": True},
                {"item_code": "BEV-06", "name": "BLACK COFFEE", "category": "Hot & Cold Beverages", "price": 40.0, "is_veg": True},
                {"item_code": "BEV-07", "name": "HOT & COLD MILK", "category": "Hot & Cold Beverages", "price": 60.0, "is_veg": True},
                {"item_code": "BEV-08", "name": "CHOICE OF LASSI", "category": "Hot & Cold Beverages", "price": 60.0, "is_veg": True},
                {"item_code": "BEV-09", "name": "JAL JEERA", "category": "Hot & Cold Beverages", "price": 40.0, "is_veg": True},
                {"item_code": "BEV-10", "name": "COLD COFFEE", "category": "Hot & Cold Beverages", "price": 60.0, "is_veg": True},
                {"item_code": "BEV-11", "name": "COLD COFFEE WITH ICE CREAM", "category": "Hot & Cold Beverages", "price": 90.0, "is_veg": True},
                {"item_code": "BEV-12", "name": "BUTTER MILK", "category": "Hot & Cold Beverages", "price": 50.0, "is_veg": True},
                {"item_code": "BEV-13", "name": "FRESH LIME WATER / SODA", "category": "Hot & Cold Beverages", "price": 40.0, "is_veg": True},

                # Mocktails
                {"item_code": "MOCK-01", "name": "PINA COLADA", "category": "Mocktails", "price": 80.0, "is_veg": True},
                {"item_code": "MOCK-02", "name": "VIRGIN MOJITO", "category": "Mocktails", "price": 100.0, "is_veg": True},
                {"item_code": "MOCK-03", "name": "VIRGIN COLADA", "category": "Mocktails", "price": 110.0, "is_veg": True},
                {"item_code": "MOCK-04", "name": "SUMMER COOLER", "category": "Mocktails", "price": 110.0, "is_veg": True},
                {"item_code": "MOCK-05", "name": "GREEN RIVER", "category": "Mocktails", "price": 120.0, "is_veg": True},
                {"item_code": "MOCK-06", "name": "BLUE LAGOON", "category": "Mocktails", "price": 120.0, "is_veg": True},
                {"item_code": "MOCK-07", "name": "MANGO DELIGHT", "category": "Mocktails", "price": 120.0, "is_veg": True},
                {"item_code": "MOCK-08", "name": "ORANGE DELIGHT", "category": "Mocktails", "price": 120.0, "is_veg": True},
                {"item_code": "MOCK-09", "name": "FRUIT PUNCH", "category": "Mocktails", "price": 130.0, "is_veg": True},
                {"item_code": "MOCK-10", "name": "CHOICE OF SHAKE (VANILLA/STRAWBERRY/BANANA)", "category": "Mocktails", "price": 130.0, "is_veg": True},

                # Breakfast
                {"item_code": "BF-01", "name": "SPECIAL MAGGI", "category": "Breakfast", "price": 100.0, "is_veg": True},
                {"item_code": "BF-02", "name": "IDLY WITH SAMBHAR CHUTNEY", "category": "Breakfast", "price": 80.0, "is_veg": True},
                {"item_code": "BF-03", "name": "SAMBHAR VADA", "category": "Breakfast", "price": 80.0, "is_veg": True},
                {"item_code": "BF-04", "name": "PLAIN DOSA", "category": "Breakfast", "price": 80.0, "is_veg": True},
                {"item_code": "BF-05", "name": "MASALA DOSA", "category": "Breakfast", "price": 100.0, "is_veg": True},
                {"item_code": "BF-06", "name": "GINI DOSA", "category": "Breakfast", "price": 120.0, "is_veg": True},
                {"item_code": "BF-07", "name": "CUTTING MASALA DOSA", "category": "Breakfast", "price": 150.0, "is_veg": True},
                {"item_code": "BF-08", "name": "SCHEZWAN MASALA DOSA", "category": "Breakfast", "price": 150.0, "is_veg": True},
                {"item_code": "BF-09", "name": "CHEESE MUSHROOM DOSA", "category": "Breakfast", "price": 150.0, "is_veg": True},
                {"item_code": "BF-10", "name": "MYSORE MASALA DOSA", "category": "Breakfast", "price": 150.0, "is_veg": True},
                {"item_code": "BF-11", "name": "GHEE PODI MASALA DOSA", "category": "Breakfast", "price": 150.0, "is_veg": True},
                {"item_code": "BF-12", "name": "UPMA", "category": "Breakfast", "price": 60.0, "is_veg": True},
                {"item_code": "BF-13", "name": "UTTAPAM", "category": "Breakfast", "price": 80.0, "is_veg": True},
                {"item_code": "BF-14", "name": "RAWA DOSA", "category": "Breakfast", "price": 110.0, "is_veg": True},
                {"item_code": "BF-15", "name": "RAWA MASALA DOSA", "category": "Breakfast", "price": 120.0, "is_veg": True},
                {"item_code": "BF-16", "name": "CORN FLAKES WITH MILK", "category": "Breakfast", "price": 90.0, "is_veg": True},
                {"item_code": "BF-17", "name": "BREAD TOAST (WITH BUTTER & JAM)", "category": "Breakfast", "price": 50.0, "is_veg": True},
                {"item_code": "BF-18", "name": "SPECIAL POHA", "category": "Breakfast", "price": 120.0, "is_veg": True},
                {"item_code": "BF-19", "name": "POORI BHAJI", "category": "Breakfast", "price": 140.0, "is_veg": True},
                {"item_code": "BF-20", "name": "CHHOLEY BHATURE", "category": "Breakfast", "price": 100.0, "is_veg": True},
                {"item_code": "BF-21", "name": "ALOO PARATHA WITH CURD", "category": "Breakfast", "price": 110.0, "is_veg": True},
                {"item_code": "BF-22", "name": "GOBHI PARATHA WITH CURD", "category": "Breakfast", "price": 150.0, "is_veg": True},
                {"item_code": "BF-23", "name": "PANEER PARATHA WITH CURD", "category": "Breakfast", "price": 160.0, "is_veg": True},
                {"item_code": "BF-24", "name": "VEG GRILLED SANDWICH", "category": "Breakfast", "price": 100.0, "is_veg": True},
                {"item_code": "BF-25", "name": "OMELETTE (P/M)", "category": "Breakfast", "price": 100.0, "is_veg": False},
                {"item_code": "BF-26", "name": "BREAD OMELETTE", "category": "Breakfast", "price": 110.0, "is_veg": False},
                {"item_code": "BF-27", "name": "BOILED EGG", "category": "Breakfast", "price": 80.0, "is_veg": False},
                {"item_code": "BF-28", "name": "FRENCH TOAST", "category": "Breakfast", "price": 110.0, "is_veg": False},
                {"item_code": "BF-29", "name": "CHICKEN SANDWICH", "category": "Breakfast", "price": 200.0, "is_veg": False},

                # Fresh Salads & Curd
                {"item_code": "SAL-01", "name": "GREEN SALAD", "category": "Fresh Salads & Curd", "price": 60.0, "is_veg": True},
                {"item_code": "SAL-02", "name": "ONION SALAD", "category": "Fresh Salads & Curd", "price": 60.0, "is_veg": True},
                {"item_code": "SAL-03", "name": "KACHUMBAR SALAD", "category": "Fresh Salads & Curd", "price": 90.0, "is_veg": True},
                {"item_code": "SAL-04", "name": "SPROUTED SALAD", "category": "Fresh Salads & Curd", "price": 110.0, "is_veg": True},
                {"item_code": "SAL-05", "name": "ALOO CHANA CHAT", "category": "Fresh Salads & Curd", "price": 100.0, "is_veg": True},
                {"item_code": "SAL-06", "name": "MASALA PAPAD", "category": "Fresh Salads & Curd", "price": 40.0, "is_veg": True},
                {"item_code": "SAL-07", "name": "BOONDI RAITA", "category": "Fresh Salads & Curd", "price": 70.0, "is_veg": True},
                {"item_code": "SAL-08", "name": "PINEAPPLE RAITA", "category": "Fresh Salads & Curd", "price": 110.0, "is_veg": True},

                # From the Soup Kettle
                {"item_code": "SOP-01", "name": "VEG HOT & SOUR SOUP", "category": "Soup Kettle", "price": 110.0, "is_veg": True},
                {"item_code": "SOP-02", "name": "VEG MANCHOW SOUP", "category": "Soup Kettle", "price": 110.0, "is_veg": True},
                {"item_code": "SOP-03", "name": "VEG SWEET CORN SOUP", "category": "Soup Kettle", "price": 110.0, "is_veg": True},
                {"item_code": "SOP-04", "name": "TOMATO SOUP", "category": "Soup Kettle", "price": 110.0, "is_veg": True},
                {"item_code": "SOP-05", "name": "TOMATO DHANIYA KA SHORBA", "category": "Soup Kettle", "price": 130.0, "is_veg": True},
                {"item_code": "SOP-06", "name": "CHICKEN HOT & SOUR SOUP", "category": "Soup Kettle", "price": 130.0, "is_veg": False},
                {"item_code": "SOP-07", "name": "CHICKEN MANCHOW SOUP", "category": "Soup Kettle", "price": 130.0, "is_veg": False},
                {"item_code": "SOP-08", "name": "CHICKEN SWEET CORN SOUP", "category": "Soup Kettle", "price": 130.0, "is_veg": False},
                {"item_code": "SOP-09", "name": "CHICKEN SHORBA", "category": "Soup Kettle", "price": 180.0, "is_veg": False},

                # Veg Starters
                {"item_code": "VST-01", "name": "HARA BHARA KEBAB", "category": "Veg Starters", "price": 200.0, "is_veg": True},
                {"item_code": "VST-02", "name": "ADRAKI TIKKI", "category": "Veg Starters", "price": 200.0, "is_veg": True},
                {"item_code": "VST-03", "name": "VEG CORN KEBAB", "category": "Veg Starters", "price": 200.0, "is_veg": True},
                {"item_code": "VST-04", "name": "VEG SEEKH KEBAB", "category": "Veg Starters", "price": 250.0, "is_veg": True},
                {"item_code": "VST-05", "name": "VEG CUTLET", "category": "Veg Starters", "price": 150.0, "is_veg": True},
                {"item_code": "VST-06", "name": "DAHI KEBAB", "category": "Veg Starters", "price": 220.0, "is_veg": True},
                {"item_code": "VST-07", "name": "PANEER PAKODA", "category": "Veg Starters", "price": 200.0, "is_veg": True},
                {"item_code": "VST-08", "name": "PANEER KURKURE ROLL", "category": "Veg Starters", "price": 220.0, "is_veg": True},
                {"item_code": "VST-09", "name": "CHANA ROAST", "category": "Veg Starters", "price": 150.0, "is_veg": True},
                {"item_code": "VST-10", "name": "MUSHROOM PAKODA", "category": "Veg Starters", "price": 160.0, "is_veg": True},
                {"item_code": "VST-11", "name": "FINGER CHIPS", "category": "Veg Starters", "price": 120.0, "is_veg": True},
                {"item_code": "VST-12", "name": "PANEER TIKKA", "category": "Veg Starters", "price": 250.0, "is_veg": True},
                {"item_code": "VST-13", "name": "PANEER PUDINA TIKKA", "category": "Veg Starters", "price": 250.0, "is_veg": True},
                {"item_code": "VST-14", "name": "PANEER LEHSUNI TIKKA", "category": "Veg Starters", "price": 250.0, "is_veg": True},
                {"item_code": "VST-15", "name": "PANEER HARIYALI TIKKA", "category": "Veg Starters", "price": 250.0, "is_veg": True},
                {"item_code": "VST-16", "name": "CHEESE CORN BOWL", "category": "Veg Starters", "price": 250.0, "is_veg": True},
                {"item_code": "VST-17", "name": "TANDOORI PLATTER (VEG)", "category": "Veg Starters", "price": 650.0, "is_veg": True},

                # Non-Veg Starters
                {"item_code": "NST-01", "name": "EGG POUCH", "category": "Non-Veg Starters", "price": 90.0, "is_veg": False},
                {"item_code": "NST-02", "name": "EGG PAKODA", "category": "Non-Veg Starters", "price": 110.0, "is_veg": False},
                {"item_code": "NST-03", "name": "CHICKEN PAKODA", "category": "Non-Veg Starters", "price": 220.0, "is_veg": False},
                {"item_code": "NST-04", "name": "CHICKEN AMRITSARI (FRY)", "category": "Non-Veg Starters", "price": 250.0, "is_veg": False},
                {"item_code": "NST-05", "name": "CHICKEN TIKKA", "category": "Non-Veg Starters", "price": 300.0, "is_veg": False},
                {"item_code": "NST-06", "name": "CHICKEN BANJARA TIKKA", "category": "Non-Veg Starters", "price": 300.0, "is_veg": False},
                {"item_code": "NST-07", "name": "CHICKEN AFGHANI TIKKA", "category": "Non-Veg Starters", "price": 350.0, "is_veg": False},
                {"item_code": "NST-08", "name": "CHICKEN MALAI TIKKA", "category": "Non-Veg Starters", "price": 350.0, "is_veg": False},
                {"item_code": "NST-09", "name": "CHICKEN HARIYALI TIKKA", "category": "Non-Veg Starters", "price": 300.0, "is_veg": False},
                {"item_code": "NST-10", "name": "CHICKEN GARLIC TIKKA", "category": "Non-Veg Starters", "price": 300.0, "is_veg": False},
                {"item_code": "NST-11", "name": "CHICKEN DOUBLE TADKA TIKKA", "category": "Non-Veg Starters", "price": 350.0, "is_veg": False},
                {"item_code": "NST-12", "name": "CHEF SPECIAL CHICKEN TIKKA", "category": "Non-Veg Starters", "price": 350.0, "is_veg": False},
                {"item_code": "NST-13", "name": "CHICKEN RESHMI KEBAB", "category": "Non-Veg Starters", "price": 300.0, "is_veg": False},
                {"item_code": "NST-14", "name": "CHICKEN TANGDI KEBAB", "category": "Non-Veg Starters", "price": 300.0, "is_veg": False},

                # Main Course Curries & Gravies
                {"item_code": "MC-01", "name": "CHICKEN MASALA", "category": "Main Course", "price": 280.0, "is_veg": False},
                {"item_code": "MC-02", "name": "CHICKEN KADAI", "category": "Main Course", "price": 280.0, "is_veg": False},
                {"item_code": "MC-03", "name": "CHICKEN HYDERABADI", "category": "Main Course", "price": 290.0, "is_veg": False},
                {"item_code": "MC-04", "name": "CHICKEN RARA", "category": "Main Course", "price": 320.0, "is_veg": False},
                {"item_code": "MC-05", "name": "CHICKEN BHUNA", "category": "Main Course", "price": 290.0, "is_veg": False},
                {"item_code": "MC-06", "name": "CHICKEN MAHARAJA", "category": "Main Course", "price": 350.0, "is_veg": False},
                {"item_code": "MC-07", "name": "CHICKEN ASIYANA", "category": "Main Course", "price": 290.0, "is_veg": False},
                {"item_code": "MC-08", "name": "CHICKEN ROGAN JOSH", "category": "Main Course", "price": 290.0, "is_veg": False},
                {"item_code": "MC-09", "name": "CHICKEN BHARTA", "category": "Main Course", "price": 320.0, "is_veg": False},
                {"item_code": "MC-10", "name": "CHICKEN BUTTER MASALA", "category": "Main Course", "price": 320.0, "is_veg": False},
                {"item_code": "MC-11", "name": "CHICKEN TIKKA MASALA", "category": "Main Course", "price": 350.0, "is_veg": False},
                {"item_code": "MC-12", "name": "BUTTER CHICKEN BONELESS", "category": "Main Course", "price": 350.0, "is_veg": False},
                {"item_code": "MC-13", "name": "MURG MUSSALLAM (HALF)", "category": "Main Course", "price": 350.0, "is_veg": False},
                {"item_code": "MC-14", "name": "MURG MUSSALLAM (FULL)", "category": "Main Course", "price": 650.0, "is_veg": False},
                {"item_code": "MC-15", "name": "FISH CURRY (B/L)", "category": "Main Course", "price": 270.0, "is_veg": False},
                {"item_code": "MC-16", "name": "FISH MASALA (B/L)", "category": "Main Course", "price": 270.0, "is_veg": False},
                {"item_code": "MC-17", "name": "FISH AMRITSARI CURRY", "category": "Main Course", "price": 270.0, "is_veg": False},
                {"item_code": "MC-18", "name": "FISH CURRY BENGALI STYLE", "category": "Main Course", "price": 270.0, "is_veg": False},
                {"item_code": "MC-19", "name": "FISH TIKKA MASALA", "category": "Main Course", "price": 300.0, "is_veg": False},
                {"item_code": "MC-20", "name": "PRAWNS CURRY", "category": "Main Course", "price": 350.0, "is_veg": False},
                {"item_code": "MC-21", "name": "PRAWNS MASALA", "category": "Main Course", "price": 350.0, "is_veg": False},
                {"item_code": "MC-22", "name": "PRAWNS CURRY IN BENGALI STYLE", "category": "Main Course", "price": 370.0, "is_veg": False},
                {"item_code": "MC-23", "name": "TANDOORI PRAWNS MASALA", "category": "Main Course", "price": 370.0, "is_veg": False},
                {"item_code": "MC-24", "name": "MUTTON CURRY", "category": "Main Course", "price": 380.0, "is_veg": False},
                {"item_code": "MC-25", "name": "MUTTON MASALA", "category": "Main Course", "price": 380.0, "is_veg": False},
                {"item_code": "MC-26", "name": "BHUNA MUTTON", "category": "Main Course", "price": 380.0, "is_veg": False},
                {"item_code": "MC-27", "name": "MUTTON ROGAN JOSH", "category": "Main Course", "price": 380.0, "is_veg": False},
                {"item_code": "MC-28", "name": "MUTTON RARA", "category": "Main Course", "price": 450.0, "is_veg": False},
                {"item_code": "MC-29", "name": "CHAMPARAN MEAT", "category": "Main Course", "price": 500.0, "is_veg": False},

                # Indian & Tandoori Breads
                {"item_code": "BRD-01", "name": "RUMALI ROTI", "category": "Indian Breads", "price": 40.0, "is_veg": True},
                {"item_code": "BRD-02", "name": "TAWA ROTI", "category": "Indian Breads", "price": 25.0, "is_veg": True},
                {"item_code": "BRD-03", "name": "BUTTER TAWA ROTI", "category": "Indian Breads", "price": 25.0, "is_veg": True},
                {"item_code": "BRD-04", "name": "TANDOORI ROTI", "category": "Indian Breads", "price": 30.0, "is_veg": True},
                {"item_code": "BRD-05", "name": "BUTTER TANDOORI ROTI", "category": "Indian Breads", "price": 35.0, "is_veg": True},
                {"item_code": "BRD-06", "name": "MISSI ROTI", "category": "Indian Breads", "price": 40.0, "is_veg": True},
                {"item_code": "BRD-07", "name": "PLAIN PARATHA TAWA", "category": "Indian Breads", "price": 40.0, "is_veg": True},
                {"item_code": "BRD-08", "name": "LACHHA PARATHA", "category": "Indian Breads", "price": 40.0, "is_veg": True},
                {"item_code": "BRD-09", "name": "PLAIN NAAN", "category": "Indian Breads", "price": 40.0, "is_veg": True},
                {"item_code": "BRD-10", "name": "BUTTER NAAN", "category": "Indian Breads", "price": 45.0, "is_veg": True},
                {"item_code": "BRD-11", "name": "GARLIC NAAN", "category": "Indian Breads", "price": 55.0, "is_veg": True},
                {"item_code": "BRD-12", "name": "MASALA KULCHA", "category": "Indian Breads", "price": 55.0, "is_veg": True},
                {"item_code": "BRD-13", "name": "PANEER KULCHA", "category": "Indian Breads", "price": 70.0, "is_veg": True},
                {"item_code": "BRD-14", "name": "ROTI BASKET", "category": "Indian Breads", "price": 350.0, "is_veg": True},

                # Basmati Ke Jadoo (Rice & Biryanis)
                {"item_code": "RCE-01", "name": "PLAIN RICE (BASMATI)", "category": "Basmati Ke Jadoo", "price": 100.0, "is_veg": True},
                {"item_code": "RCE-02", "name": "JEERA RICE", "category": "Basmati Ke Jadoo", "price": 120.0, "is_veg": True},
                {"item_code": "RCE-03", "name": "VEG BIRYANI", "category": "Basmati Ke Jadoo", "price": 210.0, "is_veg": True},
                {"item_code": "RCE-04", "name": "VEG PULAO", "category": "Basmati Ke Jadoo", "price": 210.0, "is_veg": True},
                {"item_code": "RCE-05", "name": "CURD RICE", "category": "Basmati Ke Jadoo", "price": 150.0, "is_veg": True},
                {"item_code": "RCE-06", "name": "LEMON RICE", "category": "Basmati Ke Jadoo", "price": 150.0, "is_veg": True},
                {"item_code": "RCE-07", "name": "PANEER BIRYANI", "category": "Basmati Ke Jadoo", "price": 250.0, "is_veg": True},
                {"item_code": "RCE-08", "name": "PANEER TIKKA BIRYANI", "category": "Basmati Ke Jadoo", "price": 280.0, "is_veg": True},
                {"item_code": "RCE-09", "name": "EGG BIRYANI", "category": "Basmati Ke Jadoo", "price": 180.0, "is_veg": False},
                {"item_code": "RCE-10", "name": "CHICKEN DUM BIRYANI", "category": "Basmati Ke Jadoo", "price": 250.0, "is_veg": False},
                {"item_code": "RCE-11", "name": "CHICKEN HYDERABADI BIRYANI", "category": "Basmati Ke Jadoo", "price": 270.0, "is_veg": False},
                {"item_code": "RCE-12", "name": "CHICKEN ROAST BIRYANI", "category": "Basmati Ke Jadoo", "price": 290.0, "is_veg": False},
                {"item_code": "RCE-13", "name": "CHICKEN TIKKA BIRYANI", "category": "Basmati Ke Jadoo", "price": 300.0, "is_veg": False},
                {"item_code": "RCE-14", "name": "CHICKEN HANDI BIRYANI", "category": "Basmati Ke Jadoo", "price": 350.0, "is_veg": False},
                {"item_code": "RCE-15", "name": "PRAWNS BIRYANI", "category": "Basmati Ke Jadoo", "price": 280.0, "is_veg": False},
                {"item_code": "RCE-16", "name": "MUTTON BIRYANI", "category": "Basmati Ke Jadoo", "price": 350.0, "is_veg": False},
                {"item_code": "RCE-17", "name": "MUTTON HANDI BIRYANI", "category": "Basmati Ke Jadoo", "price": 400.0, "is_veg": False},

                # Continental & Pastas (Menu Photo 1)
                {"item_code": "CONT-01", "name": "WHITE SAUCE PASTA VEG", "category": "Continental", "price": 200.0, "is_veg": True},
                {"item_code": "CONT-02", "name": "RED SAUCE PASTA VEG", "category": "Continental", "price": 200.0, "is_veg": True},
                {"item_code": "CONT-03", "name": "FUSELI PASTA", "category": "Continental", "price": 210.0, "is_veg": True},
                {"item_code": "CONT-04", "name": "MIX SAUCE PASTA", "category": "Continental", "price": 220.0, "is_veg": True},
                {"item_code": "CONT-05", "name": "WHITE SAUCE CHICKEN PASTA", "category": "Continental", "price": 280.0, "is_veg": False},
                {"item_code": "CONT-06", "name": "RED SAUCE CHICKEN PASTA", "category": "Continental", "price": 280.0, "is_veg": False},
                {"item_code": "CONT-07", "name": "MIX SAUCE CHICKEN PASTA", "category": "Continental", "price": 300.0, "is_veg": False},
                {"item_code": "CONT-08", "name": "CHICKEN BARBECUE", "category": "Continental", "price": 250.0, "is_veg": False},

                # Sizzlers (Menu Photo 1)
                {"item_code": "SZL-01", "name": "VEG MIX GRILLED SIZZLER", "category": "Sizzlers", "price": 200.0, "is_veg": True},
                {"item_code": "SZL-02", "name": "MIX VEG TANDOORI SIZZLER", "category": "Sizzlers", "price": 350.0, "is_veg": True},
                {"item_code": "SZL-03", "name": "CHICKEN TIKKA SIZZLER", "category": "Sizzlers", "price": 400.0, "is_veg": False},
                {"item_code": "SZL-04", "name": "MIX CHICKEN SIZZLER", "category": "Sizzlers", "price": 400.0, "is_veg": False},
                {"item_code": "SZL-05", "name": "MIX NON VEG SIZZLER", "category": "Sizzlers", "price": 550.0, "is_veg": False},

                # Sweet Memories / Desserts (Menu Photo 1)
                {"item_code": "DES-01", "name": "FRESH FRUITE PLATTER", "category": "Desserts", "price": 200.0, "is_veg": True},
                {"item_code": "DES-02", "name": "HOT GULAB JAMUN", "category": "Desserts", "price": 110.0, "is_veg": True},
                {"item_code": "DES-03", "name": "RICE KHEER", "category": "Desserts", "price": 90.0, "is_veg": True},
                {"item_code": "DES-04", "name": "GAJAR HALWA (SEASONAL)", "category": "Desserts", "price": 120.0, "is_veg": True},
                {"item_code": "DES-05", "name": "HOT GULAB JAMUN WITH ICE-CREAM", "category": "Desserts", "price": 150.0, "is_veg": True},
                {"item_code": "DES-06", "name": "VANILLA ICE-CREAM", "category": "Desserts", "price": 80.0, "is_veg": True},
                {"item_code": "DES-07", "name": "VANILL ICE-CREAM WITH HOT CHOCOLATE SAUCE", "category": "Desserts", "price": 150.0, "is_veg": True},
                {"item_code": "DES-08", "name": "STRAWBERRY ICE-CREAM", "category": "Desserts", "price": 80.0, "is_veg": True},
                {"item_code": "DES-09", "name": "PLAIN PISTA", "category": "Desserts", "price": 80.0, "is_veg": True},
                {"item_code": "DES-10", "name": "KEASR PISTA", "category": "Desserts", "price": 100.0, "is_veg": True},
                {"item_code": "DES-11", "name": "BUTTER SCOTCH", "category": "Desserts", "price": 110.0, "is_veg": True},
                {"item_code": "DES-12", "name": "CHOCOLATE ICE-CREAM", "category": "Desserts", "price": 110.0, "is_veg": True},

                # From Room Service Thermal Bill (Photo 2 - R.S/2913)
                {"item_code": "DAL-01", "name": "DAL FRY", "category": "Dal & Curries", "price": 130.0, "is_veg": True},
            ]
            for m in menu_data:
                existing = db.query(MenuItem).filter(MenuItem.name == m["name"]).first()
                if not existing:
                    db.add(MenuItem(**m))
            db.commit()
            print(f"✓ Seeded Authentic Menu Items.")

        # -------------------------------------------------------------
        # 4. Inventory Raw Items
        # -------------------------------------------------------------
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
            db.commit()
            print(f"✓ Seeded {len(inventory_data)} Inventory Items.")

        # -------------------------------------------------------------
        # 5. Corporate Accounts (Rayagada Units)
        # -------------------------------------------------------------
        if db.query(CorporateAccount).count() == 0:
            corporate_data = [
                {"company_name": "Ashok Leyland Logistics", "gst_number": "21AABCA1234F1Z1", "contact_person": "Sunil Mohanty (Fleet Mgr)", "contact_phone": "+91 94370 12345", "credit_limit": 150000.0, "current_outstanding": 64500.0, "billing_cycle_days": 30},
                {"company_name": "Utkal Alumina Int. Ltd (Aditya Birla)", "gst_number": "21AAACU4567G1Z8", "contact_person": "P. K. Verma (Admin VP)", "contact_phone": "+91 94371 98765", "credit_limit": 250000.0, "current_outstanding": 32400.0, "billing_cycle_days": 30},
                {"company_name": "Linde India Industrial Gases", "gst_number": "21AABCL7890H1Z3", "contact_person": "Ramesh Rao (Site Eng)", "contact_phone": "+91 98610 54321", "credit_limit": 100000.0, "current_outstanding": 38900.0, "billing_cycle_days": 15},
                {"company_name": "JK Paper Mills Ltd (Rayagada)", "gst_number": "21AAACJ1122K1Z9", "contact_person": "Corporate Accounts Desk", "contact_phone": "+91 6856 222000", "credit_limit": 300000.0, "current_outstanding": 0.0, "billing_cycle_days": 30},
            ]
            for corp in corporate_data:
                db.add(CorporateAccount(**corp))
            db.commit()
            print(f"✓ Seeded {len(corporate_data)} Corporate Accounts.")

        # -------------------------------------------------------------
        # 6. Room Defects & Maintenance
        # -------------------------------------------------------------
        if db.query(RoomDefect).count() == 0:
            defects_data = [
                {"room_number": "104", "defect_type": "AC / Cooling Defect", "description": "Split AC coil frost leak; cooling trip after 15 mins (Audio 3)", "severity": "High", "status": "reported"},
                {"room_number": "207", "defect_type": "Geyser / Plumbing", "description": "Bathroom geyser thermostat tripping; lukewarm water (Audio 3)", "severity": "Medium", "status": "in_progress"},
            ]
            for d in defects_data:
                db.add(RoomDefect(**d))
            db.commit()
            print(f"✓ Seeded {len(defects_data)} Room Defects.")

    except Exception as e:
        db.rollback()
        print(f"Seeding note: {e}")
    finally:
        db.close()
