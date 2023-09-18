from django.core.management.base import BaseCommand
from main.models import Startup, Description, Address
from datetime import date

class Command(BaseCommand):
    help = 'Seed startup data'

    def handle(self, *args, **options):
        # Create or retrieve the Description instance
        description, created = Description.objects.get_or_create(
            name="Your Startup Name",
            description="Description of your startup goes here.",
            sector="Your Sector",
            # Add other fields as needed
        )

        # Create or retrieve the Address instance
        address, created = Address.objects.get_or_create(
            country="Your Country",
            location_id=1,  # Replace with the appropriate Wereda ID
            phone_number=1234567890,
            city_name="Your City",
            website="https://www.example.com",
        )

        # Create the Startup instance
        startup, created = Startup.objects.get_or_create(
            establishment_year=date(2020, 1, 1),  # Replace with the establishment year
            market_scope="Your Market Scope",
            stage="Your Stage",
            description=description,
            address=address,
            # Add other fields as needed
        )

        self.stdout.write(self.style.SUCCESS('Startup seeded successfully'))
