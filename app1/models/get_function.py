import datetime
import time
from math import ceil
import threading

from django.http import JsonResponse
from django.db import connection
from app1.models.validating_reformating import *


# vytiahne z pola GET dany parameter, skontroluje ci je platny, ak sa tam nenachadza vrati je default hodnotu
def extract_and_validate_data_from_get(request, pa_key, def_value):
    temp = request.GET.get(pa_key, def_value)
    if is_number(temp) is not None:
        return int(is_number(temp))
    else:
        return def_value


break_thread = 2
result = None
row = None


# vrati metadata
def get_metadata(query, params):
    global break_thread, row
    cursor = connection.cursor()
    if len(params) != 0:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    print("Metadata ", end="")
    print(cursor.query)
    row = cursor.fetchone()
    break_thread-=1


# vrati data pre hlavny response
def get_data_from_database(query, params):
    global break_thread, result
    cursor = connection.cursor()
    cursor.execute(query, params)
    print("Data ", end="")
    print(cursor.query)
    result = cursor.fetchall()
    break_thread-=1


# refreshuje spojenie
def refresh_database():
    global break_thread
    cursor = connection.cursor()
    while break_thread != 0:
        for i in range(0, 120):
            time.sleep(1)
            if break_thread == 0:
                print("Vypinam")
                return
        cursor.execute("SELECT id FROM ov.likvidator_issues LIMIT 1;")
        print("Refresh", end='')
        print(cursor.query)
        res = cursor.fetchone()


# vrati json s datami, ktore odpovedaju parametrom z pola GET
def get_list_from_get(request):
    # v dictionary params sa budu nachadzat dane argumenty na filtrovanie
    global break_thread, row
    params = {}
    params["page"] = extract_and_validate_data_from_get(request, "page", "1")
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
        params["query"] = "%" + query + "%"

    # zvaliduje datum (parameter p_registration_date_lte)
    p_registration_date_lte = request.GET.get("registration_date_lte", None)
    try:
        if p_registration_date_lte is not None:
            datetime.datetime.strptime(p_registration_date_lte, '%Y-%m-%d %H:%M:%S.%f')
            params["registration_date_lte"] = (p_registration_date_lte.split())[0]
    except ValueError:
        pass

    # zvaliduje datum (parameter registration_date_gte)
    p_registration_date_gte = request.GET.get("registration_date_gte", None)
    try:
        if p_registration_date_gte is not None:
            datetime.datetime.strptime(p_registration_date_gte, '%Y-%m-%d %H:%M:%S.%f')
            params["registration_date_gte"] = (p_registration_date_gte.split())[0]
    except ValueError:
        pass

    # vrati hlavne data
    query_params = ()
    order_by_string = " ORDER BY " + params["order_by"] + " " + params["order_type"] + """ LIMIT %s OFFSET %s ;"""
    query = """SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name,  br_section,
        br_insertion, text, street, postal_code, city FROM ov.or_podanie_issues"""
    where_clause = """"""
    if "query" in params or "registration_date_lte" in params or "registration_date_gte" in params:
        where_clause += """ WHERE (1=1) """
    if "query" in params:
        where_clause += """AND ((corporate_body_name ILIKE %s) OR (cin::varchar(255) = %s) OR (city ILIKE %s)) """
        query_params += (str(params["query"]), str(params["query"]), str(params["query"]),)

    if "registration_date_lte" in params:
        where_clause += """AND (registration_date <= %s) """
        query_params += (str(params["registration_date_lte"]),)

    if "registration_date_gte" in params:
        where_clause += """AND (registration_date >= %s) """
        query_params += (str(params["registration_date_gte"]),)

    query += where_clause + order_by_string
    query_params += (int(params["per_page"]), ((int(params["page"]) - 1) * int(params["per_page"])),)

    t1 = threading.Thread(target=get_data_from_database, args=(query, query_params,))
    t2 = threading.Thread(target=refresh_database)
    query = "SELECT COUNT(id) FROM ov.or_podanie_issues " + where_clause
    query_params = query_params[0:-2]
    t3 = threading.Thread(target=get_metadata, args=(query, query_params,))

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    # vytvori metadata
    metadata = {"page": int(params["page"]), "per_page": int(params["per_page"]),
                "pages": int(ceil(row[0]/int(params["per_page"]))), "total": row[0]}
    return JsonResponse({"items": make_dict_from_data(result), "metadata": metadata}, status=200)
