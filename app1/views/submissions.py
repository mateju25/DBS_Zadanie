from app1.functions.get_function import get_list_from_get
from app1.functions.post_function import post_new_data
from app1.functions.delete_function import erase_data


# rozhodne o aku metodu ide (GET, POST)
def choose_method(request, id=1):
    if request.method == "GET":
        return get_list_from_get(request)
    elif request.method == "POST":
        return post_new_data(request)
    elif request.method == "DELETE":
        return erase_data(id)

