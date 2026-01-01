# KPIs

This project contributes to measuring and improving the following KPIs:

1. **Weather-Adjusted Demand Index**
   - Measures how sales volume deviates from baseline under specific weather conditions (e.g., hot days vs cold days).
   - Business use: demand planning and forecasting calibration.

2. **Stockout Risk Proxy (Demand Spike Indicator)**
   - Identifies days where weather conditions historically correlate with unusually high demand for certain categories.
   - Business use: proactive replenishment and staffing decisions.

3. **Promotion Uplift vs Weather Context**
   - Compares sales uplift during promotion days under different weather conditions.
   - Business use: schedule promotions when they are most effective.

(These KPIs will be computed using Athena SQL on the curated dataset after joining sales and weather.)
