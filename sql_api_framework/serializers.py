from collections import OrderedDict

from sql_api_framework.exceptions import ValidationError


class Field():
    def __init__(self, name, source=None):
        self.source = source
        self.name = name
        if not source:
            self.source = self.name

    def to_representation(self, value):
        return value


class Serializer(Field):
    def __init__(self, instance=None, queried_field_names=None):
        self.instance = instance
        self.queried_field_names = queried_field_names

    def get_data(self):
        return self.to_representation(self.instance)

    def get_model_class(self):
        raise NotImplementedError()

    @classmethod
    def _get_fields(cls):
        if not hasattr(cls, 'fields'):
            raise NotImplementedError()
        fields_dict = {}
        for field_class in cls.fields:
            if hasattr(field_class, 'fields'):
                # Subfields
                for subfield_class in field_class.fields:
                    # Note: support for 2nd level subfields
                    fields_dict[field_class.name + ''] = field_class

            else:
                fields_dict[field_class.name] = field_class

    def to_representation(self, value):
        unavailable_field_names = set(self.queried_field_names) - self._get_fields().keys()
        if unavailable_field_names:
            unavailable_field_names_str = ', '.join((f'\'{field}\'' for field in unavailable_field_names))
            raise ValidationError(f'Requested field(s) {unavailable_field_names_str} not available')

        serialized = OrderedDict()
        for field_name in self.queried_field_names:
            field_class = self._get_fields()[field_name]
            value = getattr(self.instance, field_class.source)
            serialized[field_name] = field_class.to_representation(value)
        return serialized


class StrField(Field):
    def to_representation(self, value):
        return str(value)


class PointField(Field):
    def to_representation(self, value):
        return (value.x, value.y)
