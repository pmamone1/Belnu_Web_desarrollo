import json
from django.core.management.base import BaseCommand
from midistri_portal.analitica_captura import cambiar_estado,activa
class Command(BaseCommand):
    help='Activa/desactiva sólo la medición de actividad. Sin comunicaciones ni movimientos.'
    def add_arguments(self,p):
        group=p.add_mutually_exclusive_group();group.add_argument('--activar',action='store_true');group.add_argument('--desactivar',action='store_true')
    def handle(self,*args,**opts):
        data=cambiar_estado(True) if opts['activar'] else cambiar_estado(False) if opts['desactivar'] else {'activa':activa()}
        self.stdout.write(json.dumps(data))
