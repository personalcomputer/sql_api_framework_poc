import uuid

from django.db import models
from django.contrib.gis.db import models as gis_models


class Spot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    point = gis_models.PointField()

    @property
    def lat(self):
        return self.point.x

    @property
    def lng(self):
        return self.point.y
