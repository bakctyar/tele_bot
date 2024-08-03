from django.core.management.base import BaseCommand
from start.views import main


class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **kwargs):
        main()