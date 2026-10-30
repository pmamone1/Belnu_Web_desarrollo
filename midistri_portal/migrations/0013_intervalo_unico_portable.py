"""Forward-only compatibility repair: keep0012 and all recorded coverage intact."""
from django.db import migrations,models
from django.db.models import Count,Q


def validar(apps,schema_editor):
    model=apps.get_model('midistri_portal','IntervaloAnalitico')
    duplicate=model.objects.using(schema_editor.connection.alias).filter(hasta__isnull=True).values('distribuidora_id').annotate(n=Count('pk')).filter(n__gt=1)
    if duplicate.exists():raise RuntimeError('Hay intervalos analiticos abiertos duplicados. Detenido sin fusionar ni borrar datos; requiere conciliacion antes de migrar.')


def marcar(apps,schema_editor):
    qs=apps.get_model('midistri_portal','IntervaloAnalitico').objects.using(schema_editor.connection.alias)
    qs.filter(hasta__isnull=True).update(abierto_unico=1)
    qs.filter(hasta__isnull=False).update(abierto_unico=None)


class Migration(migrations.Migration):
    atomic=False
    dependencies=[('midistri_portal','0012_analitica')]
    operations=[
        migrations.RunPython(validar,migrations.RunPython.noop),
        migrations.AddField(model_name='intervaloanalitico',name='abierto_unico',field=models.PositiveSmallIntegerField(null=True,default=1,editable=False)),
        migrations.RunPython(marcar,migrations.RunPython.noop,atomic=True),
        migrations.RemoveConstraint(model_name='intervaloanalitico',name='analitica_intervalo_abierto'),
        migrations.AddConstraint(model_name='intervaloanalitico',constraint=models.UniqueConstraint(fields=('distribuidora','abierto_unico'),name='analitica_un_abierto_tienda')),
        migrations.AddConstraint(model_name='intervaloanalitico',constraint=models.CheckConstraint(check=(Q(hasta__isnull=True,abierto_unico=1)&Q(abierto_unico__isnull=False))|Q(hasta__isnull=False,abierto_unico__isnull=True),name='analitica_intervalo_estado')),
    ]
