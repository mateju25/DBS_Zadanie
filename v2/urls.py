from django.urls import path

from v2.views.submissions import submissions
from v2.views.companies import companies

urlpatterns = [
    path('ov/submissions', submissions.choose_method),
    path('ov/submissions/', submissions.choose_method),
    path('companies', companies.choose_method),
    path('companies/', companies.choose_method),
    path('ov/submissions/<int:id>', submissions.choose_method, name="id"),
]
