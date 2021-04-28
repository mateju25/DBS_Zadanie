from math import ceil

from django.db import models
from django.db.models import Window, Count, F, When, Value
from django.db.models.functions import Concat, NullIf
from django.http import JsonResponse

from v1.modelsZadanie2.validating_reformating import validate_data_from_get_int, is_date
from v2.models import Companies, OrPodanieIssues


# vytvori z vysledku ORM, list slovnikov (kvoli zadaniu)
def make_dict_from_data(pa_data):
    result = []
    for x in pa_data:
        result.append({
            "cin": x.cin,
            "name": x.name,
            "br_section": x.br_section,
            "address_line": x.address_line,
            "last_update": x.last_update,
            "or_podanie_issues_count": x.or_podanie_issues_count,
            "znizenie_imania_issues_count": x.znizenie_imania_issues_count,
            "likvidator_issues_count": x.likvidator_issues_count,
            "konkurz_vyrovnanie_issues_count": x.konkurz_vyrovnanie_issues_count,
            "konkurz_restrukturalizacia_actors_count": x.konkurz_restrukturalizacia_actors_count,
        })
    return result

def get_companies(request):
    # v dictionary params sa budu nachadzat dane argumenty na filtrovanie
    params = {}
    params["page"] = int(validate_data_from_get_int(request, "page", "1"))
    if params["page"] <= 0:
        params["page"] = 1
    params["per_page"] = int(validate_data_from_get_int(request, "per_page", "10"))

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
    params["order_type"] = params["order_type"].lower()

    # do vyhladavacieho stringu doplni %query%, kvoli matchovaniu pri vyhladavani
    # do vyhladavacieho stringu doplni %query%, kvoli matchovaniu pri vyhladavani
    query = request.GET.get("query", None)
    if query is None:
        query = ""
    params["query"] = query.lower()

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

    data = Companies.objects
    if "query" in params:
        data = data.annotate(search_name=Concat('name', 'address_line')).filter(search_name__icontains=params["query"])

    if "last_update_lte" in params:
        data = data.filter(last_update__lte=params["last_update_lte"])

    if "last_update_gte" in params:
        data = data.filter(last_update__gte=params["last_update_gte"])

    count = data.count()

    #data = data.select_related('cin')

    data = data.annotate(or_podanie_issues_count=NullIf(Count('orpodanieissues', distinct=True), Value(0)),
                         likvidator_issues_count=NullIf(Count('likvidatorissues', distinct=True), Value(0)),
                         konkurz_vyrovnanie_issues_count=NullIf(Count('konkurzvyrovnanieissues', distinct=True), Value(0)),
                         znizenie_imania_issues_count=NullIf(Count('znizenieimaniaissues', distinct=True), Value(0)),
                         konkurz_restrukturalizacia_actors_count=NullIf(Count('konkurzrestrukturalizaciaactors', distinct=True), Value(0)))

    if params["order_type"] == "asc":
        data = list(data.order_by(F(params["order_by"]).asc(nulls_last=True)).all()[
                    (params["page"] - 1) * params["per_page"]: params["page"] * params["per_page"]])

    else:
        data = list(data.order_by(F(params["order_by"]).desc(nulls_last=True)).all()[
                    (params["page"] - 1) * params["per_page"]: params["page"] * params["per_page"]])


    # vytvori metadata
    metadata = {"page": int(params["page"]), "per_page": int(params["per_page"]),
                "pages": int(ceil(count / int(params["per_page"]))), "total": count}
    return JsonResponse({"items": make_dict_from_data(data), "metadata": metadata}, status=200)