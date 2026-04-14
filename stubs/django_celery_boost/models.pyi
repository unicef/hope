from django.db import models

class CeleryTaskModel(models.Model):
    class Meta:
        abstract: bool

class AsyncJobModel(CeleryTaskModel):
    class Meta:
        abstract: bool
