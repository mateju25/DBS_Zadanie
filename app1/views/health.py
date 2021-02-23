from django.db import connection
from django.http import JsonResponse


# vrati json s informaciou o casovej dlzke behu databazy
def get_uptime(request):
    cursor = connection.cursor()
    cursor.execute("SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime;")
    row = cursor.fetchone()
    if row is None:
        return JsonResponse({"Error": "Nothing fetched from database"})

    # z datetimu sprav string a odstan ciarky
    return JsonResponse({"pgsql": {"uptime": str(row[0]).replace(',', '')}})
