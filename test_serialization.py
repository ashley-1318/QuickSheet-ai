#!/usr/bin/env python3
"""Test the improved serialization function."""

from typing import Any

# Mock the test data structure that comes from a cheatsheet
mock_cheatsheet = {
    "title": "AI-Based Electricity Demand & Peak Forecasting",
    "one_line_summary": "Techniques for using AI models to forecast electricity consumption patterns and identify peak demand periods.",
    "definitions": [
        "Renewable Energy: Energy generated from natural sources that replenish themselves continuously",
        "Peak Demand: The highest amount of electricity consumed during a specific time period",
        "Load Forecasting: Predicting future electrical load using historical data and models",
        "Smart Grid: An electrical grid with automated control systems to optimize power distribution",
    ],
    "core_formulas": [
        "RMSE = sqrt(1/n * sum((predicted - actual)^2))",
        "MAE = 1/n * sum(|predicted - actual|)",
        "Peak Load = max(hourly_loads) over 24-hour period",
    ],
    "key_concepts": [
        "Time-series forecasting for electricity consumption",
        "Machine learning models for demand prediction",
        "Integration of renewable energy sources into grids",
        "Real-time demand management and response",
        "Factors affecting electricity demand: weather, day of week, season, events",
    ],
    "important_metrics": [
        "RMSE: Root Mean Squared Error for forecast accuracy",
        "MAPE: Mean Absolute Percentage Error",
        "Peak load forecasting accuracy: ±5-10% is typical",
        "Renewable penetration: % of total supply from renewables",
    ],
}

def serialize_structured_json(data: dict[str, Any]) -> str:
    """Serialize cheatsheet data into semantically rich text for FAISS indexing."""
    parts: list[str] = []
    
    # These are the actual content fields from RagResponse
    content_fields = {
        "title": 3,  # weight - appears 3 times
        "one_line_summary": 3,
        "definitions": 2,
        "core_formulas": 2,
        "key_concepts": 2,
        "diagrams": 1,
        "comparison_table": 1,
        "important_metrics": 1,
        "mistakes_to_avoid": 1,
    }
    
    for field, weight in content_fields.items():
        value = data.get(field)
        if not value:
            continue
        
        # Add field as context (helps with semantic search)
        for _ in range(weight):
            if isinstance(value, str):
                if value.strip():
                    parts.append(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str) and item.strip():
                        parts.append(item)
                    elif isinstance(item, dict):
                        for k, v in item.items():
                            if isinstance(v, str) and v.strip():
                                parts.append(f"{k}: {v}")
    
    # Add flashcards if present
    flashcards = data.get("flashcards", [])
    if flashcards:
        for fc in flashcards:
            if isinstance(fc, dict):
                q = fc.get("question") or fc.get("prompt")
                a = fc.get("answer")
                if q and isinstance(q, str):
                    parts.append(q)
                if a and isinstance(a, str):
                    parts.append(a)
    
    serialized = "\n\n".join(parts)
    return serialized

# Test the serialization
if __name__ == "__main__":
    result = serialize_structured_json(mock_cheatsheet)
    print("=" * 80)
    print("SERIALIZED CONTENT FOR FAISS:")
    print("=" * 80)
    print(result)
    print("=" * 80)
    print(f"\nTotal length: {len(result)} characters")
    print(f"Total parts: {len(result.split(chr(10)+chr(10)))}")
    
    # Test that key terms are present
    key_terms = [
        "renewable energy",
        "peak demand",
        "electricity",
        "forecasting",
        "AI",
        "demand",
    ]
    
    print("\nKey term presence test:")
    for term in key_terms:
        found = term.lower() in result.lower()
        status = "✓" if found else "✗"
        print(f"  {status} '{term}'")
    
    # Test the question matching
    test_question = "what is renewable energy"
    print(f"\nTest question: '{test_question}'")
    print(f"Question lowercase: {test_question.lower()}")
    
    # Check if definitions contain "renewable energy"
    for definition in mock_cheatsheet["definitions"]:
        if "renewable" in definition.lower():
            print(f"\nFound in definitions: {definition}")
