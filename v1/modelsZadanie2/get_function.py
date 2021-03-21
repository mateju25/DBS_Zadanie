from math import ceil

from django.http import JsonResponse
from django.db import connection
from v1.modelsZadanie2.validating_reformating import *


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


# vrati json s datami, ktore odpovedaju parametrom z pola GET
def get_list_from_get(request):
    # v dictionary params sa budu nachadzat dane argumenty na filtrovanie
    params = {}
    params["page"] = extract_and_validate_data_from_get(request, "page", "1")
    if params["page"] == 0:
        params["page"] = 1
    params["per_page"] = extract_and_validate_data_from_get(request, "per_page", "10")

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
        params["query"] = "%" + query.lower() + "%"

    # zvaliduje datum (parameter p_registration_date_lte)
    p_registration_date_lte = request.GET.get("registration_date_lte", None)
    p_registration_date_lte = is_date(p_registration_date_lte)
    if p_registration_date_lte is not None:
        params["registration_date_lte"] = p_registration_date_lte

    # zvaliduje datum (parameter registration_date_gte)
    p_registration_date_gte = request.GET.get("registration_date_gte", None)
    p_registration_date_gte = is_date(p_registration_date_gte)
    if p_registration_date_gte is not None:
        params["registration_date_gte"] = p_registration_date_gte


    cursor = connection.cursor()

    # vysklada podmienky
    query_params = ()
    order_by_string = " ORDER BY " + params["order_by"] + " " + params["order_type"] + """ LIMIT %s OFFSET %s ;"""
    where_clause = """"""
    if "query" in params or "registration_date_lte" in params or "registration_date_gte" in params:
        where_clause += """ WHERE (1=1) """
    if "query" in params:
        where_clause += """AND ((corporate_body_name ILIKE %s) OR (cin::varchar(255) ILIKE %s) OR (city ILIKE %s)) """
        query_params += (str(params["query"]), str(params["query"]), str(params["query"]),)

    if "registration_date_lte" in params:
        where_clause += """AND (registration_date <= %s) """
        query_params += (str(params["registration_date_lte"]),)

    if "registration_date_gte" in params:
        where_clause += """AND (registration_date >= %s) """
        query_params += (str(params["registration_date_gte"]),)

    # zisti metadata
    query = """SELECT COUNT(id) FROM ov.or_podanie_issues """ + where_clause
    if len(query_params) != 0:
        cursor.execute(query, query_params)
    else:
        cursor.execute(query)
    print(cursor.query)
    count = cursor.fetchone()

    # zisti hlavny data
    row = []
    if not (int(ceil(count[0]/int(params["per_page"]))) < (int(params["page"]))):
        query = """SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name,  br_section,  br_insertion, text, street, postal_code, city FROM ov.or_podanie_issues"""
        query += where_clause + order_by_string
        query_params += (int(params["per_page"]), ((int(params["page"]) - 1) * int(params["per_page"])),)
        cursor.execute(query, query_params)
        print(cursor.query)
        row = cursor.fetchall()

    cursor.close()

    # vytvori metadata
    metadata = {"page": int(params["page"]), "per_page": int(params["per_page"]),
                "pages": int(ceil(count[0]/int(params["per_page"]))), "total": count[0]}
    return JsonResponse({"items": make_dict_from_data(row), "metadata": metadata}, status=200)
