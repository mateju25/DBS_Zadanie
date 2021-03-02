from django.db import connection
from django.http import JsonResponse
from django.http import HttpResponse
from app1.functions.sql_defense import *


def http_error_422():
    return JsonResponse({"Error": "volam sandare"})


def verify_parameter(request, pa_key, errors, pa_is_number=False):
    reasons = []
    temp = request.POST.get(pa_key, -1)
    if temp == -1:
        reasons.append("required")
    if pa_is_number:
        if is_number(temp) is not None:
            temp = int(is_number(temp))
        else:
            reasons.append("not_number")
    else:
        if is_string(temp) is not None:
            temp = is_string(temp)
        else:
            reasons.append("required")

    if len(reasons) != 0:
        errors.append({"field": "br_court_name", "reasons": reasons})

    return temp


def post_new_data(request):
    errors = []
    br_court_name = verify_parameter(request, "br_court_name", errors)
    kind_name = verify_parameter(request, "kind_name", errors)
    cin = verify_parameter(request, "cin", errors, pa_is_number=True)
    registration_date = verify_parameter(request, "registration_date", errors)
    corporate_body_name = verify_parameter(request, "corporate_body_name", errors)
    br_section = verify_parameter(request, "br_section", errors)
    br_insertion = verify_parameter(request, "br_insertion", errors)
    text = verify_parameter(request, "text", errors)
    street = verify_parameter(request, "street", errors)
    postal_code = verify_parameter(request, "postal_code", errors)
    city = verify_parameter(request, "city", errors)
    if len(errors) != 0:
        return JsonResponse({"errors": errors})
    return
