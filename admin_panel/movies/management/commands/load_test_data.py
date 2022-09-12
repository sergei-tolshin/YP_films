from django.core.management.base import BaseCommand, CommandError

from test_data.load_data import main

class Command(BaseCommand):
    help = "load test data from sqlite database"

    def handle(self, *args, **options):
        main()
