from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone
import random

from tickets import models


class Command(BaseCommand):
    help = 'Creates some sample data for testing'

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.user = User.objects.get(username='super')

    def handle(self, *args, **options):
        if not (settings.DEBUG or settings.STAGING):
            raise CommandError('You cannot run this command in production')

        # otherwise it is done by time, which could lead to inconsistent tests
        random.seed('I watch slug documentaries')

        self.create_shows()
        self.create_occurrences()
        self.reserve_tickets()

    @staticmethod
    def create_shows():
        names = ['The Show With No Name', 'Some Unnecessary Commentary on Politics', 'Dangerous Steve, The Musical', 'Not Enough Budget To Think Of A Name', 'Indisposed Chicken, by Bernard Mathews', 'The Play Inside A Play, Inside A Play', 'We\'ll Cover The Bad Acting With Projection', 'Bee Movie Live', 'Silence of the Mice', 'Departure', 'The Student']
        descriptions = ['Not worth seeing really', 'We couldn\'t be bother to light this properly', 'We got the set from Toys \'R Us', 'No one likes me so I did everything myself', 'We needed a filler show and this didn\'t seem awful', 'This show will not make any money back']

        for count in range(50):

            if count % 3 == 0:
                category = models.Category.objects.get(slug='in-house')
            else:
                category = models.Category.objects.get(slug='fringe')

            start_date = timezone.now() + timezone.timedelta(days=random.randint(-20, 60))

            models.Show.objects.get_or_create(
                name=random.choice(names),
                description=random.choice(descriptions),
                category=category,
                start_date=start_date,
                end_date=start_date + timezone.timedelta(days=random.randint(2, 6)),
            )

    @staticmethod
    def create_occurrences():
        for show in models.Show.objects.all():
            for day in range((show.end_date - show.start_date).days):
                models.Occurrence.objects.create(
                    show=show,
                    date=show.start_date + timezone.timedelta(days=day),
                )

    @staticmethod
    def reserve_tickets():
        names = ['Angelo Hearl','Celisse Lionel','Reid Poynor','Ervin Hamlen','Hamil Botha','Emery Laycock','Brandice Gaishson','Toma Kiloh','Marie-ann Conley','Teddie Ahern']
        emails = ['lmclean0@about.com','akalker1@telegraph.co.uk','adanbrook2@blog.com','rbream3@whitehouse.gov','hmaurice4@pen.io','eatty5@patch.com','afranz6@independent.co.uk','jbeazleigh7@illinois.edu','isaltsberger8@prlog.org','ajurisic9@cbc.ca']

        for show in models.Show.objects.all():
            for occurrence in show.occurrence_set.all():
                for i in range(2, 10):
                    models.Ticket.objects.create(
                        occurrence=occurrence,
                        person_name=random.choice(names),
                        email_address=random.choice(emails),
                        quantity=random.randint(1, 4)
                    )
