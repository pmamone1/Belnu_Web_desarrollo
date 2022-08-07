# Generated by Django 3.2.14 on 2022-08-04 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0008_productgallery'),
    ]

    operations = [
        migrations.AddField(
            model_name='banner',
            name='date_created',
            field=models.DateField(auto_now_add=True, null=True, verbose_name='Fecha de creacion'),
        ),
        migrations.AddField(
            model_name='banner',
            name='proveedor',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Proveedor'),
        ),
    ]
