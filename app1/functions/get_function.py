import datetime
from math import ceil

from django.http import JsonResponse
from django.db import connection
from app1.functions.validating_reformating import *


# vytiahne z pola GET dany parameter, skontroluje ci je platny, ak sa tam nenachadza vrati je default hodnotu
def extract_and_validate_data_from_get(request, pa_key, def_value):
    temp = request.GET.get(pa_key, def_value)
    if is_number(temp) is not None:
        return int(is_number(temp))
    else:
        return def_value


# vrati json s datami, ktore odpovedaju parametrom z pola GET
def get_list_from_get(request):
    # v dictionary params sa budu nachadzat dane argumenty na filtrovanie
    params = {}
    params["page"] = extract_and_validate_data_from_get(request, "page", 1)
    params["per_page"] = extract_and_validate_data_from_get(request, "per_page", 10)

    # overi, ci v order_by parametri je len to co tam ma byt
    params["order_by"] = request.GET.get("order_by", "id")
    columns = ["id", "br_court_name", "kind_name", "cin", "registration_date",
               "corporate_body_name", "br_section", "text", "street", "postal_code", "city"]
    if params["order_by"] not in columns:
        params["order_by"] = "id"

    # overi, ci v order_type parametri je len to co tam ma byt
    params["order_type"] = request.GET.get("order_type", "desc")
    columns = ["asc", "desc", "ASC", "DESC"]
    if params["order_type"] not in columns:
        params["order_type"] = "desc"

    # do vyhladavacieho stringu doplni %query%, kvoli matchovaniu pri vyhladavani
    query = request.GET.get("query", None)
    if query is not None:
        params["query"] = "%" + query + "%"

    # zvaliduje datum (parameter p_registration_date_lte)
    p_registration_date_lte = request.GET.get("registration_date_lte", None)
    try:
        if p_registration_date_lte is not None:
            datetime.datetime.strptime(p_registration_date_lte, '%Y-%m-%d %H:%M:%S.%f')
            params["registration_date_lte"] = p_registration_date_lte
    except ValueError:
        pass

    # zvaliduje datum (parameter registration_date_gte)
    p_registration_date_gte = request.GET.get("registration_date_gte", None)
    try:
        if p_registration_date_gte is not None:
            datetime.datetime.strptime(p_registration_date_gte, '%Y-%m-%d %H:%M:%S.%f')
            params["registration_date_gte"] = p_registration_date_gte
    except ValueError:
        pass

    cursor = connection.cursor()

    # vrati hlavne data
    order_by_string = " ORDER BY " + params["order_by"] + " " + params["order_type"] + """ LIMIT %s OFFSET %s ;"""
    query = """SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name,  br_section,
        br_insertion, text, street, postal_code, city FROM ov.or_podanie_issues WHERE ((1 = %s) OR (corporate_body_name
        ILIKE %s) OR (cin::varchar(255) = %s) OR (city ILIKE %s)) AND ((1 = %s) OR (registration_date <= %s)) AND ((1 =
        %s) OR (registration_date >= %s)) """
    query += order_by_string
    # nastavi parametre queriny
    query_params = (0 if "query" in params else 1,
                    str(1 if "query" not in params else params["query"]),
                    str(1 if "query" not in params else params["query"]),
                    str(1 if "query" not in params else params["query"]),
                    0 if "registration_date_lte" in params else 1,
                    str('2000-1-1' if "registration_date_lte" not in params else params["registration_date_lte"]),
                    0 if "registration_date_gte" in params else 1,
                    str('2000-1-1' if "registration_date_gte" not in params else params["registration_date_gte"]),
                    int(params["per_page"]),
                    ((int(params["page"]) - 1) * int(params["per_page"]))
                    )
    cursor.execute(query, query_params)
    row = cursor.fetchall()

    # zisti metadata
    query = """SELECT COUNT(id) FROM ov.or_podanie_issues WHERE ((1 = %s) OR (corporate_body_name ILIKE %s) OR (
    cin::varchar(255) = %s) OR (city ILIKE %s)) AND ((1 = %s) OR (registration_date <= %s)) AND ((1 = %s) OR (
    registration_date >= %s)) ; """
    query_params = query_params[0:-2]
    cursor.execute(query, query_params)
    count = cursor.fetchone()

    # vytvori metadata
    metadata = {"page": int(params["page"]), "per_page": int(params["per_page"]),
                "pages": int(ceil(count[0]/int(params["per_page"]))), "total": count[0]}
    return JsonResponse({"items": make_dict_from_data(row), "metadata": metadata}, status=200)
