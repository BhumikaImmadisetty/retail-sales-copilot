from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.data_loader import load_data
from src.analytics import (
    inventory_status,
    sales_performance,
    sales_changes,
    get_attention_items,
)
from src.copilot import build_data_context
from src.gemini import ask_gemini

app = FastAPI(title="Retail Sales and Inventory Copilot")

products, stores, inventory, sales = load_data()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/api/dashboard")
def dashboard():

    stock = inventory_status(
    products,
    inventory,
    sales,
    stores
)

    trends = sales_changes(
        products,
        sales
    )

    performance = sales_performance(
        products,
        sales
    )

    stock_attention, trend_attention = get_attention_items(
    products,
    inventory,
    sales,
    stores
)

    return {
        "products": len(products),
        "stores": len(stores),
        "total_units_sold": int(sales["quantity"].sum()),

        "stockout_risks": stock[
            stock["status"] == "STOCK-OUT RISK"
        ].to_dict(orient="records"),

        "overstock": stock[
            stock["status"] == "OVERSTOCK"
        ].to_dict(orient="records"),

        "sales_spikes": trends[
            trends["trend"] == "SALES SPIKE"
        ].to_dict(orient="records"),

        "sales_drops": trends[
            trends["trend"] == "SALES DROP"
        ].to_dict(orient="records"),

        "top_products": performance.head(5).to_dict(
            orient="records"
        ),

        "attention_count": (
            len(stock_attention) +
            len(trend_attention)
        ),
    }
class QuestionRequest(BaseModel):
    question: str


@app.post("/api/ask")
def ask_copilot(request: QuestionRequest):

    question = request.question.strip()

    if not question:
        return {
            "answer": "Please enter a question."
        }

    data_context = build_data_context(
        products,
        stores,
        inventory,
        sales
    )

    answer = ask_gemini(
        question,
        data_context
    )

    return {
        "question": question,
        "answer": answer
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )