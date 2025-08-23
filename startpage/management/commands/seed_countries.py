from django.core.management.base import BaseCommand
from startpage.models import CountryLink

class Command(BaseCommand):
    help = 'Seeds the database with initial CountryLink data'

    def handle(self, *args, **kwargs):
        # Define countries and URLs
        countries = [
            {'country_name': 'Uganda', 'url': 'https://ug.buyerkraze.com'},
            {'country_name': 'USA', 'url': 'https://us.buyerkraze.com'},
            {'country_name': 'UK', 'url': 'https://uk.buyerkraze.com'},
            {'country_name': 'Germany', 'url': 'https://de.buyerkraze.com'},
            {'country_name': 'Finland', 'url': 'https://fi.buyerkraze.com'},
        ]

        created_count = 0
        skipped_count = 0

        for country_data in countries:
            # Check if country already exists to avoid duplicates
            if not CountryLink.objects.filter(country_name=country_data['country_name']).exists():
                CountryLink.objects.create(
                    country_name=country_data['country_name'],
                    url=country_data['url'],
                    hit_count=0
                )
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created {country_data['country_name']}"))
            else:
                skipped_count += 1
                self.stdout.write(self.style.WARNING(f"Skipped {country_data['country_name']} (already exists)"))

        self.stdout.write(self.style.SUCCESS(f"Seeding complete: {created_count} created, {skipped_count} skipped"))