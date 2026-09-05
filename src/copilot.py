from .analytics import (
    inventory_status,
    sales_performance,
    sales_changes
)


def build_data_context(products, stores, inventory, sales):

    stock = inventory_status(
        products,
        inventory,
        sales,
        stores
    )

    performance = sales_performance(
        products,
        sales
    )

    trends = sales_changes(
        products,
        sales
    )

    context = []

    context.append("STORE SUMMARY")

    for _, store in stores.iterrows():
        context.append(
            f"- Store ID {store['store_id']}: "
            f"{store['store_name']} ({store['city']})"
        )

    context.append(f"Number of stores: {len(stores)}")
    context.append(f"Number of products: {len(products)}")
    context.append(
        f"Total units sold: {int(sales['quantity'].sum())}"
    )

    context.append("\nINVENTORY STATUS BY STORE")

    for _, row in stock.iterrows():

        context.append(
            f"- {row['product_name']} | "
            f"Store: {row.get('store_name', row['store_id'])} | "
            f"City: {row.get('city', 'Unknown')} | "
            f"Current stock: {int(row['current_stock'])} | "
            f"Average daily sales: {row['avg_daily_sales']:.2f} | "
            f"Days remaining: {row['days_remaining']:.2f} | "
            f"Status: {row['status']}"
        )

    context.append("\nTOP PRODUCTS BY SALES")

    for _, row in performance.head(10).iterrows():

        context.append(
            f"- {row['product_name']}: "
            f"{int(row['total_units_sold'])} units sold"
        )

    context.append("\nSALES TRENDS")

    for _, row in trends.iterrows():

        context.append(
            f"- {row['product_name']}: "
            f"Recent sales={int(row['recent_sales'])}, "
            f"Previous sales={int(row['previous_sales'])}, "
            f"Change={row['change_percent']:.2f}%, "
            f"Trend={row['trend']}"
        )

    return "\n".join(context)