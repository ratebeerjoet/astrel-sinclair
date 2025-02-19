<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Astrology App</title>
    <script src="/AstroChart-main/dist/astrochart.js"></script>
        <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        .buttons { margin: 10px; }
        #paper { display: flex; justify-content: center; margin-top: 20px; background: #999; }
    </style>
</head>
<body>
    <h1>Astrology App</h1>
    <div class="buttons">
        <button onclick="changeDate('day')">+1 Day</button>
        <button onclick="changeDate('threeDays')">+3 Days</button>
        <button onclick="changeDate('week')">+1 Week</button>
        <button onclick="changeDate('month')">+1 Month</button>
        <button onclick="changeDate('season')">+1 Season</button>
        <button onclick="changeDate('year')">+1 Year</button>
        <button onclick="changeDate('tenYears')">+10 Years</button>
    </div>
    <button onclick="toggleZodiac()">Toggle Zodiac (Tropical)</button>
    <div id="paper"></div>
    <pre id="planetData"></pre>

    <script>
        let date = new Date();
        let zodiacType = "tropical";

        function fetchPlanetData() {
            const formattedDate = date.toISOString().split("T")[0];
            fetch(`https://api.astrologyapi.com/v1/planet_positions?date=${formattedDate}&zodiac=${zodiacType}`)
                .then(response => response.json())
                .then(response => {
                    document.getElementById("planetData").textContent = JSON.stringify(response.data, null, 2);
                    renderChart(response.data);
                })
                .catch(error => {
                    console.error("Error fetching planetary data:", error);
                    document.getElementById("planetData").textContent = "No data available or loading...";
                });
        }

        function changeDate(increment) {
            switch (increment) {
                case "day": date.setDate(date.getDate() + 1); break;
                case "threeDays": date.setDate(date.getDate() + 3); break;
                case "week": date.setDate(date.getDate() + 7); break;
                case "month": date.setMonth(date.getMonth() + 1); break;
                case "season": date.setMonth(date.getMonth() + 3); break;
                case "year": date.setFullYear(date.getFullYear() + 1); break;
                case "tenYears": date.setFullYear(date.getFullYear() + 10); break;
            }
            fetchPlanetData();
        }

        function toggleZodiac() {
            zodiacType = zodiacType === "tropical" ? "sidereal" : "tropical";
            document.querySelector("button[onclick='toggleZodiac()']").textContent = `Toggle Zodiac (${zodiacType})`;
            fetchPlanetData();
        }

        function renderChart(data) {
            document.getElementById("paper").innerHTML = "";
            const chart = new astrochart.Chart("paper", 800, 800);
            chart.radix(data).aspects();
        }

        window.onload = fetchPlanetData;
    </script>
</body>
</html>
