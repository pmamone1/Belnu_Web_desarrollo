"""Local revocation and retry ledger; never an authority for seller permissions."""
from uuid import uuid4
from django.db import models
from django.utils import timezone

class DispositivoRecordado(models.Model):
    id=models.UUIDField(primary_key=True, default=uuid4, editable=False)
    hash_cookie=models.CharField(max_length=64, unique=True)
    revocado=models.BooleanField(default=False)
    remoto_pendiente=models.BooleanField(default=False)
    creado=models.DateTimeField(default=timezone.now)
    ultimo_uso=models.DateTimeField(default=timezone.now)
