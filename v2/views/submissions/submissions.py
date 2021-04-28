

# rozhodne o aku metodu ide (GET, POST)
from v2.views.submissions.DELETE_submissons import erase_data
from v2.views.submissions.GET_submissions import get_list_from_get_without_id, get_list_from_get_with_id
from v2.views.submissions.POST_submissions import post_new_data
from v2.views.submissions.PUT_submissions import put_new_data


def choose_method(request, id=-1):
    if request.method == "GET":
        if id == -1:
            return get_list_from_get_without_id(request)
        else:
            return get_list_from_get_with_id(request, id)
    elif request.method == "POST":
        return post_new_data(request)
    elif request.method == "DELETE":
        return erase_data(id)
    elif request.method == "PUT":
        return put_new_data(request, id)

