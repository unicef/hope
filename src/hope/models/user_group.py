from django.contrib.auth.models import Group
from django.db import models
from natural_keys import NaturalKeyModel


class UserGroup(NaturalKeyModel, models.Model):
    user = models.ForeignKey("account.User", related_name="user_groups", on_delete=models.CASCADE)
    group = models.ForeignKey(Group, related_name="user_groups", on_delete=models.CASCADE)
    business_area = models.ForeignKey("core.BusinessArea", related_name="user_groups", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("business_area", "user", "group")

    def __str__(self) -> str:
        return f"{self.user} {self.group} in {self.business_area}"
