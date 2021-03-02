from django.db import connection
from django.http import JsonResponse
from django.http import HttpResponse
from app1.functions.sql_defense import *


def http_error_422():
    return JsonResponse({"Error": "volam sandare"})


def verify_parameter(request, pa_key, reasons, pa_is_number=False):
    temp = request.POST.get(pa_key, -1)
    if temp == -1:
        reasons.append("required")
    if pa_is_number:
        if is_number(temp) is not None:
            return int(is_number(temp))
        else:
            reasons.append("not_number")
    else:
        if is_string(temp) is not None:
            return is_string(temp)
        else:
            reasons.append("required")


def post_new_data(request):
    errors = []
    reasons = []
    br_court_name = verify_parameter(request, "br_court_name", reasons)
    kind_name = verify_parameter(request, "kind_name", reasons)
    cin = verify_parameter(request, "cin", reasons, pa_is_number=True)
    registration_date = verify_parameter(request, "registration_date", reasons)
    corporate_body_name = verify_parameter(request, "corporate_body_name", reasons)
    br_section = verify_parameter(request, "br_section", reasons)
    br_insertion = verify_parameter(request, "br_insertion", reasons)
    text = verify_parameter(request, "text", reasons)
    street = verify_parameter(request, "street", reasons)
    postal_code = verify_parameter(request, "postal_code", reasons)
    city = verify_parameter(request, "city", reasons)
    return
