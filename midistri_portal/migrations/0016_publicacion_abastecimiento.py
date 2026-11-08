from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('midistri_portal', '0015_publicacion_descripcion'),
    ]

    operations = [
        migrations.AddField(
            model_name='publicacion',
            name='abastecimiento',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
