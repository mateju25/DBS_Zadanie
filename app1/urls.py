from django.urls import path

from app1.views import health


urlpatterns = [
    path('', health.get_uptime),
]