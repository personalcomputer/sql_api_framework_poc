from django.contrib.gis.geos import Point
from django.test import Client, TestCase

from todos.models import Location


class LocationListingTestCase(TestCase):
    def setUp(self):
        self.locations = [
            Location.objects.create(name='test1', point=Point(37.782305, -122.397391)),
            Location.objects.create(name='test2', point=Point(37.778877, -122.396293)),
            Location.objects.create(name='test3', point=Point(37.783757, -122.394922)),
        ]
        self.client = Client()

    def test_normal(self):
        response = self.client.get('/sqlapi/SELECT id,lat,lng FROM todos_locations')
        self.assertEqual(len(response.json()['results']), 3)
        self.assertEqual(response.json()['results'][0].keys(), ['id', 'lat', 'lng'])

    def test_partial_fields(self):
        response = self.client.get('/sqlapi/SELECT lat,lng FROM todos_locations')
        self.assertEqual(len(response.json()['results']), 3)
        self.assertEqual(response.json()['results'][0].keys(), ['lat', 'lng'])

    def test_page_size(self):
        response = self.client.get('/sqlapi/SELECT id,lat,lng FROM todos_locations LIMIT 1')
        self.assertEqual(len(response.json()['results']), 1)

    def test_filter_equal(self):
        response = self.client.get('/sqlapi/SELECT id FROM todos_locations WHERE name=\'test2\'')
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['id'], self.locations[1].id)

    def test_filter_near(self):
        response = self.client.get('/sqlapi/SELECT id,lat,lng FROM todos_locations WHERE distance((lat, lng), (37.782187, -122.396926)) < 100')
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['id'], self.locations[0].id)
