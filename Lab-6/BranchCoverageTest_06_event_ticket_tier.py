import pytest
from event_ticket_tier import process_ticket_manifest, monitor_gate_flow


# =====================================================================
# 1. Tests for process_ticket_manifest
# =====================================================================

def test_invalid_input_parameters():
    """Test invalid input types and negative tax rate to raise ValueError."""
    with pytest.raises(ValueError):
        process_ticket_manifest("not_a_list", 0.1)

    with pytest.raises(ValueError):
        process_ticket_manifest([], -0.05)


def test_unconfirmed_manifest_and_zero_sales():
    """Test unconfirmed manifest leading to zero sales return status."""
    manifests = [
        {
            "is_confirmed": False,
            "tier": "general",
            "orders": [{"qty": 2, "promo": ""}]
        }
    ]
    result = process_ticket_manifest(manifests, 0.1)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_valid_tiers_promos_and_lounge():
    """Test valid seating tiers (vip, premium, general), promos, and exclusive lounge access."""
    manifests = [
        {
            "is_confirmed": True,
            "tier": "vip",
            "exclusive_lounge": True,
            "orders": [{"qty": 1, "promo": "EARLYBIRD"}]
        },
        {
            "is_confirmed": True,
            "tier": "premium",
            "exclusive_lounge": False,
            "orders": [{"qty": 5, "promo": ""}]  # Bulk order discount branch (qty >= 5)
        },
        {
            "is_confirmed": True,
            "tier": "general",
            "exclusive_lounge": False,
            "orders": [{"qty": 2, "promo": ""}]  # Standard general order
        }
    ]
    result = process_ticket_manifest(manifests, 0.10)
    assert result["status"] == "COMPLETED"
    assert result["total_revenue"] > 0.0


def test_invalid_tier_and_invalid_quantity():
    """Test invalid ticket tier and invalid quantities (<= 0)."""
    manifests = [
        {
            "is_confirmed": True,
            "tier": "unknown_tier",  # Triggers rejected_orders += 1
            "orders": [{"qty": 1, "promo": ""}]
        },
        {
            "is_confirmed": True,
            "tier": "general",
            "orders": [{"qty": 0, "promo": ""}, {"qty": -2, "promo": ""}]  # Triggers qty <= 0 rejections
        }
    ]
    result = process_ticket_manifest(manifests, 0.1)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_fraud_risk_vip_break():
    """Test FRAUD_RISK promo code on VIP tier (triggers VIP manifest reset & loop break)."""
    manifests = [
        {
            "is_confirmed": True,
            "tier": "vip",
            "exclusive_lounge": True,
            "orders": [{"qty": 2, "promo": "FRAUD_RISK"}]
        }
    ]
    result = process_ticket_manifest(manifests, 0.1)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}


def test_fraud_risk_vip_break():
    """Test FRAUD_RISK promo code on VIP tier (triggers VIP manifest reset & loop break)."""
    manifests = [
        {
            "is_confirmed": True,
            "tier": "vip",
            "exclusive_lounge": False,  # MUST be False so revenue remains 0.0
            "orders": [{"qty": 2, "promo": "FRAUD_RISK"}]
        }
    ]
    result = process_ticket_manifest(manifests, 0.1)
    assert result == {"total_revenue": 0.0, "status": "ZERO_SALES"}

def test_audit_rejected_threshold():
    """Test when rejected_orders exceeds 4, triggering AUDIT_REJECTED status."""
    manifests = [
        {"is_confirmed": True, "tier": "invalid_1", "orders": []},
        {"is_confirmed": True, "tier": "invalid_2", "orders": []},
        {"is_confirmed": True, "tier": "invalid_3", "orders": []},
        {"is_confirmed": True, "tier": "invalid_4", "orders": []},
        {"is_confirmed": True, "tier": "invalid_5", "orders": []},
    ]
    result = process_ticket_manifest(manifests, 0.1)
    assert result["status"] == "AUDIT_REJECTED"


# =====================================================================
# 2. Tests for monitor_gate_flow
# =====================================================================

def test_monitor_gate_flow_no_data():
    """Test empty turnstile streams input."""
    assert monitor_gate_flow([]) == "NO_DATA"


def test_monitor_gate_flow_overflow():
    """Test consecutive congestion streak >= 2 returning OVERFLOW."""
    streams = [
        [30, 40, 60, 55, 20]  # 60 and 55 are back-to-back > 50
    ]
    assert monitor_gate_flow(streams) == "OVERFLOW"


def test_monitor_gate_flow_normal_resets():
    """Test single high rate reset by low rate returning FLOW_NORMAL."""
    streams = [
        [60, 40, 60, 30]  # High rate (60) is immediately reset by 40
    ]
    assert monitor_gate_flow(streams) == "FLOW_NORMAL"  