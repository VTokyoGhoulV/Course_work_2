from src.classes import Aeroplane, AeroplanesAPI, JsonSaver
from src.utils import user_interaction, print_aeroplanes

country, top_n, filter_words, altitude_range = user_interaction()

response = AeroplanesAPI().get_aeroplanes(country)

aeroplanes = list(Aeroplane.cast_to_object_list(response))  # type: ignore

filtered_aeroplanes = Aeroplane.filter_aeroplanes(aeroplanes, filter_words)

ranged_aeroplanes = Aeroplane.filter_aeroplanes_by_altitude(filtered_aeroplanes, altitude_range)

sorted_aeroplanes = Aeroplane.sort_by_altitude(ranged_aeroplanes)
top_aeroplanes = Aeroplane.get_top_n_aeroplanes(sorted_aeroplanes, top_n)
print_aeroplanes(top_aeroplanes)

for plane in top_aeroplanes:
    JsonSaver.add_aeroplane(plane)