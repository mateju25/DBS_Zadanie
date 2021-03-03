import datetime
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

    params = {}
    params["page"] = extract_data_from_get(request, "page", "1", pa_is_number=True)
    params["per_page"] = extract_data_from_get(request, "per_page", "10", pa_is_number=True)

    params["order_by"] = request.GET.get("order_by", "id")
    columns = ["id", "br_court_name", "kind_name", "cin", "registration_date",
               "corporate_body_name", "br_section", "text", "street", "postal_code", "city"]
    if params["order_by"] not in columns:
        params["order_by"] = "id"

    params["order_type"] = request.GET.get("order_type", "desc")
    columns = ["asc", "desc", "ASC", "DESC"]
    if params["order_type"] not in columns:
        params["order_type"] = "desc"

    query = extract_data_from_get(request, "query", None)
    if query is not None:
        params["query"] = query

    p_registration_date_lte = request.GET.get("registration_date_lte", None)
    try:
        if p_registration_date_lte is not None:
            datetime.datetime.strptime(p_registration_date_lte, '%Y-%m-%d %H:%M:%S.%f')
            params["registration_date_lte"] = p_registration_date_lte
    except ValueError:
        pass

    p_registration_date_gte = request.GET.get("registration_date_gte", None)
    try:
        if p_registration_date_gte is not None:
            datetime.datetime.strptime(p_registration_date_gte, '%Y-%m-%d %H:%M:%S.%f')
            params["registration_date_gte"] = p_registration_date_gte
    except ValueError:
        pass

    cursor = connection.cursor()
    cursor.execute("PREPARE get_list(text, int, date, int, date, int, int, int) AS "
                   "SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name, "
                   "br_section, br_insertion, text, street, postal_code, city FROM ov.or_podanie_issues "
                   "WHERE ((1 = $2) OR (corporate_body_name ILIKE $1) OR (cin::varchar(255) = $1) OR (city ILIKE $1)) "
                   "AND ((1 = $4) OR (registration_date <= $3)) AND ((1 = $6) OR (registration_date >= $5)) "
                   "ORDER BY " + params["order_by"] + " " + params["order_type"] +
                   " LIMIT $7 OFFSET $8; ")
    cursor.execute("PREPARE get_count(text, int, date, int, date, int) AS "
                   "SELECT COUNT(id) "
                   "FROM ov.or_podanie_issues "
                   "WHERE ((1 = $2) OR (corporate_body_name ILIKE $1) OR (cin::varchar(255) = $1) OR (city ILIKE $1)) "
                   "AND ((1 = $4) OR (registration_date <= $3)) AND ((1 = $6) OR (registration_date >= $5)) ")

    query = "EXECUTE get_list({}, {}, {}, {}, {}, {}, {}, {});".format(
        "'" + str(1 if "query" not in params else params["query"]) + "'",
        0 if "query" in params else 1,
        "'" + str('2000-1-1' if "registration_date_lte" not in params else params["registration_date_lte"]) + "'",
        0 if "registration_date_lte" in params else 1,
        "'" + str('2000-1-1' if "registration_date_gte" not in params else params["registration_date_gte"]) + "'",
        0 if "registration_date_gte" in params else 1,
        int(params["per_page"]),
        ((int(params["page"])-1) * int(params["per_page"]))
    )

    cursor.execute(query)
    row = cursor.fetchall()

    query = "EXECUTE get_count({}, {}, {}, {}, {}, {});".format(
        "'" + str(1 if "query" not in params else params["query"]) + "'",
        0 if "query" in params else 1,
        "'" + str('2000-1-1' if "registration_date_lte" not in params else params["registration_date_lte"]) + "'",
        0 if "registration_date_lte" in params else 1,
        "'" + str('2000-1-1' if "registration_date_gte" not in params else params["registration_date_gte"]) + "'",
        0 if "registration_date_gte" in params else 1
    )

    cursor.execute(query)

    count = cursor.fetchone()

    metadata = {"page": int(params["page"]), "per_page": int(params["per_page"]),
                "pages": int(ceil(count[0]/int(params["per_page"]))), "total": count[0]}
    return JsonResponse({"items": make_dict_from_data(row), "metadata": metadata})
