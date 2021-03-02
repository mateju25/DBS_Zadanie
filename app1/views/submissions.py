import re
from math import ceil

from django.http import JsonResponse
from django.db import connection


def is_string(pa_string):
    if pa_string is None:
        return None
    prog = re.compile("^[0-9a-zA-Z_., :-]+$")
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
            "registration_date": str(x[4]),
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
            return int(is_number(temp))
        else:
            return def_value
    else:
        if is_string(temp) is not None:
            return is_string(temp)
        else:
            return def_value


def get_list_from_get(request):
    page = extract_data_from_get(request, "page", "1")
    per_page = extract_data_from_get(request, "per_page", "10")
    order_by = extract_data_from_get(request, "order_by", None, pa_is_number=False)
    order_type = extract_data_from_get(request, "order_type", None, pa_is_number=False)
    corporate_body_name = extract_data_from_get(request, "corporate_body_name", None, pa_is_number=False)
    cin = extract_data_from_get(request, "cin", None)
    city = extract_data_from_get(request, "city", None, pa_is_number=False)
    registration_date_lte = (extract_data_from_get(request, "registration_date_lte", None, pa_is_number=False)).split()[0]
    registration_date_gte = (extract_data_from_get(request, "registration_date_gte", None, pa_is_number=False)).split()[0]

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
    count_query = "SELECT COUNT(id) FROM ov.or_podanie_issues "

    if corporate_body_name is not None or cin is not None or city is not None:
        count_query = count_query + "WHERE (2 = 1"
        query = query + "WHERE (2 = 1"
        if corporate_body_name is not None:
            query = query + " OR corporate_body_name = '" + corporate_body_name + "' "
            count_query = count_query + " OR corporate_body_name = '" + corporate_body_name + "' "
        if cin is not None:
            query = query + " OR cin = " + str(cin) + " "
            count_query = count_query + " OR cin = " + str(cin) + " "
        if city is not None:
            query = query + " OR city = '" + city + "' "
            count_query = count_query + " OR city = '" + city + "' "

        count_query = count_query + ") "
        query = query + ") "

    if registration_date_lte is not None or registration_date_gte is not None:
        count_query = count_query + "AND ( 1 = 1 "
        query = query + "AND ( 1 = 1 "
        if registration_date_lte is not None:
            query = query + "AND registration_date <= '" + registration_date_lte + "' "
            count_query = count_query + "AND registration_date <= '" + registration_date_lte + "' "
        if registration_date_gte is not None:
            query = query + "AND registration_date >= '" + registration_date_gte + "' "
            count_query = count_query + "AND registration_date >= '" + registration_date_gte + "' "
        count_query = count_query + ") "
        query = query + ") "

    if order_by is not None and order_by in columns:
        query = query + "ORDER BY " + order_by + " "
    if order_type is not None and order_type in ["asc", "desc"]:
        query = query + order_type + " "

    query = query + "LIMIT " + str(per_page) + " "
    query = query + "OFFSET " + str(page * per_page)

    cursor.execute(query)
    row = cursor.fetchall()

    cursor.execute(count_query)
    count = cursor.fetchone()

    metadata = {"page": page, "per_page": per_page, "pages": int(ceil(count[0]/per_page)), "total": count[0]}
    #metadata = {"page": page, "per_page": per_page, "pages": "?", "total": "?"}
    return JsonResponse({"items": make_dict_from_data(row), "metadata": metadata})
