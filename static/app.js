async function loadDashboard() {
    try {
        const response = await fetch("/api/dashboard");

        if (!response.ok) {
            throw new Error("Dashboard request failed");
        }

        const data = await response.json();

        document.getElementById("products").textContent = data.products;
        document.getElementById("stores").textContent = data.stores;
        document.getElementById("units").textContent =
            data.total_units_sold.toLocaleString();

        document.getElementById("attention").textContent =
            data.attention_count;

        displayProducts(
            "stockout",
            data.stockout_risks,
            "days_remaining"
        );

        displayProducts(
            "overstock",
            data.overstock,
            "days_remaining"
        );

        displayProducts(
            "spikes",
            data.sales_spikes,
            "change_percent"
        );

        displayProducts(
            "drops",
            data.sales_drops,
            "change_percent"
        );

    } catch (error) {
        console.error(error);

        document.getElementById("stockout").textContent =
            "Unable to load dashboard data.";

        document.getElementById("overstock").textContent =
            "Unable to load dashboard data.";
    }
}


function displayProducts(elementId, products, metric) {

    const container = document.getElementById(elementId);

    if (!products || products.length === 0) {
        container.innerHTML = "<p>No items found.</p>";
        return;
    }

    container.innerHTML = products.map(product => {

        let value = product[metric];

        if (metric === "days_remaining") {
            value = `${value} days`;
        } else {
            value = `${value}%`;
        }

        return `
            <div class="product-item">

                <div class="product-name">
                    ${product.product_name}
                </div>

                <div class="product-details">
                    Current stock: ${product.current_stock ?? "N/A"}
                    &nbsp; | &nbsp;
                    Avg daily sales: ${product.avg_daily_sales ?? "N/A"}
                    &nbsp; | &nbsp;
                    ${metric}: ${value}
                </div>

            </div>
        `;

    }).join("");
}


function setQuestion(question) {
    document.getElementById("question").value = question;
}

async function askQuestion() {

    const question =
        document.getElementById("question").value.trim();

    const responseBox =
        document.getElementById("response");

    if (!question) {
        responseBox.textContent =
            "Please enter a question.";
        return;
    }

    responseBox.innerHTML =
        "<p>🔎 Analyzing your retail data with Gemini...</p>";

    try {

        const response = await fetch("/api/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        const data = await response.json();

        responseBox.innerHTML = `
            <div class="ai-answer">
                ${formatAnswer(data.answer)}
            </div>
        `;

    } catch (error) {

        console.error(error);

        responseBox.innerHTML =
            "<p>Unable to process the question.</p>";
    }
}


function formatAnswer(text) {

    return text
        .replace(/\n/g, "<br>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}


loadDashboard();