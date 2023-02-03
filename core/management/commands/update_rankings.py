"""
Django command to update rankings (ambassador.views.RankingsAPIView).
"""
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django_redis import get_redis_connection


class Command(BaseCommand):
    """Django command to update rankings"""

    def handle(self, *args, **options):
        con = get_redis_connection('default')

        ambassadors = get_user_model().objects.filter(is_ambassador=True)

        for ambassador in ambassadors:
            con.zadd('rankings', {ambassador.name: float(ambassador.revenue)})
