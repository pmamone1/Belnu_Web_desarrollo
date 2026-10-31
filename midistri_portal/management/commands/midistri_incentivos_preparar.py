import json
from django.core.management.base import BaseCommand,CommandError
from midistri_portal.client import ApiError
from midistri_portal.incentivos_preparacion import procesar
class Command(BaseCommand):
    help='Prepara las semanas autorizadas usando la cola Urban; no envía SMTP ni activa recurrencias.'
    def handle(self,*args,**options):
        try:result=procesar()
        except ApiError as exc:raise CommandError(str(exc))
        self.stdout.write(json.dumps(result,ensure_ascii=False))
        if result['errores']:raise CommandError('Hay preparaciones bloqueadas. Revisar cobertura/configuración; no se enviaron fuentes parciales.')
