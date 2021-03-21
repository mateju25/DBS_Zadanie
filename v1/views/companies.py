from math import ceil

from django.db import connection
from django.http import JsonResponse

from v1.modelsZadanie2.validating_reformating import *


# vytiahne z pola GET dany parameter, skontroluje ci je platny, ak sa tam nenachadza vrati je default hodnotu
def extract_and_validate_data_from_get(request, pa_key, def_value):
    temp = request.GET.get(pa_key, def_value)
    if is_number(temp) is not None:
        return int(is_number(temp))
    else:
        return def_value


# vytvori z listu listov, list slovnikov (kvoli zadaniu)
def make_dict_from_data(pa_data):
    result = []
    for x in pa_data:
        result.append({
            "cin": x[0],
            "name": x[1],
            "br_section": x[2],
            "addres_line": x[3],
            "or_podanie_issues_count": x[4],
            "znizenie_imania_issues_count": x[5],
            "likvidator_issues_count": x[6],
            "konkurz_vyrovnanie_issues_count": x[7],
            "konkurz_restrukturalizacia_actors_count": x[8],
        })
    return result


def get_companies(request):
    # v dictionary params sa budu nachadzat dane argumenty na filtrovanie
    params = {}
    params["page"] = extract_and_validate_data_from_get(request, "page", "1")
    if params["page"] == 0:
        params["page"] = 1
    params["per_page"] = extract_and_validate_data_from_get(request, "per_page", "10")

    # overi, ci v order_by parametri je len to co tam ma byt
    params["order_by"] = request.GET.get("order_by", "cin")
    columns = ["cin", "name", "br_section", "address_line", "last_update",
               "or_podanie_issues_count", "znizenie_imania_issues_count", "likvidator_issues_count",
               "konkurz_vyrovnanie_issues_count", "konkurz_restrukturalizacia_actors_count"]
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
    p_last_update_lte = request.GET.get("last_update_lte", None)
    p_last_update_lte = is_date(p_last_update_lte)
    if p_last_update_lte is not None:
        params["last_update_lte"] = p_last_update_lte

    # zvaliduje datum (parameter registration_date_gte)
    p_last_update_gte = request.GET.get("last_update_gte", None)
    p_last_update_gte = is_date(p_last_update_gte)
    if p_last_update_gte is not None:
        params["last_update_gte"] = p_last_update_gte

    cursor = connection.cursor()

    # vysklada podmienky
    query_params = ()
    order_by_string = " ORDER BY " + params["order_by"] + " " + params["order_type"] + """ LIMIT %s OFFSET %s ;"""
    where_clause = """"""
    if "query" in params or "last_update_lte" in params or "last_update_gte" in params:
        where_clause += """ WHERE (1=1) """
    if "query" in params:
        where_clause += """AND ((ov.companies.name ILIKE %s) OR (ov.companies.address_line ILIKE %s)) """
        query_params += (str(params["query"]), str(params["query"]),)

    if "last_update_lte" in params:
        where_clause += """AND (ov.companies.last_update <= %s) """
        query_params += (str(params["last_update_lte"]),)

    if "last_update_gte" in params:
        where_clause += """AND (ov.companies.last_update >= %s) """
        query_params += (str(params["last_update_gte"]),)

    views = """
        WITH podanie as
        (
	        SELECT DISTINCT ov.or_podanie_issues.cin,  NULLIF(COUNT(ov.or_podanie_issues.company_id) OVER (PARTITION BY ov.or_podanie_issues.company_id), 0) AS or_podanie_issues_count FROM ov.or_podanie_issues
        ),
        likvidator as
        (
	        SELECT DISTINCT ov.likvidator_issues.cin,  NULLIF(COUNT(ov.likvidator_issues.company_id) OVER (PARTITION BY ov.likvidator_issues.company_id), 0) AS likvidator_issues_count FROM ov.likvidator_issues
        ),
        konkurz_vyrovnanie as
        (
	        SELECT DISTINCT ov.konkurz_vyrovnanie_issues.cin,  NULLIF(COUNT(ov.konkurz_vyrovnanie_issues.company_id) OVER (PARTITION BY ov.konkurz_vyrovnanie_issues.company_id), 0) AS konkurz_vyrovnanie_issues_count FROM ov.konkurz_vyrovnanie_issues
        ),  
        znizenie_imania as
        (
     	        SELECT DISTINCT ov.znizenie_imania_issues.cin,  NULLIF(COUNT(ov.znizenie_imania_issues.company_id) OVER (PARTITION BY ov.znizenie_imania_issues.company_id), 0) AS znizenie_imania_issues_count FROM ov.znizenie_imania_issues
        ),
        konkurz_restrukturalizacia as
        (
     	    SELECT DISTINCT ov.konkurz_restrukturalizacia_actors.cin,  NULLIF(COUNT(ov.konkurz_restrukturalizacia_actors.company_id) OVER (PARTITION BY ov.konkurz_restrukturalizacia_actors.company_id), 0) AS konkurz_restrukturalizacia_actors_count FROM ov.konkurz_restrukturalizacia_actors
        )"""

    from_table = """
     FROM ov.companies
     LEFT JOIN podanie ON ov.companies.cin = podanie.cin
     LEFT JOIN likvidator ON ov.companies.cin = likvidator.cin
     LEFT JOIN konkurz_vyrovnanie ON ov.companies.cin = konkurz_vyrovnanie.cin
     LEFT JOIN znizenie_imania ON ov.companies.cin = znizenie_imania.cin
     LEFT JOIN konkurz_restrukturalizacia ON ov.companies.cin = konkurz_restrukturalizacia.cin"""

    # zisti metadata
    query = """ SELECT COUNT(ov.companies.cin) FROM ov.companies """ + where_clause
    if len(query_params) != 0:
        cursor.execute(query, query_params)
    else:
        cursor.execute(query)
    print(cursor.query)
    count = cursor.fetchone()

    # zisti hlavny data
    row = []
    if not (int(ceil(count[0] / int(params["per_page"]))) < (int(params["page"]))):
        query = views + """  
        SELECT 
        ov.companies.cin,
        ov.companies.name,
        ov.companies.br_section,
        ov.companies.last_update,
        or_podanie_issues_count,
        znizenie_imania_issues_count,
        likvidator_issues_count,
        konkurz_vyrovnanie_issues_count,
        konkurz_restrukturalizacia_actors_count""" + from_table
        query += where_clause + order_by_string
        query_params += (int(params["per_page"]), ((int(params["page"]) - 1) * int(params["per_page"])),)
        cursor.execute(query, query_params)
        print(cursor.query)
        row = cursor.fetchall()

    cursor.close()

    # vytvori metadata
    metadata = {"page": int(params["page"]), "per_page": int(params["per_page"]),
                "pages": int(ceil(count[0] / int(params["per_page"]))), "total": count[0]}
    return JsonResponse({"items": make_dict_from_data(row), "metadata": metadata}, status=200)
