import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q


class AppUser(AbstractUser):
    id = models.UUIDField(
        "ユーザーID", primary_key=True, default=uuid.uuid7, editable=False
    )
    employee_id = models.IntegerField("社員番号", unique=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)

    REQUIRED_FIELDS = ["employee_id"]

    class Meta:
        db_table = "app_user"

        constraints = [
            models.CheckConstraint(
                condition=Q(employee_id__gt=0),
                name="app_user_employee_id_gt_0",
            ),
        ]

    def __str__(self):
        return self.username
