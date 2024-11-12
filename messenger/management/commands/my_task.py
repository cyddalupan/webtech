from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Describe your task'

    def handle(self, *args, **kwargs):
        # Task logic here
        print("Task executed")
