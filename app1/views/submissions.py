import re

from django.http import JsonResponse
from django.db import connection


def is_string(paString):
    prog = re.compile("^[a-zA-Z_]+$")
    return prog.match(paString)


def is_number(paString):
    prog = re.compile("^[0-9]+$")
    return int(prog.match(paString))


def get_list_from_GET(request):
    page = request.GET["page"]
    page = is_number(page)
    if page is None:
        page = 1
    per_page = request.GET["per_page"]
    per_page = is_number(per_page)
    if per_page is None:
        per_page = 1;
    # order_by = request.GET["order_by"]
    # order_by = is_number(order_by)
    # order_type = request.GET["order_type"]
    # order_type = is_number(order_type)

    cursor = connection.cursor()
    query = "SELECT " + "id, " + "br_court_name, " + "kind_name, " + "cin, " + "registration_date, " + "corporate_body_name, " + "br_section, "
    "br_insertion, "
    "text, "
    "street, "
    "postal_code, "
    "city"
    "FROM ov.or_podania_issues"
    "LIMIT " + str(per_page) + ";"


    cursor.execute(query)
    row = cursor.fetchone()

    return JsonResponse("Halo")
