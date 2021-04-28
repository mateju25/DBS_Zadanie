from v2.views.companies.GET_companies import get_companies


def choose_method(request):
    return get_companies(request)