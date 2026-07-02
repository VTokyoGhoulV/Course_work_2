from pathlib import Path


def user_interaction() -> tuple:
    country = input("Введите название страны: ")
    top_n = int(input("Введите количество самолетов для вывода в топ N: "))
    filter_words = input("Введите названия стран для фильтрации по стране регистрации: ").split()
    altitude_range = input("Введите диапазон высот полета: ")  # Пример: 100000 - 150000
    return country, top_n, filter_words, altitude_range


def find_project_root(marker_files: str | tuple = ("pyproject.toml", ".git", "requirements.txt")) -> Path:
    """
    Ищет корневую директорию проекта, поднимаясь по дереву папок,
    пока не найдет один из маркерных файлов/папок.
    """
    current_path = Path.cwd()  # Начинаем с текущей рабочей директории
    for parent in [current_path] + list(current_path.parents):
        for marker in marker_files:
            if (parent / marker).exists():
                return parent
    raise RuntimeError("Не удалось найти корень проекта. Убедитесь, что один из маркерных файлов присутствует.")


def print_aeroplanes(aeroplanes: list) -> None:
    """
    Выводит список самолетов в консоль.
    """
    if not aeroplanes:
        print("Нет самолетов")
        return
    print(f"Найдено {len(aeroplanes)} самолетов:")
    for plane in aeroplanes:
        print(
            f"Позывной: {plane.callsign} "
            f"страна: {plane.country} "
            f"скорость: {plane.velocity} "
            f"высота: {plane.baro_altitude}"
        )