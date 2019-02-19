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
    def __init__(self, name=None, instance=None, source=None):
        super().__init__(name, source)
        self.instance = instance
        self._queried_field_names = None
        self._fields_dict = None

    def get_data(self):
        return self.to_representation(self.instance)

    def get_model_class(self):
        raise NotImplementedError()

    @classmethod
    def get_fields(cls):
        if not hasattr(cls, '_fields_dict'):
            if not hasattr(cls, 'fields_spec'):
                raise NotImplementedError()
            cls._fields_dict = {field.name: field for field in cls.fields_spec}
        return cls._fields_dict

    def set_queried_field_names(self, queried_field_names):
        queried_field_identifiers = OrderedDict()
        for raw_field_name in queried_field_names:
            field_parts = raw_field_name.split('.')
            field_name = field_parts[0]
            if field_name not in self.get_fields():
                raise ValidationError(f'Requested field {raw_field_name} not available')
            if len(field_parts) == 2:
                subfield_name = field_parts[1]
                if subfield_name not in self.get_fields()[field_name].get_fields():
                    raise ValidationError(f'Requested field {raw_field_name} not available')
                if field_name in queried_field_identifiers:
                    queried_field_identifiers[field_name].append(subfield_name)
                else:
                    queried_field_identifiers[field_name] = [subfield_name]
            else:
                queried_field_identifiers[field_name] = None
        self._queried_field_identifiers = queried_field_identifiers

    def to_representation(self, value):
        serialized = OrderedDict()
        for field_name, queried_subfield_names in self._queried_field_identifiers.items():
            field = self.get_fields()[field_name]
            field_value = getattr(value, field.source)
            if queried_subfield_names:
                field.set_queried_field_names(queried_subfield_names)
            serialized[field_name] = field.to_representation(field_value)
        return serialized


class StrField(Field):
    def to_representation(self, value):
        return str(value)


class PointField(Field):
    def to_representation(self, value):
        return (value.x, value.y)
