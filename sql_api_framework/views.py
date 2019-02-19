from sql_api_framework.responses import ListResponse


class ViewSet():

    def __init__(self, request, queried_field_names, filters, max_results):
        self.request = request
        self.queried_field_names = queried_field_names
        self.filters = filters
        self.max_results = max_results

    def get_serializer_class(self):
        if not hasattr(self, 'serializer_class'):
            raise NotImplementedError()
        return self.serializer_class

    def get_queryset(self):
        return self.get_serializer_class().get_model_class().objects.all()

    def limit_queryset(self, queryset):
        if self.max_results is not None:
            queryset = queryset[:self.max_results]
        return queryset

    def query(self):
        queryset = self.get_queryset()
        queryset = self.limit_queryset(queryset)

        data = []
        for instance in queryset:
            serializer = self.get_serializer_class()()
            serializer.set_queried_field_names(self.queried_field_names)
            data.append(serializer.to_representation(instance))
        return ListResponse(data)
