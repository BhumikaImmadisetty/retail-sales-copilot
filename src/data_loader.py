from pathlib import Path
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def create_sample_data():
    DATA_DIR.mkdir(exist_ok=True)

    products = pd.DataFrame([
        [1, "Wireless Mouse", "Electronics", 799],
        [2, "USB-C Cable", "Electronics", 399],
        [3, "Bluetooth Speaker", "Electronics", 1499],
        [4, "Laptop Backpack", "Accessories", 1299],
        [5, "Mechanical Keyboard", "Electronics", 2499],
        [6, "Webcam", "Electronics", 1899],
        [7, "Notebook", "Stationery", 120],
        [8, "Water Bottle", "Lifestyle", 599],
        [9, "Desk Lamp", "Home", 999],
        [10, "Power Bank", "Electronics", 1599],
    ], columns=["product_id", "product_name", "category", "price"])

    stores = pd.DataFrame([
        [1, "Main Street Store", "Vijayawada"],
        [2, "City Center Store", "Guntur"],
        [3, "Market Road Store", "Hyderabad"],
    ], columns=["store_id", "store_name", "city"])

    inventory = pd.DataFrame([
        [1, 1, 18],
        [1, 2, 55],
        [1, 3, 8],
        [1, 4, 120],
        [1, 5, 35],
        [1, 6, 12],
        [1, 7, 300],
        [1, 8, 15],
        [1, 9, 90],
        [1, 10, 22],

        [2, 1, 10],
        [2, 2, 80],
        [2, 3, 25],
        [2, 4, 18],
        [2, 5, 60],
        [2, 6, 30],
        [2, 7, 400],
        [2, 8, 20],
        [2, 9, 40],
        [2, 10, 50],

        [3, 1, 35],
        [3, 2, 20],
        [3, 3, 12],
        [3, 4, 75],
        [3, 5, 15],
        [3, 6, 8],
        [3, 7, 250],
        [3, 8, 60],
        [3, 9, 25],
        [3, 10, 18],
    ], columns=["store_id", "product_id", "quantity"])

    # Generate realistic daily sales for 30 days
    import random
    from datetime import date, timedelta

    random.seed(42)

    sales_rows = []
    start_date = date.today() - timedelta(days=29)

    base_sales = {
        1: 5,
        2: 4,
        3: 2,
        4: 1,
        5: 3,
        6: 2,
        7: 10,
        8: 3,
        9: 1,
        10: 4,
    }

    for day in range(30):
        current_date = start_date + timedelta(days=day)

        for store_id in [1, 2, 3]:
            for product_id in range(1, 11):
                base = base_sales[product_id]

                # Create a sales spike/drop for some products
                multiplier = 1.0

                if product_id == 1 and day >= 23:
                    multiplier = 1.8

                if product_id == 5 and day >= 20:
                    multiplier = 0.45

                quantity = max(
                    0,
                    int(random.gauss(base * multiplier, max(1, base * 0.25)))
                )

                if quantity > 0:
                    sales_rows.append([
                        current_date.isoformat(),
                        store_id,
                        product_id,
                        quantity
                    ])

    sales = pd.DataFrame(
        sales_rows,
        columns=["date", "store_id", "product_id", "quantity"]
    )

    products.to_csv(DATA_DIR / "products.csv", index=False)
    stores.to_csv(DATA_DIR / "stores.csv", index=False)
    inventory.to_csv(DATA_DIR / "inventory.csv", index=False)
    sales.to_csv(DATA_DIR / "sales.csv", index=False)


def load_data():
    required_files = [
        DATA_DIR / "products.csv",
        DATA_DIR / "stores.csv",
        DATA_DIR / "inventory.csv",
        DATA_DIR / "sales.csv",
    ]

    if not all(file.exists() for file in required_files):
        create_sample_data()

    products = pd.read_csv(DATA_DIR / "products.csv")
    stores = pd.read_csv(DATA_DIR / "stores.csv")
    inventory = pd.read_csv(DATA_DIR / "inventory.csv")
    sales = pd.read_csv(DATA_DIR / "sales.csv")

    return products, stores, inventory, sales