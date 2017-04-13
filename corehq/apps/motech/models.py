from django.db import models
from django.utils.translation import ugettext_lazy as _


class ConnectedAccount(models.Model):
    domain = models.CharField(max_length=255, db_index=True)
    token = models.UUIDField(unique=True)
    token_password = models.BinaryField(max_length=16)  # 128 bit key
    server_type = models.CharField(max_length=32, choices=((_("OpenMRS"), 'openmrs'),))
    server_url = models.URLField()
    server_username = models.CharField(max_length=255)
