import simplejson as json
from django.http import HttpResponse
import moz_sql_parser

from parking.models import Spot


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


class ValidationError(Exception):

    def __init__(self, message):
        self.message = message


class UnsupportedSQLError(ValidationError):

    def __init__(self):
        super().__init__('Unsupported SQL feature in query')


def sql_api_router(request, sql):
    try:
        if not sql.strip():
            raise ValidationError('No query provided')
        try:
            query = moz_sql_parser.parse(sql)
        except Exception:
            raise ValidationError('Unable to parse query')
        # if len(query) == 0:
        #     raise ValidationError('No query provided')
        # if len(query) > 1:
        #     raise ValidationError('Only one statement per request supported at this time')
        # statement = query[0]
        statement = query
        query_type = 'select'
        resource = statement['from']
        fields = {item['value'] for item in statement['select']}
        filters = statement['where'] if 'where' in statement else {}
        limit = statement['limit'] if 'limit' in statement else None

        if fields == '*':
            raise ValidationError('Wildcard select not support, please specify each field you require.')

        if query_type == 'select':
            if resource == 'parking_spots':
                return SpotsViewSet(request, fields, filters, limit).query()
            else:
                raise ValidationError(f'Resource \'{resource}\' not found')
        else:
            raise UnsupportedSQLError()
    except ValidationError as error:
        return Response({'error': error.message})


class ViewSet(object):

    def __init__(self, request, fields, filters, limit):
        self.request = request
        self.fields = fields
        self.filters = filters
        self.limit = limit

    def query(self):
        raise NotImplementedError()


class SpotsViewSet(ViewSet):

    def get_queryset(self):
        queryset = Spot.objects.all()
        if self.filters:
            raise ValidationError(f'Filtering not yet available')
        if self.limit is not None:
            queryset = queryset.limit(self.limit)
        return queryset

    def serialize(self, queryset):
        data = []
        for instance in queryset:
            serialized_instance = {}
            if 'id' in self.fields:
                serialized_instance['id'] = str(instance.id)
            if 'lat' in self.fields:
                serialized_instance['lat'] = instance.lat
            if 'lng' in self.fields:
                serialized_instance['lng'] = instance.lng
            data.append(serialized_instance)
        return data

    def query(self):
        print(str(self.fields))
        queryset = self.get_queryset()
        data = self.serialize(queryset)
        return ListResponse(data)
