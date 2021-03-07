from django.http import HttpResponse
from django.http import JsonResponse
from django.db import connection


# vymaze dany zaznam idetifikovany pomocou id
def erase_data(row_id):
    # zisti id pre raw_issue a bulletin_issue, ak zaznam neexistuje vobec vrati chybovu hlasku
    cursor = connection.cursor()
    query = """SELECT bulletin_issue_id, raw_issue_id FROM ov.or_podanie_issues WHERE id = %s;"""
    cursor.execute(query, (row_id,))
    delete_data = cursor.fetchone()
    if delete_data is None:
        return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404)

    # zisti pocet riadkov v tabulke or_podanie_issues, ktore maju dany bulletin
    query = """SELECT count(id) FROM ov.or_podanie_issues WHERE bulletin_issue_id = %s;"""
    cursor.execute(query, (delete_data[0],))
    count = (cursor.fetchone())[0]
    if count == 1:
        # ak je prave jeden riadok v tabulke or_podanie_issues, ktory maju dany bulletin,
        # este zisti kolko riadkov v raw_issues ma tento bulletin
        query = """SELECT count(id) FROM ov.raw_issues WHERE bulletin_issue_id = %s;"""
        cursor.execute(query, (delete_data[0],))
        count = (cursor.fetchone())[0]
        if count == 1:
            # ak je prave jeden riadok v tabulke or_podanie_issues aj v raw_issues, tak vymaze dany bulletin
            query = """DELETE FROM ov.bulletin_issues WHERE id = %s;"""
            cursor.execute(query, (delete_data[0],))

    # zisti pocet riadkov v tabulke or_podanie_issues, ktore maju dany raw
    query = """SELECT count(id) FROM ov.or_podanie_issues WHERE raw_issue_id = %s;"""
    cursor.execute(query, (delete_data[1],))
    count = (cursor.fetchone())[0]
    if count == 1:
        # ak je prave jeden riadok v tabulke or_podanie_issues, ktory maju dany raw, vymaze ho
        query = """DELETE FROM ov.raw_issues WHERE id = %s;"""
        cursor.execute(query, (delete_data[1],))

    query = """DELETE FROM ov.or_podanie_issues WHERE id = %s;"""
    cursor.execute(query, (row_id,))

    return HttpResponse(status=204)
