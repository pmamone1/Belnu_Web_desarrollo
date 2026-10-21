from django.core.management.base import BaseCommand,CommandError
from midistri_portal.services import sincronizar
from midistri_portal.client import ApiError
class Command(BaseCommand):
    help='Actualiza exclusivamente el catálogo de Urban Soft, sin borrar archivos ni históricos.'
    def handle(self,*args,**options):
        try:count=sincronizar()
        except (ApiError,ValueError) as e:raise CommandError(str(e))
        self.stdout.write('Catálogo sincronizado: '+str(count)+' publicaciones.')
