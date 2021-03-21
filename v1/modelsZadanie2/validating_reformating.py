from datetime import datetime
import re


# ak je string zo spravnymi znakmi vrati ho skonvertovany na cislo, inak vrati None
def is_number(pa_string):
    if pa_string is None:
        return None
    prog = re.compile("^[0-9]+$")
    if prog.match(pa_string):
        return int(pa_string)
    else:
        return None


def is_date(pa_string):
    if pa_string is None:
        return None
    try:
        temp = datetime.fromisoformat(pa_string)
        return datetime.strftime(temp, '%Y-%m-%d')
    except ValueError:
        return None


# vytiahne z pola GET dany parameter, skontroluje ci je platny, ak sa tam nenachadza vrati je default hodnotu
def extract_and_validate_data_from_get(request, pa_key, def_value):
    temp = request.GET.get(pa_key, def_value)
    if is_number(temp) is not None:
        return int(is_number(temp))
    else:
        return def_value
