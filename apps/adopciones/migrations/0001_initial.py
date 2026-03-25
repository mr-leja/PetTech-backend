import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('familias', '0005_add_foto_perfil_to_familia'),
        ('mascotas', '0004_mascota_carnet_vacunas_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='SolicitudAdopcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.CharField(
                    choices=[('PENDIENTE', 'Pendiente'), ('APROBADA', 'Aprobada'), ('RECHAZADA', 'Rechazada')],
                    default='PENDIENTE',
                    max_length=10,
                )),
                ('mensaje', models.TextField(blank=True, help_text='Mensaje opcional de la familia al administrador.')),
                ('notas_admin', models.TextField(blank=True, help_text='Notas del administrador sobre la decisión.')),
                ('fecha_solicitud', models.DateTimeField(auto_now_add=True)),
                ('fecha_decision', models.DateTimeField(blank=True, null=True)),
                ('familia', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='solicitudes',
                    to='familias.familia',
                )),
                ('mascota', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='solicitudes',
                    to='mascotas.mascota',
                )),
            ],
            options={
                'verbose_name': 'Solicitud de Adopción',
                'verbose_name_plural': 'Solicitudes de Adopción',
                'db_table': 'solicitudes_adopcion',
                'ordering': ['-fecha_solicitud'],
            },
        ),
        migrations.CreateModel(
            name='Adopcion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_adopcion', models.DateTimeField(auto_now_add=True)),
                ('notas', models.TextField(blank=True)),
                ('solicitud', models.OneToOneField(
                    on_delete=django.db.models.deletion.PROTECT,
                    related_name='adopcion',
                    to='adopciones.solicitudadopcion',
                )),
            ],
            options={
                'verbose_name': 'Adopción',
                'verbose_name_plural': 'Adopciones',
                'db_table': 'adopciones',
                'ordering': ['-fecha_adopcion'],
            },
        ),
    ]
