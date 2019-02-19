from collections import OrderedDict

from sql_api_framework.exceptions import ValidationError


class Field():
    def __init__(self, name, source=None):
        self.source = source
        self.name = name
        if not source:
            self.source = self.name

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class Serializer(Field):
    def __init__(self, instance=None, data=None, queried_field_names=None):
        self.instance = instance
        self.data = data
        self.validated = False
        self.queried_field_names = queried_field_names

    def is_valid(self):
        nonexistent_field_names = self.data.keys() - self._get_fields().keys()
        if nonexistent_field_names:
            nonexistent_field_names_str = ', '.join((f'\'{field}\'' for field in nonexistent_field_names))
            raise ValidationError(f'Provided field(s) {nonexistent_field_names_str} not available')

        self._validate(self.data)
        self.validated = True

    def save(self):
        if not self.validated:
            raise AssertionError('Must call .is_valid() before calling .save()')
        self.instance = self.to_internal_value(self.data)
        return self.instance

    def get_data(self):
        return self.to_representation(self.instance)

    def get_model_class(self):
        raise NotImplementedError()

    def _validate(self, data):
        pass

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

    def to_internal_value(self, data):
        if self.instance is None:
            # Create
            instance = self.get_model_class()()
        else:
            # Update
            instance = self.instance

        for field_name, value in data.items():
            field_class = self._get_fields()[field_name]
            setattr(instance, field_class.source, field_class.to_internal_value(value))
        return instance

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
