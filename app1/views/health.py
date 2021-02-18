from django.db import connection
from django.http import JsonResponse

# Create your views here.


def get_uptime(request):
    query="SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime;"
    cursor = connection.cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    if row is None:
        return JsonResponse({"Error": "Nothing fetched from database"})

    fut_json = {"pgsql": {"uptime": str(row[0]).replace(',', '')}}
    return JsonResponse(fut_json)
