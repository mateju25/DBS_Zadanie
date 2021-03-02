from math import ceil

from django.http import JsonResponse
from django.db import connection
from app1.functions.sql_defense import *


# vytvori z listu listov, list slovnikov (kvoli zadaniu)
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


# vytiahne z pola GET dany parameter, skontroluje ci je platny, ak sa tam nenachadza vrati je default hodnotu
def extract_data_from_get(request, pa_key, def_value, pa_is_number=False):
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


# vrati json s datami, ktore odpovedaju parametrom z pola GET
def get_list_from_get(request):
    p_page = extract_data_from_get(request, "page", "1", pa_is_number=True)
    p_per_page = extract_data_from_get(request, "per_page", "10",  pa_is_number=True)
    p_order_by = extract_data_from_get(request, "order_by", None)
    p_order_type = extract_data_from_get(request, "order_type", None)
    p_query = extract_data_from_get(request, "query", None)
    if p_query is not None:
        p_query = "%" + str(p_query) + "%"
    p_registration_date_lte = extract_data_from_get(request, "registration_date_lte", None)
    if p_registration_date_lte is not None:
        p_registration_date_lte = (p_registration_date_lte.split())[0]
    p_registration_date_gte = extract_data_from_get(request, "registration_date_gte", None)
    if p_registration_date_gte is not None:
        p_registration_date_gte = (p_registration_date_gte.split())[0]

    if p_order_by is not None:
        order_by_statement = "ORDER BY "
        if p_order_type in ["asc", "desc"]:
            order_by_statement = order_by_statement + str(p_order_by) + " " + p_order_type + " "
        else:
            order_by_statement = order_by_statement + str(p_order_by) + " "
    else:
        order_by_statement = ""

    cursor = connection.cursor()
    cursor.execute("PREPARE get_list(text, int, date, int, date, int, int, int) AS "
                   "SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name, "
                   "br_section, br_insertion, text, street, postal_code, city FROM ov.or_podanie_issues "
                   "WHERE ((corporate_body_name ILIKE $1) OR (cin::varchar(255) = $1) OR (city ILIKE $1) OR (1 = $2)) "
                   "AND ((registration_date <= $3) OR (1 = $4)) AND ((registration_date >= $5) OR (1 = $6)) "
                   + order_by_statement +
                   "LIMIT $7 OFFSET $8; ")
    cursor.execute("PREPARE get_count(text, int, date, int, date, int) AS "
                   "SELECT COUNT(id) "
                   "FROM ov.or_podanie_issues "
                   "WHERE ((corporate_body_name ILIKE $1) OR (cin::varchar(255) = $1) OR (city ILIKE $1) OR (1 = $2)) "
                   "AND ((registration_date <= $3) OR (1 = $4)) AND ((registration_date >= $5) OR (1 = $6)) ")

    if p_query is None:
        search_cond = 1
    else:
        search_cond = 0

    query = "EXECUTE get_list({}, {}, {}, {}, {}, {}, {}, {});".format(
        "'" + str(1 if p_query is None else p_query) + "'",
        str(search_cond),
        "'" + str('2000-1-1' if p_registration_date_lte is None else p_registration_date_lte) + "'",
        1 if p_registration_date_lte is None else 0,
        "'" + str('2000-1-1' if p_registration_date_gte is None else p_registration_date_gte) + "'",
        1 if p_registration_date_gte is None else 0,
        str(p_per_page),
        str(p_page * p_per_page)
    )

    cursor.execute(query)
    row = cursor.fetchall()

    query = "EXECUTE get_count({}, {}, {}, {}, {}, {});".format(
        "'" + str(1 if p_query is None else p_query) + "'",
        str(search_cond),
        "'" + str('2000-1-1' if p_registration_date_lte is None else p_registration_date_lte) + "'",
        1 if p_registration_date_lte is None else 0,
        "'" + str('2000-1-1' if p_registration_date_gte is None else p_registration_date_gte) + "'",
        1 if p_registration_date_gte is None else 0
    )

    cursor.execute(query)
    count = cursor.fetchone()

    metadata = {"page": p_page, "per_page": p_per_page, "pages": int(ceil(count[0]/p_per_page)), "total": count[0]}
    return JsonResponse({"items": make_dict_from_data(row), "metadata": metadata})
