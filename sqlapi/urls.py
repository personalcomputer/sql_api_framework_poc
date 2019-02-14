from django.contrib import admin
from django.urls import path, re_path

import parking.views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^sqlapi/v1/(?P<sql>[\w|\W]+)$', parking.views.sql_api_router, name='sql_api'),
]
