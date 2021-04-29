from django.http import JsonResponse
from django.utils import timezone
import json
from v2.models import OrPodanieIssues


# vlozi novy riadok do tabulky or_podanie_issues
from v2.views.submissions.POST_submissions import extract_and_validate_data_from_body


def put_new_data(request, id):
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

    if OrPodanieIssues.objects.filter(id=id).count() == 0:
        return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404)


    OrPodanieIssues.objects.filter(id=id).update(
                                 br_court_name=post_json["br_court_name"], kind_name=post_json["kind_name"],
                                 cin=post_json["cin"], registration_date=post_json["registration_date"], corporate_body_name=post_json["corporate_body_name"],
                                 br_section=post_json["br_section"], br_insertion=post_json["br_insertion"], text=post_json["text"],
                                 updated_at=timezone.now(), street=post_json["street"], postal_code=post_json["postal_code"], city=post_json["city"])

    post_json["id"] = id
    return JsonResponse({"response": post_json}, status=201)
