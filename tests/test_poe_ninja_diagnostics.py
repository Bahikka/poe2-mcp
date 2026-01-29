"""Diagnostics-focused tests for poe.ninja imports."""

import os
import json
import sys
from urllib.parse import urlparse, unquote
from pathlib import Path
import pytest
import httpx
import asyncio

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


def test_resolved_account_guard_rejects_changes():
    api = PoeNinjaAPI()
    account = "🅱🄰🅷🅸🅺🅺🄰-1456"

    with pytest.raises(ValueError):
        api._validate_resolved_identity(account, "BAHIKKA-1456", "account")

    api._validate_resolved_identity("Account#1234", "Account-1234", "account", allow_hash_swap=True)


def test_bahikka_url_import_fallback_and_unicode():
    url = (
        "https://poe.ninja/poe2/profile/%F0%9F%85%B1%F0%9F%84%B0%F0%9F%85%B7"
        "%F0%9F%85%B8%F0%9F%85%BA%F0%9F%85%BA%F0%9F%84%B0-1456/character/Bahikka"
    )
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    account = unquote(parts[2])
    character = unquote(parts[4])

    fixture_path = Path("tests/fixtures/poe_ninja_bahikka.json")
    fixture_data = json.loads(fixture_path.read_text())

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/poe2/api/data/index-state"):
            return httpx.Response(
                200,
                json={
                    "snapshotVersions": [
                        {"url": "vaal", "version": "vaal-1"},
                        {"url": "abyss", "version": "abyss-1"},
                    ]
                },
            )
        if request.url.path.endswith("/poe2/api/builds/vaal-1/character"):
            return httpx.Response(404, json={"error": "not found"})
        if request.url.path.endswith("/poe2/api/builds/abyss-1/character"):
            params = dict(request.url.params)
            assert params["account"] == account
            assert params["name"] == character
            assert params["overview"] == "abyss"
            return httpx.Response(200, json=fixture_data)
        return httpx.Response(404, json={"error": "unexpected url"})

    api = PoeNinjaAPI()
    api.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    async def run_fetch() -> dict:
        try:
            return await api.fetch_character_verbose(
                account=account,
                character=character,
                league="Abyss",
                overview="vaal",
                allow_html_fallback=False,
            )
        finally:
            await api.close()

    result = asyncio.run(run_fetch())

    assert result["resolved_account"] == account
    assert result["overview"] == "abyss"
    assert result["build_version"] == "abyss-1"
    assert result["data"]
    assert api._extract_items(result["data"])
    assert api._select_active_passives(result["data"])
