const analyzeButton = document.getElementById("analyzeBtn");
analyzeButton.addEventListener("click", () => {
    console.log("Analyze button clicked");
    analyzeStock();
});
async function analyzeStock() {
    const ticker = document.getElementById("ticker").value.trim();
    console.log(ticker)
    if (!ticker) {
        alert("Please enter a stock ticker.");
        return;
    }
    const results = document.getElementById("results");
    results.innerHTML = "<p>Loading stock information...</p>";
    try {
        const response = await fetch(
            `/stocks/analyze?ticker=${ticker}`,
            {
                method: "POST"
            }
        );
        if (!response.ok) {
            throw new Error("Unable to fetch stock data.");
        }

        const data = await response.json();
        displayResults(data);

    } catch (error) {
        results.innerHTML = `
            <p style="color:red;">
                ${error.message}
            </p>
        `;
    }
}

function displayResults(stock) {
    const results = document.getElementById("results");
    results.innerHTML = `
        <div class="result-card">
            <h2>${stock.company}</h2>
            <p><strong>Ticker:</strong> ${stock.ticker}</p>
            <p><strong>Sector:</strong> ${stock.sector}</p>
            <p><strong>Current Price:</strong> ${stock.current_price}</p>
            <p><strong>Market Cap:</strong> ${stock.market_cap}</p>
            <p><strong>52 Week High:</strong> ${stock["52_week_high"]}</p>
            <p><strong>52 Week Low:</strong> ${stock["52_week_low"]}</p>
            <p><strong>Currency:</strong> ${stock.currency}</p>
        </div>
    `;

}