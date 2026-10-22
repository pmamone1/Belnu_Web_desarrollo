from uuid import uuid4
from django.db import models
from django.utils import timezone

class Distribuidora(models.Model):
    id=models.PositiveIntegerField(primary_key=True)
    nombre=models.CharField(max_length=150)
    activa=models.BooleanField(default=True)

class Publicacion(models.Model):
    producto_id=models.PositiveIntegerField()
    distribuidora=models.ForeignKey(Distribuidora,on_delete=models.PROTECT)
    nombre=models.CharField(max_length=200)
    codigo=models.CharField(max_length=80,blank=True)
    categoria=models.CharField(max_length=100,blank=True)
    precio=models.DecimalField(max_digits=12,decimal_places=2)
    pvp=models.DecimalField(max_digits=12,decimal_places=2)
    imagenes=models.JSONField(default=list)
    display=models.PositiveIntegerField(null=True)
    activa=models.BooleanField(default=True)
    class Meta:
        unique_together=[('producto_id','distribuidora')]
        ordering=['nombre']

class Sincronizacion(models.Model):
    id=models.PositiveSmallIntegerField(primary_key=True,default=1)
    completada=models.DateTimeField(null=True)
    error=models.CharField(max_length=150,blank=True)

class PedidoLocal(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    vendedor_id=models.PositiveIntegerField()
    distribuidora=models.ForeignKey(Distribuidora,on_delete=models.PROTECT)
    datos=models.JSONField(default=dict)
    respuesta=models.JSONField(default=dict)
    estado=models.CharField(max_length=16,default='pendiente')
    error=models.CharField(max_length=300,blank=True)
    creado=models.DateTimeField(default=timezone.now)
