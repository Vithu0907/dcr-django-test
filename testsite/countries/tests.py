from django.test import TestCase, Client
from django.urls import reverse
import json
from .models import Region, Country

class StatsViewTestCase(TestCase):
    """Test cases for the stats view."""
    
    def setUp(self):
        """Set up the test data for all test methods."""
        self.africa = Region.objects.create(name="Africa")
        self.americas = Region.objects.create(name="Americas")
        self.asia = Region.objects.create(name="Asia")
        self.empty_region = Region.objects.create(name="Empty Region")
        
        Country.objects.create(
            name="Nigeria",
            alpha2Code="NG",
            alpha3Code="NGA",
            population=200000000,
            region=self.africa
        )
        Country.objects.create(
            name="Egypt",
            alpha2Code="EG",
            alpha3Code="EGY",
            population=100000000,
            region=self.africa
        )
        Country.objects.create(
            name="United States",
            alpha2Code="US",
            alpha3Code="USA",
            population=330000000,
            region=self.americas
        )
        Country.objects.create(
            name="China",
            alpha2Code="CN",
            alpha3Code="CHN",
            population=1400000000,
            region=self.asia
        )
        
        self.client = Client()
        self.url = reverse('stats')
    
    def test_stats_view_response_structure(self):
        """Test that the stats view returns the correct response structure."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('regions', data)
        self.assertIsInstance(data['regions'], list)
        
        region_names = [region['name'] for region in data['regions']]
        self.assertIn('Africa', region_names)
        self.assertIn('Americas', region_names)
        self.assertIn('Asia', region_names)
        self.assertIn('Empty Region', region_names)
        
        for region in data['regions']:
            self.assertIn('name', region)
            self.assertIn('number_countries', region)
            self.assertIn('total_population', region)
    
    def test_populated_regions_stats(self):
        """Test that populated regions return correct statistics."""
        response = self.client.get(self.url)
        data = json.loads(response.content)
        
        africa_data = next((r for r in data['regions'] if r['name'] == 'Africa'), None)
        americas_data = next((r for r in data['regions'] if r['name'] == 'Americas'), None)
        asia_data = next((r for r in data['regions'] if r['name'] == 'Asia'), None)
        
        self.assertIsNotNone(africa_data)
        self.assertEqual(africa_data['number_countries'], 2)
        self.assertEqual(africa_data['total_population'], 300000000)
        
        self.assertIsNotNone(americas_data)
        self.assertEqual(americas_data['number_countries'], 1)
        self.assertEqual(americas_data['total_population'], 330000000)
        
        self.assertIsNotNone(asia_data)
        self.assertEqual(asia_data['number_countries'], 1)
        self.assertEqual(asia_data['total_population'], 1400000000)
    
    def test_empty_region_stats(self):
        """Test that empty regions are handled correctly."""
        response = self.client.get(self.url)
        data = json.loads(response.content)
        
        empty_region_data = next((r for r in data['regions'] if r['name'] == 'Empty Region'), None)
        
        self.assertIsNotNone(empty_region_data)
        self.assertEqual(empty_region_data['number_countries'], 0)
        self.assertEqual(empty_region_data['total_population'], 0)
    
    def test_response_data_types(self):
        """Test that the response contains correct data types."""
        response = self.client.get(self.url)
        data = json.loads(response.content)
        
        for region in data['regions']:
            self.assertIsInstance(region['name'], str)
            self.assertIsInstance(region['number_countries'], int)
            self.assertIsInstance(region['total_population'], int)
    