import datetime
from django.db import connection
from django.http import JsonResponse
from app1.models.validating_reformating import *

import json


# overi ci cislo je int, alebo ci je datum v spravnom formate, ak nie vrati None
def extract_and_validate_data_from_post(pa_json, pa_key, pa_is_number=False):
    temp = pa_json[pa_key]
    if pa_is_number:
        if type(temp) is int:
            return temp
        else:
            return None
    else:
        temp = is_date(str(temp))
        if temp is None:
            return None
        if temp >= datetime.now().strftime('%Y'):
            return temp
        else:
            return None


# vlozi novy riadok do tabulky or_podanie_issues
def post_new_data(request):
    errors = []
    required = ["br_court_name", "kind_name", "cin", "registration_date", "corporate_body_name",
                "br_section", "br_insertion", "text", "street", "postal_code", "city"]

    try:
        post_json = json.loads(request.body)
    except Exception:
        for x in required:
            errors.append({"field": x, "reasons": ["required"]})
        return JsonResponse({"errors": errors}, status=422)

    # prejde json, ci su pritomne vsetky required polia
    for x in required:
        if x not in post_json:
            errors.append({"field": x, "reasons": ["required"]})
        else:
            # ak je to parameter cin, overi ci je to cislo
            if x == 'cin':
                post_json[x] = extract_and_validate_data_from_post(post_json, x, pa_is_number=True)
                if post_json[x] is None:
                    errors.append({"field": x, "reasons": ["not_number"]})

            # ak je to registration_date, overi ci datum v spravnom formate
            elif x == 'registration_date':
                post_json[x] = extract_and_validate_data_from_post(post_json, x)
                if post_json[x] is None:
                    errors.append({"field": x, "reasons": ["invalid_range"]})

            elif type(post_json[x]) is int:
                errors.append({"field": x, "reasons": ["required"]})

    # ak nie su chyby, pokracuj dalej
    if len(errors) != 0:
        return JsonResponse({"errors": errors}, status=422)

    # ziskaj dalsie mozne number pre bulletin_issues v dany rok
    cursor = connection.cursor()
    query = """SELECT MAX(number)+1 FROM ov.bulletin_issues WHERE year = date_part('year', CURRENT_DATE);"""
    cursor.execute(query)
    number = (cursor.fetchone())[0]
    if number is None:
        number = 1

    # vytvor novy zaznam pre bullettin_issues
    query = """INSERT INTO ov.bulletin_issues (year, number, published_at, created_at, updated_at) VALUES 
    (date_part('year', CURRENT_DATE), %s, now(), now(), now()) RETURNING id; """
    cursor.execute(query, (number,))
    # ziskaj id prave vytvoreneho bulletin_issues
    bullet_id = (cursor.fetchone())[0]

    # vytvor novy zaznam v raw_issues
    query = """INSERT INTO ov.raw_issues (bulletin_issue_id, file_name, content, created_at, updated_at) VALUES 
    (%s, '-', '-', now(), now()) RETURNING id; """
    cursor.execute(query, (bullet_id,))
    # ziskaj id prave vytvoreneho raw_isssues
    raw_id = (cursor.fetchone())[0]

    # vytvor riadok z dat a klucov do podanie_issues
    adress_line = post_json["street"] + ", " + post_json["postal_code"] + " " + post_json["city"]
    query = """INSERT INTO ov.or_podanie_issues 
    (raw_issue_id, bulletin_issue_id, br_mark, br_court_code, br_court_name, kind_code, kind_name, cin, 
    registration_date, corporate_body_name, br_section, br_insertion, text, created_at, updated_at, 
    address_line, street, postal_code, city ) 
    VALUES (%s, %s, '-', '-', %s, '-', %s, %s, %s, %s, %s, %s, %s, now(), now(), %s, %s, %s, %s) RETURNING id;"""
    cursor.execute(query, (raw_id, bullet_id, post_json["br_court_name"], post_json["kind_name"], post_json["cin"],
                           post_json["registration_date"], post_json["corporate_body_name"], post_json["br_section"],
                           post_json["br_insertion"], post_json["text"], adress_line, post_json["street"],
                           post_json["postal_code"], post_json["city"],))
    # ziskaj id prave vytvoreneho podanie_issues
    podanie_id = (cursor.fetchone())[0]
    post_json["id"] = podanie_id

    return JsonResponse({"response": post_json}, status=201)
