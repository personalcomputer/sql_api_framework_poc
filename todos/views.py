from sql_api_framework.serializers import Field, PointField, Serializer, StrField
from sql_api_framework.views import ViewSet

from todos.models import Location, TodoItem


class LocationSerializer(Serializer):
    _fields = [
        StrField('id'),
        Field('name'),
        Field('lat'),
        Field('lng'),
        PointField('coord_pair', source='point'),
    ]

    @classmethod
    def get_model_class(cls):
        return Location


class LocationViewSet(ViewSet):
    serializer_class = LocationSerializer


class TodoItemSerializer(Serializer):
    _fields = [
        StrField('id'),
        Field('summary'),
        Field('description'),
    ]

    @classmethod
    def get_model_class(cls):
        return TodoItem


class TodoItemViewSet(ViewSet):
    serializer_class = TodoItemSerializer
