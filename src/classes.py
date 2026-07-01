import json
import os.path
from abc import ABC, abstractmethod
from typing import Iterator

from requests import get

from src.utils import find_project_root


class BaseAPIAdapter(ABC):

    @abstractmethod
    def __init__(self) -> None:
        self.openstreetmap_url = ""
        self.opensky_url = ""

    @abstractmethod
    def get_aeroplanes(self, country: str) -> dict:
        pass


class APIAdapter(BaseAPIAdapter):

    def __init__(self) -> None:
        self.openstreetmap_url = "https://nominatim.openstreetmap.org/search"
        self.opensky_url = "https://opensky-network.org/api/states/all?"

    def get_aeroplanes(self, country: str) -> dict:
        # Headers с user-agent - обязательный параметр при запросе к nominatim.openstreetmap.
        # Вы можете использовать любое название вместо test-app/1.0, например просто test-app.
        headers_nominatim = {
            "User-Agent": "test-app/1.0",
        }

        # Указываем параметры: в каком формате возвращать данные и максимальную длину списка стран в ответе.
        params_nominatim = {
            "country": country,
            "format": "json",
            "limit": 1,
        }

        response = get(
            url=self.openstreetmap_url,
            params=params_nominatim, #type: ignore
            headers=headers_nominatim,
        )

        data = response.json()

        # Пример ответа от nominatim.openstreetmap можно посмотреть в задании курсовой.
        geo_coordinates = data[0].get("boundingbox")

        # Параметры для фильтрации самолетов по их географическим координатам.
        params = {
            "lamin": geo_coordinates[0],
            "lamax": geo_coordinates[1],
            "lomin": geo_coordinates[2],
            "lomax": geo_coordinates[3],
        }

        response = get(url=self.opensky_url, params=params)

        # Пример ответа от opensky-network можно посмотреть в задании курсовой.
        aeroplanes = response.json()
        return aeroplanes #type: ignore


class AeroplanesAPI(APIAdapter):

    def __init__(self) -> None:
        super().__init__()


class Aeroplane:
    """
    Класс для работы с самолетами.
    """

    def __init__(
        self,
        callsign: str,
        country: str,
        velocity: int | float,
        baro_altitude: int | float,
        icao24: str | None = None,
        time_position: int | float | None = None,
        last_contact: int | float | None = None,
        longitude: float | int | None = None,
        latitude: float | int | None = None,
        on_ground: bool | None = None,
        true_track: int | float | None = None,
        vertical_rate: int | float | None = None,
        sensors: list | None = None,
        geo_altitude: int | float | None = None,
        squawk: str | None = None,
        spi: bool | None = None,
        position_source: int | float | None = None,
    ) -> None:

        if not callsign or not isinstance(callsign, str):
            raise ValueError("callsign must be a non-empty string")
        if not country or not isinstance(country, str):
            raise ValueError("country must be a non-empty string")

        if not velocity or not isinstance(velocity, (int, float)):
            raise ValueError("Velocity must be a number")
        if velocity < 0:
            raise ValueError("Velocity cannot be negative")

        if not baro_altitude or not isinstance(baro_altitude, (int, float)):
            raise ValueError("Baro altitude must be a number")

        if not longitude or not isinstance(longitude, (int, float)):
            raise ValueError("Longitude must be a number")
        if not -180 <= longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees")

        if not latitude or not isinstance(latitude, (int, float)):
            raise ValueError("Latitude must be a number")
        if not -90 <= latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees")

        if not icao24 or not isinstance(icao24, str):
            raise ValueError("icao24 must be a string")
        if len(icao24) != 6 or not all(c in "0123456789ABCDEF" for c in icao24.upper()):
            raise ValueError("icao24 must be a 6-character hexadecimal string")

        self.icao24 = icao24
        self.callsign = callsign
        self.country = country
        self.time_position = time_position
        self.last_contact = last_contact
        self.longitude = longitude
        self.latitude = latitude
        self.baro_altitude = baro_altitude
        self.on_ground = on_ground
        self.velocity = velocity
        self.true_track = true_track
        self.vertical_rate = vertical_rate
        self.sensors = sensors
        self.geo_altitude = geo_altitude
        self.squawk = squawk
        self.spi = spi
        self.position_source = position_source

    @classmethod
    def cast_to_object_list(cls, data: list) -> Iterator:
        """Создает список объектов Aeroplane из данных"""
        if not isinstance(data, dict) or "states" not in data:
            raise ValueError("Invalid data format: expected dict with 'states' key")

        for plane in data["states"]:
            # Пропускаем некорректные записи
            if len(plane) < 11:
                continue
            try:
                yield cls(
                    icao24=plane[0],
                    callsign=plane[1] if plane[1] else "UNKNOWN",
                    country=plane[2] if plane[2] else "UNKNOWN",
                    time_position=plane[3],
                    last_contact=plane[4],
                    longitude=plane[5],
                    latitude=plane[6],
                    baro_altitude=plane[7],
                    on_ground=plane[8],
                    velocity=plane[9] if plane[9] is not None else 0,
                    true_track=plane[10],
                )
            except ValueError:
                pass

    @staticmethod
    def sort_by_altitude(planes: list) -> list:
        """Сортирует список самолетов по высоте"""
        if not planes:
            return []
        if not all(isinstance(p, Aeroplane) for p in planes):
            raise TypeError("All elements must be Aeroplane objects")
        return sorted(
            planes,
            key=lambda x: x.baro_altitude if x.baro_altitude is not None else 0,
            reverse=True,
        )

    @staticmethod
    def sort_by_velocity(planes: list) -> list:
        """Сортирует список самолетов по скорости"""
        if not planes:
            return []
        if not all(isinstance(p, Aeroplane) for p in planes):
            raise TypeError("All elements must be Aeroplane objects")
        return sorted(
            planes,
            key=lambda x: x.velocity if x.velocity is not None else 0,
            reverse=True,
        )

    @staticmethod
    def get_top_n_aeroplanes(planes: list, n: int) -> list:
        """Возвращает n самых быстрых самолетов"""
        if not planes:
            return []
        if not all(isinstance(p, Aeroplane) for p in planes):
            raise TypeError("All elements must be Aeroplane objects")
        return planes[:n]

    @staticmethod
    def filter_aeroplanes(planes: list, filter_words: list) -> list:
        """Фильтрует самолеты по стране регистрации"""
        if not planes:
            return []
        if not all(isinstance(p, Aeroplane) for p in planes):
            raise TypeError("All elements must be Aeroplane objects")
        return [p for p in planes if any(word in p.country for word in filter_words)]

    @staticmethod
    def filter_aeroplanes_by_altitude(planes: list, altitude_range: str) -> list:
        """Возвращает самолеты в заданном диапазоне высот"""
        if not planes:
            return []
        if not all(isinstance(p, Aeroplane) for p in planes):
            raise TypeError("All elements must be Aeroplane objects")
        altitude_range = [int(x) for x in altitude_range.split("-")] # type: ignore
        return [p for p in planes if altitude_range[0] <= p.baro_altitude <= altitude_range[1]]


class BaseJsonSaver(ABC):
    """Абстрактный класс для сохранения данных в файл"""

    @staticmethod
    @abstractmethod
    def save(data: list) -> None:
        """Сохраняет данные в файл"""

    @staticmethod
    @abstractmethod
    def load() -> list:
        """Загружает данные из файла"""

    @staticmethod
    @abstractmethod
    def delete(data: list) -> None:
        """Удаляет данные из файла"""


class JsonSaver(BaseJsonSaver):
    """Класс для сохранения данных в файл"""

    @staticmethod
    def add_aeroplane(aeroplane: Aeroplane) -> None:
        """Добавляет самолет в файл"""
        with open(f"{find_project_root()}/data/data.json", "r", encoding="utf-8") as rf:
            if os.path.getsize(f"{find_project_root()}/data/data.json") > 0:
                data = json.load(rf)
            else:
                data = []

        with open(f"{find_project_root()}/data/data.json", "w", encoding="utf-8") as af:
            if not data:
                data = []
            data.append(aeroplane.__dict__)
            json.dump(data, af, indent=4)

    @staticmethod
    def load() -> list:
        with open(f"{find_project_root()}/data/data.json", "r", encoding="utf-8") as f:
            return json.load(f) # type: ignore

    @staticmethod
    def delete_aeroplane(aeroplane: Aeroplane) -> None:
        try:

            with open(f"{find_project_root()}/data/data.json", "r", encoding="utf-8") as f:
                if os.path.getsize(f"{find_project_root()}/data/data.json") > 0:
                    all_data = json.load(f)
                else:
                    return

            all_data.remove(aeroplane.__dict__)

            with open(f"{find_project_root()}/data/data.json", "w", encoding="utf-8") as f:
                json.dump(all_data, f, indent=4)

        except ValueError:
            print("Aeroplane not found")
