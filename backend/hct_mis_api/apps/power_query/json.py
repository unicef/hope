from typing import Any
from uuid import UUID

from django.contrib.gis.gdal.geometries import Point as GdalPoint
from django.contrib.gis.geos import Point as GeosPoint
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models


class PQJSONEncoder(DjangoJSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, models.Model):
            return str(o)
        if isinstance(o, UUID):
            return o.hex
        if isinstance(o, (GdalPoint, GeosPoint)):
            return [o.x, o.y]
        return super().default(o)
