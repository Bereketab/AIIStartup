from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from main.models import EthRegion
class Command(BaseCommand):
    help = 'Seed groups data'

    def handle(self, *args, **options):
        region_names = ['Addis Ababa', 'Afar', 'Amhara', 'Benishangul-Gumuz', 'Dire Dawa','Gambela','Harari','Oromia','Somali','Sidama','South West','SNNP','Tigray']

        for region_name in region_names:
            EthRegion.objects.get_or_create(region_name=region_name)

        self.stdout.write(self.style.SUCCESS('Regions seeded successfully'))

