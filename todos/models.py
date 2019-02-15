import uuid

from django.db import models
from django.contrib.gis.db import models as gis_models


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.TextField()
    point = gis_models.PointField()

    @property
    def lat(self):
        return self.point.x

    @property
    def lng(self):
        return self.point.y


class TodoItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    summary = models.TextField()
    description = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.PROTECT)
