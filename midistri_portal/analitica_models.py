"""Additive, nonfinancial activity and expiring read-report data."""
from uuid import uuid4
from django.db import models
from django.utils import timezone

class ControlAnalitica(models.Model):
    id=models.PositiveSmallIntegerField(primary_key=True,default=1)
    activa=models.BooleanField(default=False)
    cambiado=models.DateTimeField(default=timezone.now)

class IntervaloAnalitico(models.Model):
    distribuidora=models.ForeignKey('Distribuidora',on_delete=models.PROTECT)
    desde=models.DateTimeField(default=timezone.now)
    hasta=models.DateTimeField(null=True)
    class Meta:
        constraints=[models.UniqueConstraint(fields=['distribuidora'],condition=models.Q(hasta__isnull=True),name='analitica_intervalo_abierto')]

class SesionAnalitica(models.Model):
    clave=models.CharField(primary_key=True,max_length=64)
    vendedor_id=models.PositiveIntegerField()
    distribuidora_id=models.PositiveIntegerField()
    visita=models.UUIDField(default=uuid4)
    ultima=models.DateTimeField(default=timezone.now)
    cupo_inicio=models.DateTimeField(default=timezone.now)
    cupo=models.PositiveIntegerField(default=0)

class EventoAnalitico(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    fecha=models.DateTimeField(default=timezone.now)
    distribuidora_id=models.PositiveIntegerField()
    vendedor_id=models.PositiveIntegerField()
    vendedor=models.CharField(max_length=150)
    visita=models.UUIDField()
    tipo=models.CharField(max_length=30)
    producto_id=models.PositiveIntegerField(null=True)
    producto=models.CharField(max_length=200,blank=True)
    sku=models.CharField(max_length=80,blank=True)
    recurso=models.PositiveSmallIntegerField(null=True)
    cantidad=models.PositiveIntegerField(null=True)
    pedido=models.UUIDField(null=True)
    huella=models.CharField(max_length=64)
    class Meta:
        indexes=[models.Index(fields=['distribuidora_id','fecha'],name='analitica_dist_fecha'),models.Index(fields=['vendedor_id','fecha'],name='analitica_vend_fecha'),models.Index(fields=['producto_id','fecha'],name='analitica_prod_fecha')]

class ConsultaAnalitica(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    operador_id=models.PositiveIntegerField()
    distribuidora_id=models.PositiveIntegerField()
    distribuidoras=models.JSONField(default=list)
    desde=models.DateField()
    hasta=models.DateField()
    fuente=models.UUIDField(null=True)
    fase=models.CharField(max_length=16,default='vendedores')
    cursor=models.PositiveIntegerField(default=0)
    revision=models.PositiveIntegerField(default=0)
    datos=models.JSONField(default=dict)
    meta=models.JSONField(default=dict)
    completa=models.BooleanField(default=False)
    creado=models.DateTimeField(default=timezone.now)
    vence=models.DateTimeField()

class EvidenciaAnalitica(models.Model):
    distribuidora_id=models.PositiveIntegerField()
    vendedor_id=models.PositiveIntegerField()
    acreditada=models.DateTimeField(default=timezone.now)
    origen=models.CharField(max_length=30,default='sesion_existente')
    class Meta:
        constraints=[models.UniqueConstraint(fields=['distribuidora_id','vendedor_id'],name='analitica_identidad_acreditada')]

class IncidenciaAnalitica(models.Model):
    distribuidora_id=models.PositiveIntegerField()
    desde=models.DateTimeField(default=timezone.now)
    hasta=models.DateTimeField(default=timezone.now)
    class Meta:
        indexes=[models.Index(fields=['distribuidora_id','desde'],name='analitica_inc_dist_fecha')]
