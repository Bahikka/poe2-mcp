"""Regression tests for poe.ninja normalization with unexpected types."""

import os

os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("ENCRYPTION_KEY", "test")

from src.api.poe_ninja_api import PoeNinjaAPI
from src.analyzer.character_analyzer import CharacterAnalyzer
from src.mcp_server import PoE2BuildOptimizerMCP


def test_poe_ninja_int_fields_do_not_crash_formatting():
    api_data = {
        "name": 12345,
        "account": 67890,
        "class": 44683,
        "level": 70,
        "league": 1010,
        "defensiveStats": {
            "life": 1200,
            "energyShield": 300,
            "fireResistance": 75,
            "coldResistance": 75,
            "lightningResistance": 75,
            "chaosResistance": 0,
        },
        "items": [
            {
                "itemSlot": 1,
                "itemData": {
                    "name": "Test Sword",
                    "typeLine": "Rusty Sword",
                    "baseType": "Sword",
                    "ilvl": 10,
                    "frameType": 2,
                    "corrupted": False,
                    "icon": "",
                    "implicitMods": [],
                    "explicitMods": [],
                    "craftedMods": [],
                    "enchantMods": [],
                },
            }
        ],
        "skills": [],
        "passiveSelectionSet1": [],
        "passiveSelectionSet2": [],
        "keystones": [],
        "flasks": [],
        "jewels": [],
        "charms": [],
    }

    normalized = PoeNinjaAPI()._normalize_api_character_data(api_data)

    assert isinstance(normalized["class"], str)
    assert isinstance(normalized["league"], str)
    assert isinstance(normalized["items"][0]["slot"], str)

    analyzer = CharacterAnalyzer()
    analysis = analyzer.analyze_character(normalized)
    assert "error" not in analysis

    mcp = PoE2BuildOptimizerMCP()
    formatted = mcp._format_character_analysis(
        normalized,
        {
            "overall_score": 0.0,
            "tier": "Unknown",
            "strengths": [],
            "weaknesses": [],
            "dps": normalized.get("dps", 0),
            "ehp": 0,
            "defense_rating": 0.0,
            "resistances": {},
        },
        recommendations="",
    )
    assert "Character Analysis" in formatted
