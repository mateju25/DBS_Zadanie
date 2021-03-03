from django.db import connection
from django.http import JsonResponse
from django.http import HttpResponse
from app1.functions.sql_defense import *

import json


def http_error_422():
    return JsonResponse({"Error": "volam sandare"})


def verify_parameter(pa_json, pa_key, errors, pa_is_number=False):
    temp = pa_json[pa_key]
    if pa_is_number:
        if is_number(temp) is not None:
            return int(is_number(temp))
        else:
            return None
    else:
        if is_string(temp) is not None:
            return is_string(temp)
        else:
            return None


def post_new_data(request):
    errors = []
    post_json = json.loads(request.body)

    required = ["br_court_name", "kind_name", "cin", "registration_date", "corporate_body_name",
                "br_section", "br_insertion", "text", "street", "postal_code", "city"]

    for x in required:
        if x not in post_json:
            errors.append({"field": x, "reasons": "required"})
        else:
            if x == 'cin':
                post_json[x] = verify_parameter(post_json, x, errors, pa_is_number=True)
                if post_json[x] is None:
                    errors.append({"field": x, "reasons": "not_number"})
            else:
                post_json[x] = verify_parameter(post_json, x, errors)
                if post_json[x] is None:
                    errors.append({"field": x, "reasons": "required"})

    if len(errors) != 0:
        return JsonResponse({"errors": errors})
    return JsonResponse({"errors": errors})
