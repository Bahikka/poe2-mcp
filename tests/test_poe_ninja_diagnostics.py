"""Diagnostics-focused tests for poe.ninja imports."""

import os
import json
import sys
from pathlib import Path

os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("ENCRYPTION_KEY", "test")

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.api.poe_ninja_api import PoeNinjaAPI


def test_unicode_account_encodes_params():
    api = PoeNinjaAPI()
    account = "🅱🄰🅷🅸🅺🅺🄰-1456"
    character = "Bahikka"
    url = api._build_character_request_url(
        "https://poe.ninja/poe2/api/builds/123/character",
        {"account": account, "name": character, "overview": "overview"},
    )

    assert "%F0%9F%85%B1" in url
    assert "%25F0" not in url


def test_extract_items_handles_dict_and_list():
    api = PoeNinjaAPI()

    data_list = {"items": [{"itemData": {"name": "List Sword", "typeLine": "Sword"}}]}
    data_dict = {"equipment": {"0": {"itemData": {"name": "Dict Axe", "typeLine": "Axe"}}}}

    assert len(api._extract_items(data_list)) == 1
    assert len(api._extract_items(data_dict)) == 1


def test_bahikka_items_nonempty_from_fixture():
    fixture_path = Path("tests/fixtures/poe_ninja_bahikka.json")
    raw_data = json.loads(fixture_path.read_text())

    api = PoeNinjaAPI()
    items = api._extract_items(raw_data)

    assert items
