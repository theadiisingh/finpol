"""Helper utilities for the application."""
from typing import Any, Dict
import json
from datetime import datetime


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount."""
    return f"{currency} {amount:,.2f}"


def validate_transaction_data(data: Dict[str, Any]) -> bool:
    """Validate transaction data."""
    required_fields = ["user_id", "amount", "transaction_type"]
    return all(field in data for field in required_fields)


def serialize_datetime(obj: datetime) -> str:
    """Serialize datetime to ISO format."""
    return obj.isoformat()


def load_json_file(file_path: str) -> Dict:
    """Load JSON from file."""
    with open(file_path, "r") as f:
        return json.load(f)


def save_json_file(data: Dict, file_path: str):
    """Save JSON to file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
