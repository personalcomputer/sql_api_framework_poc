import logging

import moz_sql_parser

from sql_api_framework.exceptions import BadRequestError, ParseError
from sql_api_framework.responses import Response


def handle_exceptions_as_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except BadRequestError as error:
            return Response({'error': error.message}, status_code=400)
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
            raise ParseError('No query provided')
        fields, resource, filters, limit = parse_select_query(sql)

        if fields == ['*']:
            raise ParseError('Wildcard select not supported, please specify each field you require.')

        if resource not in self.viewsets:
            raise ParseError(f'Resource \'{resource}\' not found')
        viewset = self.viewsets[resource]
        viewset_instance = viewset(request, fields, filters, limit)
        return viewset_instance.query()


def parse_select_query(sql):
    """
    returns fields, resource, filters, limit
    """
    try:
        query = moz_sql_parser.parse(sql)
    except Exception:
        raise ParseError('Unable to parse query')
    if 'AS' in sql:
        raise ParseError('Aliasing with \'AS\' is not supported')
    if 'JOIN' in sql:
        raise ParseError('Custom JOINs are not supported')

    resource = query['from']

    if isinstance(query['select'], list):
        fields = [item['value'] for item in query['select']]
    elif isinstance(query['select'], str):
        fields = [query['select']]

    filters = query['where'] if 'where' in query else {}
    limit = query['limit'] if 'limit' in query else None

    return fields, resource, filters, limit
