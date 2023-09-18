from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Seed groups data'

    def handle(self, *args, **options):
        group_names = ['Funder/Donor', 'Government', 'Incubator/Hub/Accelerator', 'Mentor', 'Startup']

        for group_name in group_names:
            Group.objects.get_or_create(name=group_name)

        self.stdout.write(self.style.SUCCESS('Groups seeded successfully'))