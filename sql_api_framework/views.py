from sql_api_framework.exceptions import ValidationError
from sql_api_framework.responses import ListResponse


class ViewSet():

    def __init__(self, request, queried_field_names, filters, limit):
        self.request = request
        self.queried_field_names = queried_field_names
        self.filters = filters
        self.limit = limit

    def get_serializer_class(self):
        return self.serializer_class

    def get_queryset(self):
        return self.get_serializer_class().get_model_class().objects.all()

    def limit_queryset(self, queryset):
        if self.limit is not None:
            queryset = queryset[:self.limit]
        return queryset

    def query(self):
        queryset = self.get_queryset()
        if self.filters:
            raise ValidationError(f'Filtering not yet available')
        queryset = self.limit_queryset(queryset)

        data = []
        for instance in queryset:
            serializer = self.get_serializer_class()(instance, queried_field_names=self.queried_field_names)
            data.append(serializer.get_data())
        return ListResponse(data)
