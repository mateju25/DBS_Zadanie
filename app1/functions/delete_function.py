from django.http import HttpResponse
from django.http import JsonResponse
from django.db import connection

def erase_data(id):
    cursor = connection.cursor()
    query = """SELECT bulletin_issue_id, raw_issue_id FROM ov.or_podanie_issues WHERE id = %s;"""
    cursor.execute(query, (id, ))
    delete_data = cursor.fetchone()
    if delete_data is None:
        return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404)

    query = """SELECT count(id) FROM ov.or_podanie_issues WHERE bulletin_issue_id = %s;"""
    cursor.execute(query, (delete_data[0],))
    count = (cursor.fetchone())[0]
    if count == 1:
        query = """SELECT count(id) FROM ov.raw_issues WHERE bulletin_issue_id = %s;"""
        cursor.execute(query, (delete_data[0],))
        count = (cursor.fetchone())[0]
        if count == 1:
            query = """DELETE FROM ov.bulletin_issues WHERE id = %s;"""
            cursor.execute(query, (delete_data[0],))

    query = """SELECT count(id) FROM ov.or_podanie_issues WHERE raw_issue_id = %s;"""
    cursor.execute(query, (delete_data[1],))
    count = (cursor.fetchone())[0]
    if count == 1:
        query = """DELETE FROM ov.raw_issues WHERE id = %s;"""
        cursor.execute(query, (delete_data[1],))

    return HttpResponse(status=204)
