import pandas as pd


STOCKOUT_THRESHOLD_DAYS = 7
OVERSTOCK_THRESHOLD_DAYS = 30


def inventory_status(products, inventory, sales, stores=None):
    recent_sales = sales.copy()
    recent_sales["date"] = pd.to_datetime(recent_sales["date"])

    # Calculate average daily sales for each store and product
    daily_sales = (
        recent_sales
        .groupby(["store_id", "product_id", "date"])["quantity"]
        .sum()
        .reset_index()
    )

    avg_sales = (
        daily_sales
        .groupby(["store_id", "product_id"])["quantity"]
        .mean()
        .reset_index(name="avg_daily_sales")
    )

    # Combine inventory with average sales
    result = inventory.merge(
        avg_sales,
        on=["store_id", "product_id"],
        how="left"
    )

    result["avg_daily_sales"] = result["avg_daily_sales"].fillna(0)

    # Calculate how many days the current stock can support
    result["days_remaining"] = result.apply(
        lambda row:
        row["quantity"] / row["avg_daily_sales"]
        if row["avg_daily_sales"] > 0 else 999,
        axis=1
    )

    def classify(days):
        if days <= STOCKOUT_THRESHOLD_DAYS:
            return "STOCK-OUT RISK"
        elif days >= OVERSTOCK_THRESHOLD_DAYS:
            return "OVERSTOCK"
        return "HEALTHY"

    result["status"] = result["days_remaining"].apply(classify)

    # Add product information
    result = result.merge(
        products,
        on="product_id",
        how="left"
    )

    # Add store information
    if stores is not None:
        result = result.merge(
            stores,
            on="store_id",
            how="left"
        )

    result = result.rename(
        columns={
            "quantity": "current_stock"
        }
    )

    return result.round(2)


def sales_performance(products, sales):
    """
    Calculate sales performance by product.
    """

    sales_copy = sales.copy()
    sales_copy["date"] = pd.to_datetime(sales_copy["date"])

    summary = (
        sales_copy
        .groupby("product_id")["quantity"]
        .sum()
        .reset_index(name="total_units_sold")
    )

    result = products.merge(summary, on="product_id", how="left")
    result["total_units_sold"] = result["total_units_sold"].fillna(0)

    return result.sort_values(
        "total_units_sold",
        ascending=False
    )


def sales_changes(products, sales):
    """
    Compare recent sales with earlier sales
    to detect significant increases/decreases.
    """

    sales_copy = sales.copy()
    sales_copy["date"] = pd.to_datetime(sales_copy["date"])

    latest_date = sales_copy["date"].max()

    recent_start = latest_date - pd.Timedelta(days=6)
    previous_start = latest_date - pd.Timedelta(days=13)
    previous_end = latest_date - pd.Timedelta(days=7)

    recent = (
        sales_copy[sales_copy["date"] >= recent_start]
        .groupby("product_id")["quantity"]
        .sum()
    )

    previous = (
        sales_copy[
            (sales_copy["date"] >= previous_start) &
            (sales_copy["date"] <= previous_end)
        ]
        .groupby("product_id")["quantity"]
        .sum()
    )

    result = products.copy()

    result["recent_sales"] = result["product_id"].map(recent).fillna(0)
    result["previous_sales"] = result["product_id"].map(previous).fillna(0)

    result["change_percent"] = result.apply(
        lambda row:
        ((row["recent_sales"] - row["previous_sales"])
         / row["previous_sales"] * 100)
        if row["previous_sales"] > 0 else 0,
        axis=1
    )

    def classify(change):
        if change >= 25:
            return "SALES SPIKE"
        elif change <= -25:
            return "SALES DROP"
        return "NORMAL"

    result["trend"] = result["change_percent"].apply(classify)

    return result.round(2)


def get_attention_items(products, inventory, sales, stores=None):
    stock = inventory_status(
        products,
        inventory,
        sales,
        stores
    )

    trends = sales_changes(products, sales)

    stock_attention = stock[
        stock["status"] != "HEALTHY"
    ].copy()

    trend_attention = trends[
        trends["trend"] != "NORMAL"
    ].copy()

    return stock_attention, trend_attention