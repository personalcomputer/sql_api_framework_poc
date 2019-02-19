from sql_api_framework.exceptions import ValidationError, ParseError
from sql_api_framework.responses import ListResponse


class ViewSet():

    def __init__(self, request, queried_field_names, filters, max_results):
        self.request = request
        self.queried_field_names = queried_field_names
        self.filters = filters
        self.max_results = max_results

    def get_serializer_class(self):
        return self.serializer_class

    def get_queryset(self):
        return self.get_serializer_class().get_model_class().objects.all()

    def filter_queryset(self, queryset, filters):
        for filter_name, arg in filters.items():
            # TODO: Lots of repetive code will end up here if on a large codebase. It can be generalized with a
            #       "FilterSet" concept. precedent:
            #       https://django-filter.readthedocs.io/en/master/guide/rest_framework.html
            if filter_name == 'id_equal':
                if not isinstance(arg, str):
                    raise ValidationError('id must be a string')
                queryset = queryset.filter(id=arg)
            elif filter_name == 'name_equal':
                if not isinstance(arg, str):
                    raise ValidationError('name must be a string')
                queryset = queryset.filter(name=arg)
            else:
                raise ParseError(f'Unsupported filtering parameter: {filter_name}')
        return queryset

    def limit_queryset(self, queryset):
        if self.max_results is not None:
            queryset = queryset[:self.max_results]
        return queryset

    def query(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset, self.filters)
        queryset = self.limit_queryset(queryset)

        data = []
        for instance in queryset:
            serializer = self.get_serializer_class()()
            serializer.set_queried_field_names(self.queried_field_names)
            data.append(serializer.to_representation(instance))
        return ListResponse(data)
