"""Read-only contract status, without bearer tokens or seller details."""
import json
from django.core.management.base import BaseCommand,CommandError
from midistri_portal.dispositivos import activo
from midistri_portal.client import api,ApiError
from midistri_portal.models import DispositivoRecordado

class Command(BaseCommand):
    help='Consulta capacidades privadas y cantidades locales sin modificar datos.'
    def add_arguments(self,parser):parser.add_argument('--local',action='store_true')
    def handle(self,*args,**options):
        result={'habilitado':activo(),'dispositivos':DispositivoRecordado.objects.count(),
            'revocados':DispositivoRecordado.objects.filter(revocado=True).count(),
            'revocaciones_pendientes':DispositivoRecordado.objects.filter(remoto_pendiente=True).count()}
        if not options['local']:
            try:caps=api('capabilities')
            except ApiError as exc:raise CommandError(str(exc))
            if caps.get('seller_device')!=1:raise CommandError('Urban no ofrece el contrato seller_device=1.')
            result['urban_habilitado']=caps.get('seller_device_habilitado') is True
        self.stdout.write(json.dumps(result))
