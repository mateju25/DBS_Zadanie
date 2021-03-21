from django.urls import path

from v1.views import health
from v1.views import submissions
from v1.views import companies

urlpatterns = [
    path('health', health.get_uptime),
    path('health/', health.get_uptime),
    path('ov/submissions', submissions.choose_method),
    path('ov/submissions/', submissions.choose_method),
    path('ov/companies', companies.get_companies),
    path('ov/companies/', companies.get_companies),
    path('ov/submissions/<int:id>', submissions.choose_method, name="id"),

]