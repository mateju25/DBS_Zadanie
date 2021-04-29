from math import ceil

from django.db.models import Q, F, CharField
from django.db.models.functions import Concat, Cast
from django.http import JsonResponse

from v1.modelsZadanie2.validating_reformating import validate_data_from_get_int, is_date
from v2.models import OrPodanieIssues


# vytvori z vysledku ORM, list slovnikov (kvoli zadaniu)
def make_dict_from_data(pa_data):
    result = []
    for x in pa_data:
        result.append({
            "id": x.id,
            "br_court_name": x.br_court_name,
            "kind_name": x.kind_name,
            "cin": x.cin,
            "registration_date": x.registration_date,
            "corporate_body_name": x.corporate_body_name,
            "br_section": x.br_section,
            "br_insertion": x.br_insertion,
            "text": x.text,
            "street": x.street,
            "postal_code": x.postal_code,
            "city": x.city
        })
    return result


def validate_parameters(request):
    # v dictionary params sa budu nachadzat dane argumenty na filtrovanie
    params = {}

    params["page"] = int(validate_data_from_get_int(request, "page", "1"))
    if params["page"] <= 0:
        params["page"] = 1
    params["per_page"] = int(validate_data_from_get_int(request, "per_page", "10"))

    # overi, ci v order_by parametri je len to co tam ma byt
    params["order_by"] = request.GET.get("order_by", "id")
    columns = ["id", "br_court_name", "kind_name", "cin", "registration_date",
               "corporate_body_name", "br_section", "br_insertion", "text", "street", "postal_code", "city"]
    if params["order_by"] not in columns:
        params["order_by"] = "id"

    # overi, ci v order_type parametri je len to co tam ma byt
    params["order_type"] = (request.GET.get("order_type", "-")).lower()
    columns = ["asc", "desc"]
    if params["order_type"] not in columns:
        params["order_type"] = "desc"

    # do vyhladavacieho stringu doplni %query%, kvoli matchovaniu pri vyhladavani
    query = request.GET.get("query", None)
    if query is None:
        query = ""
    params["query"] = query.lower()

    # zvaliduje datum (parameter p_registration_date_lte)
    p_registration_date_lte = request.GET.get("registration_date_lte", None)
    p_registration_date_lte = is_date(p_registration_date_lte)
    if p_registration_date_lte is not None:
        params["registration_date_lte"] = p_registration_date_lte

    # zvaliduje datum (parameter registration_date_gte)
    p_registration_date_gte = request.GET.get("registration_date_gte", None)
    p_registration_date_gte = is_date(p_registration_date_gte)
    if p_registration_date_gte is not None:
        params["registration_date_gte"] = p_registration_date_gte

    return params


def get_list_from_get_without_id(request):
    # v dictionary params sa budu nachadzat dane argumenty na filtrovanie
    params = validate_parameters(request)

    data = OrPodanieIssues.objects
    if "query" in params:
        data = data.annotate(search_name=Concat('corporate_body_name', Cast('cin', CharField()), 'city')).filter(search_name__icontains=params["query"])

    if "registration_date_lte" in params:
        data = data.filter(registration_date__lte=params["registration_date_lte"])

    if "registration_date_gte" in params:
        data = data.filter(registration_date__gte=params["registration_date_gte"])

    count = data.count()

    if params["order_type"] == "asc":
        data = data.order_by(F(params["order_by"]).asc(nulls_last=True))
    else:
        data = data.order_by(F(params["order_by"]).desc(nulls_last=True))

    data = list(data.all()[(params["page"] - 1) * params["per_page"]: params["page"] * params["per_page"]])

    # vytvori metadata
    metadata = {"page": int(params["page"]), "per_page": int(params["per_page"]),
                "pages": int(ceil(count / int(params["per_page"]))), "total": count}
    return JsonResponse({"items": make_dict_from_data(data), "metadata": metadata}, status=200)


def get_list_from_get_with_id(request, id):
    try:
        x = OrPodanieIssues.objects.get(id=id)
    except Exception:
        return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404)

    get_json = {
        "id": x.id,
        "br_court_name": x.br_court_name,
        "kind_name": x.kind_name,
        "cin": x.cin,
        "registration_date": x.registration_date,
        "corporate_body_name": x.corporate_body_name,
        "br_section": x.br_section,
        "br_insertion": x.br_insertion,
        "text": x.text,
        "street": x.street,
        "postal_code": x.postal_code,
        "city": x.city
    }

    return JsonResponse({"response": get_json}, status=201)
