import moz_sql_parser
from sql_api_framework.exceptions import ValidationError
from sql_api_framework.responses import Response


def handle_exceptions_as_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as error:
            return Response({'error': error.message})
    return wrapper


class Router():

    def __init__(self):
        self.viewsets = {}

    def register_viewset(self, viewset, name):
        if name in self.viewsets:
            raise AssertionError(f'Attempted to register multiple viewsets under the same name, \'{name}\'.')
        self.viewsets[name] = viewset

    @handle_exceptions_as_errors
    def query_view(self, request, sql):
        if not sql.strip():
            raise ValidationError('No query provided')
        try:
            query = moz_sql_parser.parse(sql)
        except Exception:
            raise ValidationError('Unable to parse query')
        statement = query
        query_type = 'select'
        resource = statement['from']
        if isinstance(statement['select'], list):
            fields = {item['value'] for item in statement['select']}
        elif isinstance(statement['select'], str):
            fields = {statement['select']}
        else:
            fields = {statement['select']['value']}
        filters = statement['where'] if 'where' in statement else {}
        limit = statement['limit'] if 'limit' in statement else None

        if fields == {'*'}:
            raise ValidationError('Wildcard select not supported, please specify each field you require.')

        if query_type == 'select':
            if resource not in self.viewsets:
                raise ValidationError(f'Resource \'{resource}\' not found')
            viewset = self.viewsets[resource]
            viewset_instance = viewset(request, fields, filters, limit)
            return viewset_instance.query()
        else:
            raise ValidationError('Unsupported SQL statement in query')
