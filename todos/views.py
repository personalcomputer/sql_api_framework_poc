from sql_api_framework.exceptions import ValidationError
from sql_api_framework.serializers import Field, PointField, Serializer, StrField
from sql_api_framework.views import ViewSet
from todos.models import Location, TodoItem


class LocationSerializer(Serializer):
    fields_spec = [
        StrField('id'),
        Field('name'),
        Field('lat'),
        Field('lng'),
        PointField('coord_pair', source='point'),
    ]

    @classmethod
    def get_model_class(cls):
        return Location


class TodoItemSerializer(Serializer):
    fields_spec = [
        StrField('id'),
        Field('summary'),
        Field('description'),
        LocationSerializer('location'),
    ]

    @classmethod
    def get_model_class(cls):
        return TodoItem


class LocationViewSet(ViewSet):
    serializer_class = LocationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        for filter_name, arg in self.filters.items():
            # TODO: Lots of repetive code will end up here if on a large codebase with sql_api_framework. It can be
            #       generalized with a "FilterSet" concept. precedent:
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
                raise ValidationError(f'Unsupported filtering parameter: {filter_name}')
        return queryset


class TodoItemViewSet(ViewSet):
    serializer_class = TodoItemSerializer
