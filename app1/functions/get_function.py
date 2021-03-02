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
    page = extract_data_from_get(request, "page", "1", pa_is_number=True)
    per_page = extract_data_from_get(request, "per_page", "10",  pa_is_number=True)
    order_by = extract_data_from_get(request, "order_by", None)
    order_type = extract_data_from_get(request, "order_type", None)
    corporate_body_name = extract_data_from_get(request, "corporate_body_name", None)
    if corporate_body_name is not None:
        corporate_body_name = "%" + str(corporate_body_name) + "%"
    cin = extract_data_from_get(request, "cin", None)
    if cin is not None:
        cin = "%" + str(cin) + "%"
    city = extract_data_from_get(request, "city", None)
    if city is not None:
        city = "%" + str(city) + "%"
    registration_date_lte = extract_data_from_get(request, "registration_date_lte", None)
    if registration_date_lte is not None:
        registration_date_lte = (registration_date_lte.split())[0]
    registration_date_gte = extract_data_from_get(request, "registration_date_gte", None)
    if registration_date_gte is not None:
        registration_date_gte = (registration_date_gte.split())[0]

    if order_by is not None:
        order_by_statement = "ORDER BY "
        if order_type in ["asc", "desc"]:
            order_by_statement = order_by_statement + order_by + " " + order_type + " "
        else:
            order_by_statement = order_by_statement + order_by + " "
    else:
        order_by_statement = ""

    cursor = connection.cursor()
    cursor.execute("PREPARE get_list(text, int, text, int, date, int, date, int, int, int) AS "
                   "SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name, "
                   "br_section, br_insertion, text, street, postal_code, city FROM ov.or_podanie_issues "
                   "WHERE ((corporate_body_name = $1) OR (cin = $2) OR (city = $3) OR (1 = $4)) "
                   "AND ((registration_date <= $5) OR (1 = $6)) AND ((registration_date >= $7) OR (1 = $8)) "
                   + order_by_statement +
                   "LIMIT $9 OFFSET $10; ")
    cursor.execute("PREPARE get_count(text, int, text, int, date, int, date, int) AS "
                   "SELECT COUNT(id) "
                   "FROM ov.or_podanie_issues "
                   "WHERE ((corporate_body_name = $1) OR (cin = $2) OR (city = $3) OR (1 = $4)) "
                   "AND ((registration_date <= $5) OR (1 = $6)) AND ((registration_date >= $7) OR (1 = $8)) ")

    if corporate_body_name is None and cin is None and city is None:
        search_cond = 1
    else:
        search_cond = 0

    query = "EXECUTE get_list({}, {}, {}, {}, {}, {}, {}, {}, {}, {});".format(
        "'" + str(1 if corporate_body_name is None else corporate_body_name) + "'",
        str(1 if cin is None else cin),
        "'" + str(1 if city is None else cin) + "'",
        str(search_cond),
        "'" + str('2000-1-1' if registration_date_lte is None else registration_date_lte) + "'",
        1 if registration_date_lte is None else 0,
        "'" + str('2000-1-1' if registration_date_gte is None else registration_date_gte) + "'",
        1 if registration_date_gte is None else 0,
        str(per_page),
        str(page * per_page)
    )

    cursor.execute(query)
    row = cursor.fetchall()

    query = "EXECUTE get_count({}, {}, {}, {}, {}, {}, {}, {});".format(
        "'" + str(1 if corporate_body_name is None else corporate_body_name) + "'",
        str(1 if cin is None else cin),
        "'" + str(1 if city is None else cin) + "'",
        str(search_cond),
        "'" + str('2000-1-1' if registration_date_lte is None else registration_date_lte) + "'",
        1 if registration_date_lte is None else 0,
        "'" + str('2000-1-1' if registration_date_gte is None else registration_date_gte) + "'",
        1 if registration_date_gte is None else 0
    )

    cursor.execute(query)
    count = cursor.fetchone()

    metadata = {"page": page, "per_page": per_page, "pages": int(ceil(count[0]/per_page)), "total": count[0]}
    #metadata = {"page": page, "per_page": per_page, "pages": "?", "total": "?"}
    return JsonResponse({"items": make_dict_from_data(row), "metadata": metadata})
