"""
Reusable, modular prompt templates for Claude AI integration.
Each prompt is a function that returns a formatted string, making them
easy to test, version, and swap out.
"""

DOCUMENT_CLASSIFICATION = """You are analyzing a cafeteria operations document.

Based on the following extracted text, classify this document into one of these categories:
- DAILY_PRODUCTION: Daily food production/serving records
- WASTE_LOG: Food waste tracking logs
- MENU_PLAN: Weekly/monthly menu plans
- INVENTORY: Inventory or purchasing records
- FINANCIAL: Cost/budget reports
- OTHER: Does not fit the above categories

Also extract the date range covered by the document if present.

Respond in this exact JSON format:
{
  "document_type": "<category>",
  "date_range_start": "<YYYY-MM-DD or null>",
  "date_range_end": "<YYYY-MM-DD or null>",
  "confidence": <0.0-1.0>,
  "summary": "<one sentence summary>"
}

DOCUMENT TEXT:
---
%s
---"""


STRUCTURED_DATA_EXTRACTION = """You are a data extraction specialist for school cafeteria operations.

Extract structured data from the following cafeteria report text. Pull out every
menu item you can find along with its associated metrics.

Respond in this exact JSON format:
{
  "school_name": "<name or null>",
  "report_date": "<YYYY-MM-DD or null>",
  "menu_items": [
    {
      "name": "<item name>",
      "category": "<entree|side|beverage|dessert|fruit|vegetable|grain|dairy|other>",
      "servings_prepared": <integer or null>,
      "servings_served": <integer or null>,
      "servings_wasted": <integer or null>,
      "cost_per_serving": <float or null>,
      "date_served": "<YYYY-MM-DD or null>"
    }
  ],
  "totals": {
    "total_prepared_lbs": <float or null>,
    "total_served_lbs": <float or null>,
    "total_wasted_lbs": <float or null>,
    "total_meals_served": <integer or null>
  }
}

If a value cannot be determined from the text, use null. Do your best to infer
categories from item names (e.g., "chicken tenders" = "entree", "apple slices" = "fruit").

REPORT TEXT:
---
%s
---"""


WASTE_ANALYSIS = """You are a food waste analyst for school cafeteria operations.

Given the following structured cafeteria data, provide a detailed waste analysis.

DATA:
%s

Analyze this data and respond in this exact JSON format:
{
  "waste_level": "<low|medium|high|critical>",
  "waste_percentage": <float>,
  "key_findings": [
    "<finding 1>",
    "<finding 2>",
    "<finding 3>"
  ],
  "waste_drivers": [
    {
      "driver": "<description of waste driver>",
      "impact": "<high|medium|low>",
      "affected_items": ["<item1>", "<item2>"]
    }
  ],
  "recommendations": [
    {
      "action": "<specific actionable recommendation>",
      "priority": "<high|medium|low>",
      "expected_impact": "<description of expected outcome>",
      "timeframe": "<immediate|short-term|long-term>"
    }
  ],
  "cost_analysis": {
    "estimated_daily_waste_cost": <float or null>,
    "potential_daily_savings": <float or null>
  }
}

Waste level thresholds:
- low: < 10% waste
- medium: 10-20% waste
- high: 20-35% waste
- critical: > 35% waste

Be specific and actionable in recommendations. Reference actual menu items from the data."""


TREND_ANALYSIS = """You are a data analyst specializing in school cafeteria operations trends.

Given the following historical waste data across multiple dates/schools, identify
trends and provide strategic recommendations.

HISTORICAL DATA:
%s

Respond in this exact JSON format:
{
  "overall_trend": "<improving|stable|worsening>",
  "trend_summary": "<2-3 sentence summary>",
  "patterns": [
    {
      "pattern": "<description>",
      "evidence": "<supporting data points>"
    }
  ],
  "school_rankings": [
    {
      "school": "<name>",
      "avg_waste_pct": <float>,
      "trend": "<improving|stable|worsening>"
    }
  ],
  "strategic_recommendations": [
    {
      "recommendation": "<district-level recommendation>",
      "rationale": "<why this matters>",
      "schools_affected": ["<school1>", "<school2>"]
    }
  ]
}"""
