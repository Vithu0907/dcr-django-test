import json
import logging
import requests
from urllib.parse import urlparse

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from countries.models import Country, Region

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command to update country data from an external file."""

    help = "Update country listing from remote file"

    def add_arguments(self, parser):
        """Add command-line arguments for the command."""
        parser.add_argument(
            "--url",
            type=str,
            default="https://storage.googleapis.com/dcr-django-test/countries.json",
            help="URL to fetch country data from",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=30,
            help="Request timeout in seconds",
        )

    def handle(self, *args, **options):
        """Execute the command to fetch and update country data."""
        url = options["url"]
        timeout = options["timeout"]

        self.stdout.write(f"Fetching country data from: {url}")
        
        try:
            parsed_url = urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                raise CommandError(f"Invalid URL format: {url}")
        except Exception as e:
            logger.error(f"URL validation error: {str(e)}")
            raise CommandError(f"URL validation error: {str(e)}")

        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            countries_data = response.json()
            
            if not isinstance(countries_data, list):
                raise CommandError("API did not return a list of countries")
                
            self._process_countries_data(countries_data)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully updated {len(countries_data)} countries from API"
                )
            )
            
        except requests.RequestException as e:
            logger.error(f"API request error: {str(e)}")
            raise CommandError(f"Failed to fetch data from API: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise CommandError(f"Failed to parse API response as JSON: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise CommandError(f"An unexpected error occurred: {str(e)}")

    @transaction.atomic
    def _process_countries_data(self, countries_data):
        """
        Process the countries data and update the database.
        
        Args:
            countries_data (list): List of country dictionaries from the API
            
        Raises:
            CommandError: If there's an error processing the data
        """
        countries_created = 0
        countries_updated = 0
        regions_created = 0
        
        try:
            for country_data in countries_data:
                required_fields = ["name", "alpha2Code", "alpha3Code", "population", "region"]
                for field in required_fields:
                    if field not in country_data:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Skipping country: Missing required field '{field}'"
                            )
                        )
                        continue
                
                region_name = country_data.get("region", "")
                region, region_created = Region.objects.get_or_create(name=region_name)
                if region_created:
                    regions_created += 1
                    self.stdout.write(f"Created new region: {region_name}")
                
                country, country_created = Country.objects.update_or_create(
                    name=country_data["name"],
                    defaults={
                        "alpha2Code": country_data["alpha2Code"],
                        "alpha3Code": country_data["alpha3Code"],
                        "population": country_data.get("population", 0),
                        "region": region,
                    },
                )
                
                if country_created:
                    countries_created += 1
                    self.stdout.write(f"Created new country: {country.name}")
                else:
                    countries_updated += 1
                    self.stdout.write(f"Updated existing country: {country.name}")
                    
            self.stdout.write(
                f"Summary: Created {regions_created} regions, "
                f"created {countries_created} countries, "
                f"updated {countries_updated} countries"
            )
                
        except Exception as e:
            logger.error(f"Error processing country data: {str(e)}")
            raise CommandError(f"Error processing country data: {str(e)}")