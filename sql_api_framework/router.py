import collections

import moz_sql_parser
from sql_api_framework.exceptions import BadRequestError, ParseError, ValidationError
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
        fields, resource, filters, max_results = parse_select_query(sql)

        if resource not in self.viewsets:
            raise ValidationError(f'Resource \'{resource}\' not found')
        viewset = self.viewsets[resource]
        viewset_instance = viewset(request, fields, filters, max_results)
        return viewset_instance.query()


def parse_select_query(sql):
    """
    :returns: fields, resource, filters, max_results
        - fields is a list of requested fields, i.e. SQL column names.
        - resource is the resource (aka "model", "type", i.e. the SQL table) being quired.
        - filters is a dict with the conditions on what results to return, i.e. the SQL WHERE clause.
        - max_results is a number specifying the maximum number of results to return, i.e. the SQL LIMIT.
    """
    try:
        query = moz_sql_parser.parse(sql)
    except Exception:
        raise ParseError('Unable to parse query')
    if 'AS' in sql:
        raise ParseError('Aliasing with \'AS\' is not supported')
    if 'JOIN' in sql:
        raise ParseError('Custom JOINs are not supported')

    if isinstance(query['select'], list):
        fields = [item['value'] for item in query['select']]
    elif isinstance(query['select'], str):
        fields = [query['select']]
    else:
        fields = [query['select']['value']]
    if fields == ['*']:
        raise ParseError('Wildcard select not supported, please specify each field you require')

    resource = query['from']

    filters = {}
    if 'where' in query:
        if list(query['where'].keys()) == ['and']:
            where_conditions = query['where']['and']
        else:
            where_conditions = [query['where']]
        for filter_type, args in (next(iter(condition.items())) for condition in where_conditions):
            if filter_type != 'eq':
                raise ParseError('Only equality operators (=) and and operators (AND) are supported in WHERE clauses')
            if not isinstance(args[0], str):
                raise ParseError('Filter name / field name in WHERE clauses must appear before operand')
            filter_name = f'{args[0]}_equal'
            if isinstance(args[1], str):
                if args[1] == 'TRUE':
                    operand = True
                elif args[1] == 'FALSE':
                    operand = False
                elif args[1] == 'NULL':
                    operand = None
                else:
                    raise ParseError(f'Unable to parse WHERE clause filter operand \'{operand}\'')
            elif isinstance(args[1], collections.Mapping):
                assert('literal' in args[1])
                operand = args[1]['literal']
            else:
                assert(isinstance(args[1], (int, float, list)))
                operand = args[1]
            filters[filter_name] = operand


    max_results = query['limit'] if 'limit' in query else None

    return fields, resource, filters, max_results
