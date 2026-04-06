from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adopciones', '0002_calendariovacunacion_entradacalendario'),
    ]

    operations = [
        migrations.AddField(
            model_name='entradacalendario',
            name='foto_comprobante',
            field=models.ImageField(blank=True, null=True, upload_to='comprobantes_vacunas/'),
        ),
    ]
