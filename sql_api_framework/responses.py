import simplejson as json
from django.http import HttpResponse


class Response(HttpResponse):

    def __init__(self, data, status_code=200):
        rendered_data = json.dumps(data)
        super().__init__(rendered_data, status=status_code, content_type='application/json')


class DetailResponse(Response):
    pass


class ListResponse(Response):

    def __init__(self, data):
        wrapped_data = {
            'num_results': len(data),
            'previous': None,
            'next': None,
            'results': data,
        }
        super().__init__(wrapped_data)
