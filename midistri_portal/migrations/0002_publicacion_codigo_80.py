from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('midistri_portal', '0001_initial')]
    operations = [migrations.AlterField(model_name='publicacion', name='codigo',
        field=models.CharField(blank=True, max_length=80))]
