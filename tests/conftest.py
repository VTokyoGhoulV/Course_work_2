import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest

from src.classes import Aeroplane


@pytest.fixture
def sample_plane() -> Aeroplane:
    return Aeroplane(
        icao24="ABC123",
        callsign="TEST123",
        country="Belarus",
        time_position=1,
        last_contact=2,
        longitude=27.56,
        latitude=53.90,
        baro_altitude=10_000,
        on_ground=False,
        velocity=250,
        true_track=180,
    )


@pytest.fixture
def aeroplane_factory():
    def _factory(
        *,
        icao24: str = "ABC123",
        callsign: str = "TEST123",
        country: str = "Belarus",
        velocity: int | float = 250,
        baro_altitude: int | float = 10_000,
        longitude: int | float = 27.56,
        latitude: int | float = 53.90,
    ) -> Aeroplane:
        return Aeroplane(
            icao24=icao24,
            callsign=callsign,
            country=country,
            velocity=velocity,
            baro_altitude=baro_altitude,
            longitude=longitude,
            latitude=latitude,
        )

    return _factory
