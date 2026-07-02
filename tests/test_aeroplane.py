import pytest

from src.classes import Aeroplane


def test_aeroplane_init_saves_all_main_fields(sample_plane: Aeroplane) -> None:
    assert sample_plane.icao24 == "ABC123"
    assert sample_plane.callsign == "TEST123"
    assert sample_plane.country == "Belarus"
    assert sample_plane.time_position == 1
    assert sample_plane.last_contact == 2
    assert sample_plane.longitude == 27.56
    assert sample_plane.latitude == 53.90
    assert sample_plane.baro_altitude == 10_000
    assert sample_plane.on_ground is False
    assert sample_plane.velocity == 250
    assert sample_plane.true_track == 180


@pytest.mark.parametrize("bad_callsign", ["", None, 123])
def test_aeroplane_rejects_invalid_callsign(aeroplane_factory, bad_callsign) -> None:
    with pytest.raises(ValueError, match="callsign"):
        aeroplane_factory(callsign=bad_callsign)


@pytest.mark.parametrize("bad_country", ["", None, 123])
def test_aeroplane_rejects_invalid_country(aeroplane_factory, bad_country) -> None:
    with pytest.raises(ValueError, match="country"):
        aeroplane_factory(country=bad_country)


@pytest.mark.parametrize("bad_velocity", [None, "fast"])
def test_aeroplane_rejects_non_numeric_velocity(aeroplane_factory, bad_velocity) -> None:
    with pytest.raises(ValueError, match="Velocity must be a number"):
        aeroplane_factory(velocity=bad_velocity)


def test_aeroplane_rejects_negative_velocity(aeroplane_factory) -> None:
    with pytest.raises(ValueError, match="Velocity cannot be negative"):
        aeroplane_factory(velocity=-1)


@pytest.mark.parametrize("bad_altitude", [None, "high"])
def test_aeroplane_rejects_non_numeric_altitude(aeroplane_factory, bad_altitude) -> None:
    with pytest.raises(ValueError, match="Baro altitude"):
        aeroplane_factory(baro_altitude=bad_altitude)


@pytest.mark.parametrize("bad_longitude", [None, "27.56"])
def test_aeroplane_rejects_non_numeric_longitude(aeroplane_factory, bad_longitude) -> None:
    with pytest.raises(ValueError, match="Longitude must be a number"):
        aeroplane_factory(longitude=bad_longitude)


@pytest.mark.parametrize("bad_longitude", [-181, 181])
def test_aeroplane_rejects_longitude_out_of_range(aeroplane_factory, bad_longitude) -> None:
    with pytest.raises(ValueError, match="Longitude must be between"):
        aeroplane_factory(longitude=bad_longitude)


@pytest.mark.parametrize("bad_latitude", [None, "53.90"])
def test_aeroplane_rejects_non_numeric_latitude(aeroplane_factory, bad_latitude) -> None:
    with pytest.raises(ValueError, match="Latitude must be a number"):
        aeroplane_factory(latitude=bad_latitude)


@pytest.mark.parametrize("bad_latitude", [-91, 91])
def test_aeroplane_rejects_latitude_out_of_range(aeroplane_factory, bad_latitude) -> None:
    with pytest.raises(ValueError, match="Latitude must be between"):
        aeroplane_factory(latitude=bad_latitude)


@pytest.mark.parametrize("bad_icao24", ["", None, 123])
def test_aeroplane_rejects_non_string_or_empty_icao24(aeroplane_factory, bad_icao24) -> None:
    with pytest.raises(ValueError, match="icao24 must be a string"):
        aeroplane_factory(icao24=bad_icao24)


@pytest.mark.parametrize("bad_icao24", ["ABC12", "ABC1234", "ZZZZZZ"])
def test_aeroplane_rejects_invalid_icao24_format(aeroplane_factory, bad_icao24) -> None:
    with pytest.raises(ValueError, match="6-character hexadecimal"):
        aeroplane_factory(icao24=bad_icao24)


def test_cast_to_object_list_creates_aeroplane_objects() -> None:
    data = {
        "states": [
            ["abc123", "BEL123", "Belarus", 10, 20, 27.56, 53.90, 11_000, False, 250, 180],
            ["def456", "GER123", "Germany", 30, 40, 13.40, 52.52, 9_000, False, 300, 90],
        ]
    }

    planes = list(Aeroplane.cast_to_object_list(data))

    assert len(planes) == 2
    assert all(isinstance(plane, Aeroplane) for plane in planes)
    assert planes[0].icao24 == "abc123"
    assert planes[0].callsign == "BEL123"
    assert planes[0].country == "Belarus"
    assert planes[0].baro_altitude == 11_000
    assert planes[1].velocity == 300


def test_cast_to_object_list_uses_unknown_for_missing_callsign_and_country() -> None:
    data = {
        "states": [
            ["abc123", None, None, 10, 20, 27.56, 53.90, 11_000, False, 250, 180],
        ]
    }

    planes = list(Aeroplane.cast_to_object_list(data))

    assert len(planes) == 1
    assert planes[0].callsign == "UNKNOWN"
    assert planes[0].country == "UNKNOWN"


@pytest.mark.parametrize("bad_data", [[], {}, {"items": []}, None])
def test_cast_to_object_list_rejects_invalid_data_format(bad_data) -> None:
    with pytest.raises(ValueError, match="Invalid data format"):
        list(Aeroplane.cast_to_object_list(bad_data))


def test_cast_to_object_list_skips_short_and_invalid_rows() -> None:
    data = {
        "states": [
            ["short"],
            ["badhex", "BAD", "Belarus", 10, 20, 27.56, 53.90, 11_000, False, 250, 180],
            ["abc123", "OK", "Belarus", 10, 20, 27.56, 53.90, 11_000, False, 250, 180],
        ]
    }

    planes = list(Aeroplane.cast_to_object_list(data))

    assert len(planes) == 1
    assert planes[0].callsign == "OK"


def test_sort_by_altitude_returns_planes_descending(aeroplane_factory) -> None:
    low = aeroplane_factory(icao24="ABC001", callsign="LOW", baro_altitude=1_000)
    high = aeroplane_factory(icao24="ABC002", callsign="HIGH", baro_altitude=12_000)
    middle = aeroplane_factory(icao24="ABC003", callsign="MID", baro_altitude=6_000)

    result = Aeroplane.sort_by_altitude([low, high, middle])

    assert result == [high, middle, low]


def test_sort_by_velocity_returns_planes_descending(aeroplane_factory) -> None:
    slow = aeroplane_factory(icao24="ABC001", callsign="SLOW", velocity=100)
    fast = aeroplane_factory(icao24="ABC002", callsign="FAST", velocity=450)
    middle = aeroplane_factory(icao24="ABC003", callsign="MID", velocity=250)

    result = Aeroplane.sort_by_velocity([slow, fast, middle])

    assert result == [fast, middle, slow]


@pytest.mark.parametrize(
    "method_name",
    [
        "sort_by_altitude",
        "sort_by_velocity",
        "get_top_n_aeroplanes",
        "filter_aeroplanes",
        "filter_aeroplanes_by_altitude",
    ],
)
def test_list_methods_return_empty_list_for_empty_input(method_name: str) -> None:
    method = getattr(Aeroplane, method_name)

    if method_name == "get_top_n_aeroplanes":
        result = method([], 3)
    elif method_name == "filter_aeroplanes":
        result = method([], ["Belarus"])
    elif method_name == "filter_aeroplanes_by_altitude":
        result = method([], "1000-2000")
    else:
        result = method([])

    assert result == []


@pytest.mark.parametrize(
    "method_name,args",
    [
        ("sort_by_altitude", ()),
        ("sort_by_velocity", ()),
        ("get_top_n_aeroplanes", (3,)),
        ("filter_aeroplanes", (["Belarus"],)),
        ("filter_aeroplanes_by_altitude", ("1000-2000",)),
    ],
)
def test_list_methods_reject_non_aeroplane_items(method_name: str, args: tuple) -> None:
    method = getattr(Aeroplane, method_name)

    with pytest.raises(TypeError, match="All elements must be Aeroplane objects"):
        method(["not-a-plane"], *args)


def test_get_top_n_aeroplanes_returns_first_n_items(aeroplane_factory) -> None:
    first = aeroplane_factory(icao24="ABC001", callsign="FIRST")
    second = aeroplane_factory(icao24="ABC002", callsign="SECOND")
    third = aeroplane_factory(icao24="ABC003", callsign="THIRD")

    result = Aeroplane.get_top_n_aeroplanes([first, second, third], 2)

    assert result == [first, second]


def test_filter_aeroplanes_by_country_words(aeroplane_factory) -> None:
    belarus = aeroplane_factory(icao24="ABC001", callsign="BEL", country="Belarus")
    germany = aeroplane_factory(icao24="ABC002", callsign="GER", country="Germany")
    poland = aeroplane_factory(icao24="ABC003", callsign="POL", country="Poland")

    result = Aeroplane.filter_aeroplanes([belarus, germany, poland], ["Bel", "Ger"])

    assert result == [belarus, germany]


def test_filter_aeroplanes_returns_empty_when_no_words_match(aeroplane_factory) -> None:
    plane = aeroplane_factory(country="Belarus")

    result = Aeroplane.filter_aeroplanes([plane], ["Germany"])

    assert result == []


def test_filter_aeroplanes_by_altitude_range(aeroplane_factory) -> None:
    low = aeroplane_factory(icao24="ABC001", callsign="LOW", baro_altitude=1_000)
    middle = aeroplane_factory(icao24="ABC002", callsign="MID", baro_altitude=5_000)
    high = aeroplane_factory(icao24="ABC003", callsign="HIGH", baro_altitude=11_000)

    result = Aeroplane.filter_aeroplanes_by_altitude([low, middle, high], "2000-10000")

    assert result == [middle]


def test_filter_aeroplanes_by_altitude_accepts_spaces_around_dash(aeroplane_factory) -> None:
    plane = aeroplane_factory(baro_altitude=5_000)

    result = Aeroplane.filter_aeroplanes_by_altitude([plane], "1000 - 6000")

    assert result == [plane]


@pytest.mark.parametrize("bad_range", ["1000", "low-high"])
def test_filter_aeroplanes_by_altitude_rejects_invalid_range(aeroplane_factory, bad_range: str) -> None:
    plane = aeroplane_factory()

    with pytest.raises((ValueError, IndexError)):
        Aeroplane.filter_aeroplanes_by_altitude([plane], bad_range)


def test_aeroplane_comparison_by_altitude(aeroplane_factory) -> None:
    low = aeroplane_factory(icao24="ABC001", baro_altitude=1_000)
    high = aeroplane_factory(icao24="ABC002", baro_altitude=10_000)
    assert low < high
    assert high > low


def test_aeroplane_comparison_by_velocity(aeroplane_factory) -> None:
    slow = aeroplane_factory(icao24="ABC001", velocity=100)
    fast = aeroplane_factory(icao24="ABC002", velocity=500)
    assert slow < fast
    assert fast > slow
