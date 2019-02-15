from django.contrib import admin
from django.urls import path, re_path

import todos.views
import sql_api_framework.router


urlpatterns = [
    path('admin/', admin.site.urls),
]

router = sql_api_framework.router.Router()
router.register_viewset(todos.views.LocationViewSet, 'todos_locations')
router.register_viewset(todos.views.TodoItemViewSet, 'todos_todo_items')
urlpatterns.extend([
    re_path(r'^sqlapi/(?P<sql>[\w|\W]+)$', router.query_view, name='sql_api')
])
