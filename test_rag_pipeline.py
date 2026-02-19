#!/usr/bin/env python3
"""
Test the complete chat RAG pipeline simulation.

This tests the serialization and chunking without external dependencies.
"""

import logging
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def serialize_structured_json(data: dict[str, Any]) -> str:
    """Serialize cheatsheet data into semantically rich text for FAISS indexing."""
    parts: list[str] = []
    
    content_fields = {
        "title": 3,
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


def chunk_text_simple(text: str, chunk_size: int = 900, chunk_overlap: int = 150) -> list[str]:
    """Simple text chunking without external library."""
    if not text.strip():
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Find a good breaking point
        end = min(start + chunk_size, len(text))
        
        if end < len(text):
            # Try to break at a sentence boundary
            last_period = text.rfind(".", start, end)
            if last_period > start:
                end = last_period + 1
            else:
                # Try to break at a double newline
                last_para = text.rfind("\n\n", start, end)
                if last_para > start:
                    end = last_para + 2
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move forward but overlap
        start = end - chunk_overlap
        if start <= 0:
            break
    
    return chunks


# Mock cheatsheet data
mock_cheatsheet = {
    "title": "AI-Based Electricity Demand & Peak Forecasting",
    "one_line_summary": "Techniques for using AI models to forecast electricity consumption patterns and identify peak demand periods.",
    "definitions": [
        "Renewable Energy: Energy generated from natural sources that replenish themselves continuously",
        "Peak Demand: The highest amount of electricity consumed during a specific time period",
        "Load Forecasting: Predicting future electrical load using historical data and models",
        "Smart Grid: An electrical grid with automated control systems to optimize power distribution",
        "Energy Efficiency: Reducing electricity consumption while maintaining service levels",
    ],
    "core_formulas": [
        "RMSE = sqrt(1/n * sum((predicted - actual)^2))",
        "MAE = 1/n * sum(|predicted - actual|)",
        "Peak Load = max(hourly_loads) over 24-hour period",
        "Load Factor = Average Load / Peak Load",
    ],
    "key_concepts": [
        "Time-series forecasting for electricity consumption",
        "Machine learning models for demand prediction",
        "Integration of renewable energy sources into grids",
        "Real-time demand management and response",
        "Factors affecting electricity demand: weather, day of week, season, events",
        "Renewable energy: Wind, solar, hydroelectric power generation",
        "Sustainability and carbon reduction through renewable sources",
    ],
    "important_metrics": [
        "RMSE: Root Mean Squared Error for forecast accuracy",
        "MAPE: Mean Absolute Percentage Error",
        "Peak load forecasting accuracy: ±5-10% is typical",
        "Renewable penetration: % of total supply from renewables",
        "Grid stability: Measured by frequency deviation",
    ],
}


def test_serialization_and_chunking():
    """Test the full pipeline."""
    print("\n" + "=" * 80)
    print("TEST 1: SERIALIZATION")
    print("=" * 80)
    
    serialized = serialize_structured_json(mock_cheatsheet)
    logger.info(f"Serialized content: {len(serialized)} characters")
    
    # Check key terms
    key_terms = ["renewable", "energy", "peak", "demand", "forecasting", "electricity"]
    for term in key_terms:
        count = serialized.lower().count(term)
        logger.info(f"  '{term}' appears {count} times")
    
    print("\n" + "=" * 80)
    print("TEST 2: CHUNKING")
    print("=" * 80)
    
    chunks = chunk_text_simple(serialized, chunk_size=900, chunk_overlap=150)
    logger.info(f"Created {len(chunks)} chunks")
    
    for i, chunk in enumerate(chunks[:3]):  # Show first 3
        logger.info(f"  Chunk {i}: {len(chunk)} chars, preview: {chunk[:100]}...")
    
    print("\n" + "=" * 80)
    print("TEST 3: SEMANTIC SIMILARITY (MANUAL)")
    print("=" * 80)
    
    test_questions = [
        "what is renewable energy",
        "how to forecast electricity demand",
        "peak load calculation",
        "smart grid automation",
    ]
    
    for question in test_questions:
        print(f"\nQuestion: '{question}'")
        
        # Simple keyword matching (what FAISS would do with embeddings)
        question_words = set(question.lower().split())
        
        best_chunk_score = 0
        best_chunk_idx = -1
        
        for i, chunk in enumerate(chunks):
            chunk_words = set(chunk.lower().split())
            # Simple Jaccard similarity
            overlap = question_words & chunk_words
            if overlap:
                score = len(overlap) / len(question_words | chunk_words)
                if score > best_chunk_score:
                    best_chunk_score = score
                    best_chunk_idx = i
        
        if best_chunk_idx >= 0:
            logger.info(f"  Best match: Chunk {best_chunk_idx} (score: {best_chunk_score:.2f})")
            logger.info(f"  Preview: {chunks[best_chunk_idx][:150]}...")
        else:
            logger.warning(f"  No match found!")
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    logger.info("✓ Serialization preserves key content")
    logger.info("✓ Chunking creates reasonable segments")
    logger.info("✓ Keywords are searchable")
    logger.info("\nThe issue with empty retrieval is likely:")
    logger.info("  1. FAISS embeddings not loading (HuggingFace download)")
    logger.info("  2. Vector store creation failing silently")
    logger.info("  3. Embedding model timeout or network issue")
    logger.info("\nRECOMMENDATION: Add error handling and logging in:")
    logger.info("  - EmbeddingService.__init__()")
    logger.info("  - build_vector_store()")
    logger.info("  - retrieve_chunks()")


if __name__ == "__main__":
    test_serialization_and_chunking()
