import pytest

from src.classes import APIAdapter, AeroplanesAPI, BaseAPIAdapter


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def json(self):
        return self._payload


def test_base_api_adapter_is_abstract() -> None:
    with pytest.raises(TypeError):
        BaseAPIAdapter()


def test_api_adapter_initializes_urls() -> None:
    adapter = APIAdapter()

    assert adapter.openstreetmap_url == "https://nominatim.openstreetmap.org/search"
    assert adapter.opensky_url == "https://opensky-network.org/api/states/all?"


def test_aeroplanes_api_inherits_api_adapter_urls() -> None:
    api = AeroplanesAPI()

    assert isinstance(api, APIAdapter)
    assert api.openstreetmap_url == "https://nominatim.openstreetmap.org/search"
    assert api.opensky_url == "https://opensky-network.org/api/states/all?"


def test_get_aeroplanes_uses_nominatim_bbox_for_opensky_request(monkeypatch) -> None:
    calls = []
    nominatim_payload = [{"boundingbox": ["51.2", "56.1", "23.1", "32.8"]}]
    opensky_payload = {"time": 123, "states": [["abc123", "BEL123", "Belarus"]]}

    def fake_get(url, params=None, headers=None):
        calls.append({"url": url, "params": params, "headers": headers})
        if url == "https://nominatim.openstreetmap.org/search":
            return FakeResponse(nominatim_payload)
        return FakeResponse(opensky_payload)

    monkeypatch.setattr("src.classes.get", fake_get)

    result = APIAdapter().get_aeroplanes("Belarus")

    assert result == opensky_payload
    assert calls[0] == {
        "url": "https://nominatim.openstreetmap.org/search",
        "params": {"country": "Belarus", "format": "json", "limit": 1},
        "headers": {"User-Agent": "test-app/1.0"},
    }
    assert calls[1] == {
        "url": "https://opensky-network.org/api/states/all?",
        "params": {"lamin": "51.2", "lamax": "56.1", "lomin": "23.1", "lomax": "32.8"},
        "headers": None,
    }
