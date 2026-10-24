from uuid import uuid4
from django.db import models
from django.utils import timezone

class PaginaTienda(models.Model):
    tienda=models.OneToOneField('midistri_portal.Tienda',on_delete=models.PROTECT)
    revision=models.PositiveIntegerField(default=0)
    datos=models.JSONField(default=dict)
    publicada=models.ForeignKey('midistri_portal.VersionPagina',on_delete=models.PROTECT,null=True,related_name='+')
    pendiente=models.ForeignKey('midistri_portal.VersionPagina',on_delete=models.PROTECT,null=True,related_name='+')

class VersionPagina(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    tienda=models.ForeignKey('midistri_portal.Tienda',on_delete=models.PROTECT)
    revision=models.PositiveIntegerField()
    datos=models.JSONField(default=dict)
    huella=models.CharField(max_length=64)
    operador_id=models.PositiveIntegerField(null=True)
    estado=models.CharField(max_length=12,default='pendiente')
    creado=models.DateTimeField(default=timezone.now)

class EdicionPagina(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    pagina=models.ForeignKey(PaginaTienda,on_delete=models.PROTECT)
    operador_id=models.PositiveIntegerField()
    revision=models.PositiveIntegerField()
    huella=models.CharField(max_length=64)
    datos=models.JSONField(default=dict)
    creado=models.DateTimeField(default=timezone.now)
