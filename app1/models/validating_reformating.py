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


# vytvori z listu listov, list slovnikov (kvoli zadaniu)
def make_dict_from_data(pa_data):
    result = []
    for x in pa_data:
        result.append({
            "id": x[0],
            "br_court_name": x[1],
            "kind_name": x[2],
            "cin": x[3],
            "registration_date": x[4],
            "corporate_body_name": x[5],
            "br_section": x[6],
            "br_insertion": x[7],
            "text": x[8],
            "street": x[9],
            "postal_code": x[10],
            "city": x[11]
        })
    return result