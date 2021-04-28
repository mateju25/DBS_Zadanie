from django.http import JsonResponse, HttpResponse
from django.db import connection


# vymaze dany zaznam idetifikovany pomocou id
from v2.models import OrPodanieIssues, RawIssues, BulletinIssues


def erase_data(row_id):

    try:
        bullet_id = OrPodanieIssues.objects.get(id=row_id).bulletin_issue_id
        raw_id = OrPodanieIssues.objects.get(id=row_id).raw_issue_id

        OrPodanieIssues.objects.filter(id=row_id).delete()

    except Exception:
        return JsonResponse({"error": {"message": "Záznam neexistuje"}}, status=404)

    try:
        if OrPodanieIssues.objects.filter(raw_issue_id=raw_id).count() == 0:
            RawIssues.objects.filter(id=raw_id).delete()

        if OrPodanieIssues.objects.filter(bulletin_issue_id=bullet_id).count() == 0:
            if RawIssues.objects.filter(bulletin_issue_id=bullet_id).count() == 0:
                BulletinIssues.objects.filter(id=bullet_id).delete()
    finally:
        pass

    return HttpResponse(status=204)
