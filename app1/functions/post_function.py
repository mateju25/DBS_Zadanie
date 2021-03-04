from datetime import *

from django.db import connection
from django.http import JsonResponse
from app1.functions.validating_reformating import *

import json


def extract_and_validate_data_from_post(pa_json, pa_key, pa_is_number=False):
    temp = pa_json[pa_key]
    if pa_is_number:
        if type(temp) is int:
            return temp
        else:
            return None
    else:
        try:
            if temp is not None:
                datetime.strptime(temp, '%Y-%m-%d %H:%M:%S.%f')
                if temp >= datetime.now().strftime('%Y'):
                    return temp
                else:
                    return None
        except ValueError:
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
                post_json[x] = extract_and_validate_data_from_post(post_json, x, pa_is_number=True)
                if post_json[x] is None:
                    errors.append({"field": x, "reasons": "not_number"})
            elif x == 'registration_date':
                post_json[x] = extract_and_validate_data_from_post(post_json, x)
                if post_json[x] is None:
                    errors.append({"field": x, "reasons": "invalid_range"})

    if len(errors) != 0:
        return JsonResponse({"errors": errors}, status=422)

    # ziskaj dalsie number pre bulletin_issues
    cursor = connection.cursor()
    query = """SELECT MAX(number)+1 FROM ov.bulletin_issues WHERE year = date_part('year', CURRENT_DATE);"""
    cursor.execute(query)
    number = (cursor.fetchone())[0]
    if number is None:
        number = 1

    # vytvor novy zaznam pre bullettin_issues
    query = """INSERT INTO ov.bulletin_issues (year, number, published_at, created_at, updated_at) VALUES 
    (date_part('year', CURRENT_DATE), %s, now(), now(), now()); """
    cursor.execute(query, (number,))

    # ziskaj id prave vytvoreneho bulletin_issues
    query = """SELECT id FROM ov.bulletin_issues ORDER BY id desc LIMIT 1"""
    cursor.execute(query)
    bullet_id = (cursor.fetchone())[0]

    # vytvor novy zaznam v raw_issues
    query = """INSERT INTO ov.raw_issues (bulletin_issue_id, file_name, content, created_at, updated_at) VALUES 
    (%s, '', null, now(), now()); """
    cursor.execute(query, (bullet_id, ))

    # ziskaj id prave vytvoreneho raw_isssues
    query = """SELECT id FROM ov.raw_issues WHERE bulletin_issue_id = %s;"""
    cursor.execute(query, (bullet_id,))
    raw_id = (cursor.fetchone())[0]

    # vytvor riadok z dat a klucov do podanie_issues
    adress_line = post_json["street"] + ", " + post_json["postal_code"] + " " + post_json["city"]
    query = """INSERT INTO ov.or_podanie_issues 
    (raw_issue_id, bulletin_issue_id, br_mark, br_court_code, br_court_name, kind_code, kind_name, cin, registration_date, corporate_body_name, br_section, br_insertion, text, created_at, updated_at, address_line, street, postal_code, city ) 
    VALUES (%s, %s, '', '', %s, '', %s, %s, %s, %s, %s, %s, %s, now(), now(), %s, %s, %s, %s); """
    cursor.execute(query, (raw_id, bullet_id, post_json["br_court_name"], post_json["kind_name"], post_json["cin"], post_json["registration_date"], post_json["corporate_body_name"], post_json["br_section"], post_json["br_insertion"], post_json["text"], adress_line, post_json["street"], post_json["postal_code"], post_json["city"], ))

    # vrat cele data aktualne vytvoreneho
    query = """SELECT id, br_court_name, kind_name, cin, registration_date, corporate_body_name,  br_section,
            br_insertion, text, street, postal_code, city FROM ov.or_podanie_issues ORDER BY id desc LIMIT 1"""
    cursor.execute(query)
    row = cursor.fetchone()

    return JsonResponse({"response": make_dict_from_data([row])}, status=201)
