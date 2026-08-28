from pathlib import Path
import ast

CONTRACT = Path(__file__).parents[1] / "contracts" / "SubscriptionSLAEscrow.py"


def test_header_syntax_and_ascii():
    text = CONTRACT.read_text(encoding="utf-8")
    assert text.startswith('# v0.2.16\n# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }\nfrom genlayer import *')
    ast.parse(text)
    text.encode("ascii")


def test_core_rules_are_present():
    text = CONTRACT.read_text(encoding="utf-8")
    for marker in ["write.payable", "gl.message.value", "prompt_comparative", "emit_transfer", "DIGEST_REUSED", "SUBSCRIBER_ONLY", "SOURCE_NOT_APPROVED", "WINDOW_NOT_CLOSED", "OBSERVATIONS_NOT_RESOLVED", "bind_plan_service", "approve_source"]:
        assert marker in text
    assert "dict[" not in text
    assert "list[" not in text


def test_subscription_guards_and_settlement_bands_are_present():
    text = CONTRACT.read_text(encoding="utf-8")
    for marker in ["WRONG_ESCROW_VALUE", "ZERO_VALUE", "OBSERVATION_ALREADY_CLASSIFIED", "CANCELLATION_NOT_REQUESTED", "PARTY_ONLY", "SLA_MET", "PARTIAL_REFUND", "FULL_REFUND", "subscription_confirmed"]:
        assert marker in text
