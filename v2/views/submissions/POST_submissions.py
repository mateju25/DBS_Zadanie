import datetime
from django.db.models import F
from django.http import JsonResponse
from django.utils import timezone

from v1.modelsZadanie2.validating_reformating import *

import json

from v2.models import BulletinIssues, RawIssues, OrPodanieIssues


def extract_and_validate_data_from_body(pa_json, pa_key, pa_is_number=False):
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
                post_json[x] = extract_and_validate_data_from_body(post_json, x, pa_is_number=True)
                if post_json[x] is None:
                    errors.append({"field": x, "reasons": ["not_number"]})

            # ak je to registration_date, overi ci datum v spravnom formate
            elif x == 'registration_date':
                post_json[x] = extract_and_validate_data_from_body(post_json, x)
                if post_json[x] is None:
                    errors.append({"field": x, "reasons": ["invalid_range"]})

            elif type(post_json[x]) is int:
                errors.append({"field": x, "reasons": ["required"]})

    # ak nie su chyby, pokracuj dalej
    if len(errors) != 0:
        return JsonResponse({"errors": errors}, status=422)

    data_bulletin = BulletinIssues.objects

    now = timezone.now()
    max_number = data_bulletin.filter(year__gte=now.year).order_by(F('number').desc(nulls_last=True)).first().number
    newBullet = BulletinIssues(year=now.year, number=max_number+1, published_at=now, created_at=now, updated_at=now)
    newBullet.save()
    bullet_id = newBullet.id

    newRaw = RawIssues(bulletin_issue_id=bullet_id, file_name='-', content='-', created_at=now, updated_at=now)
    newRaw.save()
    raw_id = newRaw.id

    address_line = post_json["street"] + ", " + post_json["postal_code"] + " " + post_json["city"]
    newPodanie = OrPodanieIssues(raw_issue_id=raw_id, bulletin_issue_id=bullet_id, br_mark='-', br_court_code='-',
                                 br_court_name=post_json["br_court_name"], kind_code='-', kind_name=post_json["kind_name"],
                                 cin=post_json["cin"], registration_date=post_json["registration_date"], corporate_body_name=post_json["corporate_body_name"],
                                 br_section=post_json["br_section"], br_insertion=post_json["br_insertion"], text=post_json["text"],
                                 created_at=now, updated_at=now, address_line=address_line, street=post_json["street"], postal_code=post_json["postal_code"], city=post_json["city"])
    newPodanie.save()
    post_json["id"] = newPodanie.id

    return JsonResponse({"response": post_json}, status=201)
