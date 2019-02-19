from django.contrib.gis.geos import Point
from django.test import Client, TestCase
from todos.models import Location, TodoItem


class LocationListingTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.locations = [
            Location.objects.create(name='test1', point=Point(37.782305, -122.397391)),
            Location.objects.create(name='test2', point=Point(37.778877, -122.396293)),
            Location.objects.create(name='test3', point=Point(37.783757, -122.394922)),
        ]
        cls.client = Client()

    def test_normal(self):
        response = self.client.get('/sqlapi/SELECT id,lat,lng,coord_pair FROM todos_locations')
        self.assertEqual(len(response.json()['results']), 3)
        self.assertListEqual(list(response.json()['results'][0].keys()), ['id', 'lat', 'lng', 'coord_pair'])

    def test_partial_fields(self):
        response = self.client.get('/sqlapi/SELECT lat,lng FROM todos_locations')
        self.assertEqual(len(response.json()['results']), 3)
        self.assertListEqual(list(response.json()['results'][0].keys()), ['lat', 'lng'])

    def test_unavailable_field(self):
        response = self.client.get('/sqlapi/SELECT point FROM todos_locations')
        self.assertEqual(response.status_code, 400)

    def test_page_size(self):
        response = self.client.get('/sqlapi/SELECT id FROM todos_locations LIMIT 1')
        self.assertEqual(len(response.json()['results']), 1)

    def test_filter_equal(self):
        response = self.client.get('/sqlapi/SELECT id FROM todos_locations WHERE name=\'test2\'')
        self.assertEqual(len(response.json()['results']), 1)
        self.assertEqual(response.json()['results'][0]['id'], str(self.locations[1].id))


class TodoItemListingTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        facebook = Location.objects.create(name='Facebook', point=Point(37.481212, -122.152517))
        cls.tasks = [
            TodoItem.objects.create(summary='Move fast', location=facebook),
            TodoItem.objects.create(summary='Break things', location=facebook),
        ]
        cls.client = Client()

    def test_normal(self):
        response = self.client.get('/sqlapi/SELECT id,summary FROM todos_todo_items')
        self.assertEqual(len(response.json()['results']), 2)
        self.assertListEqual(list(response.json()['results'][0].keys()), ['id', 'summary'])

    def test_join(self):
        response = self.client.get('/sqlapi/SELECT id,summary,location.lat,location.lng FROM todos_todo_items')
        self.assertEqual(len(response.json()['results']), 2)
        self.assertListEqual(list(response.json()['results'][0].keys()), ['id', 'summary', 'location'])
        self.assertListEqual(list(response.json()['results'][0]['location'].keys()), ['lat', 'lng'])
