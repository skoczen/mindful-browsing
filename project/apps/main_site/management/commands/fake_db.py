from django.core.management.base import BaseCommand
from utils.factory import Factory


class Command(BaseCommand):

    def handle(self, *args, **options):
        for i in range(100):
            # Factory.useful_object(order=i)
            pass
