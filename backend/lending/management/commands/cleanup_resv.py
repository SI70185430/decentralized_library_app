from django.core.management.base import BaseCommand

from lending.services.reservation_actions import release_expired_reservations


class Command(BaseCommand):
    help = "Release expired reservations and make reserved book copies available."

    def handle(self, *args, **options):
        count = release_expired_reservations()
        self.stdout.write(f"expired reservations released. count={count}")
