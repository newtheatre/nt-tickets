from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from tickets import models


class Command(BaseCommand):
    help = 'Creates a super user'

    def handle(self, *args, **options):
        if not (settings.DEBUG or settings.STAGING):
            raise CommandError('You cannot run this command in production')

        self.delete_shows()
        self.delete_occurrences()

    @staticmethod
    def delete_shows():
        for show in models.Show.objects.all():
            show.delete()

    @staticmethod
    def delete_occurrences():
        for occurrence in models.Occurrence.objects.all():
            occurrence.delete()
