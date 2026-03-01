# Comprehensive Edge Case Demonstration Report

This report documents the performance and decision logic of OptiForm AI across varying input scenarios, covering small/short-term projects to large/long-term high-rise developments.

## Scenario 1: Small Project (Short Duration)
**Parameters:**
- Floors: 5
- Duration: 30 days
- Rental Bid: ₹500,000
- Purchase Bid: ₹1,000,000

**Result:** **RENT**
![Scenario 1 Results](/Users/deveshmishra/.gemini/antigravity/brain/a1c8dfda-f9de-4f88-b271-c2c11a33278b/scenario_1_results.png)

## Scenario 2: High-Rise Project (Multi-Year)
**Parameters:**
- Floors: 100
- Duration: 730 days
- Rental Bid: ₹8,000,000
- Purchase Bid: ₹10,000,000

**Result:** **RENT** (Optimized strategy favored rental flexibility even at scale)
![Scenario 2 Results](/Users/deveshmishra/.gemini/antigravity/brain/a1c8dfda-f9de-4f88-b271-c2c11a33278b/scenario_2_results.png)

## Scenario 3: Aggressive Rental Pricing
**Parameters:**
- Floors: 30
- Duration: 365 days
- Rental Bid: ₹10,000,000
- Purchase Bid: ₹5,000,000

**Result:** **BUY** (Amortized ownership cost is lower than the rental bid)
![Scenario 3 Results](/Users/deveshmishra/.gemini/antigravity/brain/a1c8dfda-f9de-4f88-b271-c2c11a33278b/scenario_3_results.png)

## Scenario 4: Aggressive Purchase Pricing
**Parameters:**
- Floors: 50
- Duration: 500 days
- Rental Bid: ₹1,000,000
- Purchase Bid: ₹10,000,000

**Result:** **RENT** (Extremely competitive rental pricing)
![Scenario 4 Results](/Users/deveshmishra/.gemini/antigravity/brain/a1c8dfda-f9de-4f88-b271-c2c11a33278b/scenario_4_results.png)
