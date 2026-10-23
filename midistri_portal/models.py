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


class Tienda(models.Model):
    distribuidora=models.OneToOneField(Distribuidora,on_delete=models.PROTECT)
    logo=models.FileField(upload_to='midistri/tiendas/',blank=True)
    email=models.EmailField(max_length=254,blank=True)
    telefono=models.CharField(max_length=40,blank=True)
    bienvenida=models.CharField(max_length=500,blank=True)
    instrucciones=models.CharField(max_length=1000,blank=True)
    revision=models.PositiveIntegerField(default=0)

class CambioTienda(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    tienda=models.ForeignKey(Tienda,on_delete=models.PROTECT,related_name='cambios')
    operador_id=models.PositiveIntegerField()
    antes=models.JSONField(default=dict)
    despues=models.JSONField(default=dict)
    huella=models.CharField(max_length=64)
    creado=models.DateTimeField(default=timezone.now)
    confirmado_urban=models.BooleanField(default=False)


class SesionVendedorPortal(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid4,editable=False)
    prueba_hash=models.CharField(max_length=64)
    navegador_hash=models.CharField(max_length=64)
    token_urban=models.TextField()
    vendedor_id=models.PositiveIntegerField()
    distribuidora_id=models.PositiveIntegerField()
    datos=models.JSONField(default=dict)
    creado=models.DateTimeField(default=timezone.now)
    actividad=models.DateTimeField(default=timezone.now)
    revocado=models.BooleanField(default=False)
