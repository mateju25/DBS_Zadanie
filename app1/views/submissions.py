import re

from django.http import JsonResponse
from django.db import connection


def is_string(pa_string):
    if pa_string is None:
        return None
    prog = re.compile("^[a-zA-Z_]+$")
    if prog.match(pa_string):
        return pa_string
    else:
        return None


def is_number(pa_string):
    if pa_string is None:
        return None
    prog = re.compile("^[0-9]+$")
    if prog.match(pa_string):
        return int(pa_string)
    else:
        return None


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


def extract_data_from_get(request, pa_key, def_value, pa_is_number=True):
    temp = request.GET.get(pa_key, def_value)
    if pa_is_number:
        if is_number(temp) is not None:
            return is_number(temp)
        else:
            return int(def_value)
    else:
        if is_string(temp) is not None:
            return is_string(temp)
        else:
            return def_value


def get_list_from_GET(request):
    page = extract_data_from_get(request, "page", "1")
    per_page = extract_data_from_get(request, "per_page", "10")
    order_by = extract_data_from_get(request, "order_by", None, pa_is_number=False)

    cursor = connection.cursor()
    columns = ["id", "br_court_name", "kind_name", "cin", "registration_date", "corporate_body_name",
               "br_section", "br_insertion", "text", "street", "postal_code", "city"]
    query = "SELECT "
    for x in columns:
        if x is columns[len(columns)-1]:
            query = query + x + " "
        else:
            query = query + x + ", "
    query = query + "FROM ov.or_podanie_issues "
    query = query + "LIMIT " + str(per_page) + " "
    query = query + "OFFSET " + str(page * per_page) + ";"

    cursor.execute(query)
    row = cursor.fetchall()

    # query = "SELECT COUNT(id) FROM ov.or_podanie_issues;"
    # cursor.execute(query)
    # count = cursor.fetchone()

    #metadata = {"page": page, "per_page": per_page, "pages": int(ceil(count[0]/per_page)), "total": count[0]}
    metadata = {"page": page, "per_page": per_page, "pages": "?", "total": "?"}
    return JsonResponse({"items": make_dict_from_data(row), "metadata": metadata})
