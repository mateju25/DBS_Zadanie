import re

from django.http import JsonResponse
from django.db import connection


def is_string(pa_string):
    prog = re.compile("^[a-zA-Z_]+$")
    if prog.match(pa_string):
        return pa_string
    else:
        return None


def is_number(pa_string):
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


def get_list_from_GET(request):
    page = request.GET.get("page", '1')
    page = is_number(page)
    if page is None:
        return JsonResponse({"Error" : "Volam sandare."})

    per_page = request.GET.get("per_page", '10')
    per_page = is_number(per_page)
    if per_page is None:
        return JsonResponse({"Error": "Volam sandare."})

    cursor = connection.cursor()
    query = "SELECT " \
            + "id, " \
            + "br_court_name, " \
            + "kind_name, " \
            + "cin, " \
            + "registration_date, " \
            + "corporate_body_name, " \
            + "br_section, " \
            + "br_insertion, " \
            + "text, " \
            + "street, " \
            + "postal_code, " \
            + "city " \
            + "FROM ov.or_podanie_issues "
    query = query + "LIMIT " + str(per_page)
    query = query + "OFFSET " + str(page * per_page) + ";"

    cursor.execute(query)
    row = cursor.fetchall()

    # query = "SELECT COUNT(id) FROM ov.or_podanie_issues;"
    # cursor.execute(query)
    # count = cursor.fetchone()

    #metadata = {"page": page, "per_page": per_page, "pages": int(ceil(count[0]/per_page)), "total": count[0]}
    metadata = {"page": page, "per_page": per_page, "pages": "?", "total": "?"}
    return JsonResponse({"items": make_dict_from_data(row), "metadata": metadata})
