from django.contrib.gis.geos import Point
from django.test import Client, TestCase

from parking.models import Spot


class ListTest(TestCase):
    def setUp(self):
        self.spots = [
            Spot.objects.create(point=Point(37.782305, -122.397391)),
            Spot.objects.create(point=Point(37.778877, -122.396293)),
            Spot.objects.create(point=Point(37.783757, -122.394922)),
        ]
        self.client = Client()

    def test_normal(self):
        response = self.client.get('/sqlapi/v1/SELECT id,lat,lng FROM parking_spots')
        self.assertEqual(len(response.json()['results']), 3)

    def test_filter_near(self):
        response = self.client.get('/sqlapi/v1/SELECT id,lat,lng FROM parking_spots WHERE distance((lat, lng), (37.782187, -122.396926)) < 100')
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['id'], self.spots[0].id)

    def test_page_size(self):
        response = self.client.get('/sqlapi/v1/SELECT id,lat,lng FROM parking_spots LIMIT 1')
        self.assertEqual(len(response.json()['results']), 1)
