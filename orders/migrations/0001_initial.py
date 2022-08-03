# Generated by Django 4.0 on 2022-07-20 16:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_vendedor', models.IntegerField(blank=True, null=True, verbose_name='Numero de vendedor')),
                ('nombre_vendedor', models.CharField(blank=True, max_length=50, null=True, verbose_name='Nombre de vendedor')),
                ('order_number', models.CharField(max_length=30, verbose_name='Numero de Pedido')),
                ('first_name', models.CharField(max_length=50, verbose_name='Nombre')),
                ('last_name', models.CharField(max_length=50, verbose_name='Apellido')),
                ('phone', models.CharField(blank=True, max_length=50, verbose_name='Telefono')),
                ('email', models.CharField(max_length=50, verbose_name='Email')),
                ('order_total', models.DecimalField(decimal_places=2, max_digits=10, null=True, verbose_name='Total')),
                ('status', models.CharField(choices=[('New', 'Nuevo'), ('Accepted', 'Aceptado'), ('Completed', 'Completado'), ('Cancelado', 'Cancelado')], default='New', max_length=50, verbose_name='Estado')),
                ('ip', models.CharField(blank=True, max_length=20, verbose_name='IP')),
                ('is_ordered', models.BooleanField(default=False, verbose_name='Ordenado')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualizacion')),
            ],
            options={
                'verbose_name': 'Pedido',
                'verbose_name_plural': 'Pedidos',
            },
        ),
        migrations.CreateModel(
            name='OrderProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(verbose_name='Cantidad')),
                ('product_price', models.FloatField(verbose_name='Precio')),
                ('ordered', models.BooleanField(default=False, verbose_name='Ordenado')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creacion')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualizacion')),
                ('numero_pedido', models.CharField(blank=True, max_length=30, null=True, verbose_name='Numero de Pedido')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order', verbose_name='Pedido')),
            ],
            options={
                'verbose_name': 'Producto Pedido',
                'verbose_name_plural': 'Productos del Pedido',
            },
        ),
    ]
