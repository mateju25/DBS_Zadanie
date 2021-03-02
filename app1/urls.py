from django.urls import path

from app1.views import health
from app1.views import submissions

urlpatterns = [
    path('health/', health.get_uptime),
    path('ov/submissions/', submissions.choose_method)
]