# procedimientos/migrations/0013_recreate_evolucionpaciente.py

# Generated manually to recreate missing EvolucionPaciente table

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings
import django.utils.timezone

class Migration(migrations.Migration):

    # La dependencia debe ser la última migración ANTES de esta, que fue la 0012.
    dependencies = [
        ('grupos', '0003_alter_asignaciongrupo_numero_terapias_asignadas'),
        ('procedimientos', '0012_valoracioninicial_diagnostico_cie10_texto'),
        ('terapias', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EvolucionPaciente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_sesion', models.DateField(default=django.utils.timezone.now, verbose_name='Fecha de la Sesión')),
                ('hora_inicio', models.TimeField(blank=True, null=True, verbose_name='Hora de Inicio')),
                ('hora_fin', models.TimeField(blank=True, null=True, verbose_name='Hora de Fin')),
                ('tipo_sesion', models.CharField(choices=[('INDIVIDUAL', 'Individual'), ('GRUPAL', 'Grupal'), ('EVALUACION', 'Evaluación'), ('INTERCONSULTA', 'Interconsulta')], default='GRUPAL', max_length=20, verbose_name='Tipo de Sesión')),
                ('numero_sesion', models.IntegerField(default=1, help_text='Sesión número X del total asignado', verbose_name='Número de Sesión')),
                ('asistio', models.BooleanField(default=True, verbose_name='Asistió a la Sesión')),
                ('objetivos_trabajados', models.TextField(blank=True, help_text='Objetivos terapéuticos abordados en la sesión', verbose_name='Objetivos Trabajados')),
                ('actividades_realizadas', models.TextField(blank=True, help_text='Descripción de actividades y ejercicios realizados', verbose_name='Actividades Realizadas')),
                ('desempeno', models.CharField(blank=True, choices=[('EXCELENTE', 'Excelente'), ('BUENO', 'Bueno'), ('REGULAR', 'Regular'), ('REQUIERE_APOYO', 'Requiere Apoyo'), ('NO_PARTICIPO', 'No Participó')], max_length=20, verbose_name='Desempeño del Paciente')),
                ('logros_obtenidos', models.TextField(blank=True, help_text='Avances y logros observados en la sesión', verbose_name='Logros Obtenidos')),
                ('dificultades_observadas', models.TextField(blank=True, help_text='Dificultades o retos encontrados', verbose_name='Dificultades Observadas')),
                ('observaciones_conducta', models.TextField(blank=True, help_text='Aspectos conductuales relevantes', verbose_name='Observaciones de Conducta')),
                ('observaciones_generales', models.TextField(blank=True, verbose_name='Observaciones Generales')),
                ('recomendaciones', models.TextField(blank=True, help_text='Recomendaciones para próximas sesiones o para el hogar', verbose_name='Recomendaciones')),
                ('proximos_objetivos', models.TextField(blank=True, help_text='Objetivos para trabajar en próximas sesiones', verbose_name='Próximos Objetivos')),
                ('nivel_atencion', models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], help_text='1=Muy bajo, 5=Excelente', null=True, verbose_name='Nivel de Atención (1-5)')),
                ('nivel_participacion', models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], null=True, verbose_name='Nivel de Participación (1-5)')),
                ('nivel_colaboracion', models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], null=True, verbose_name='Nivel de Colaboración (1-5)')),
                ('nivel_comprension', models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], null=True, verbose_name='Nivel de Comprensión (1-5)')),
                ('material_utilizado', models.TextField(blank=True, help_text='Material didáctico o recursos utilizados', verbose_name='Material Utilizado')),
                ('tarea_asignada', models.TextField(blank=True, help_text='Tareas o ejercicios para realizar en casa', verbose_name='Tarea Asignada')),
                ('fecha_registro', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Fecha de Registro')),
                ('ultima_modificacion', models.DateTimeField(auto_now=True, verbose_name='Última Modificación')),
                ('firmado', models.BooleanField(default=False, help_text='Indica si la evolución ha sido finalizada y firmada', verbose_name='Evolución Firmada')),

                # Definición de las claves foráneas
                ('paciente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='evoluciones_paciente', to='procedimientos.paciente', verbose_name='Paciente')),
                ('profesional', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='evoluciones_registradas', to=settings.AUTH_USER_MODEL, verbose_name='Profesional')),
                ('terapia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='evoluciones_terapias', to='terapias.terapia', verbose_name='Terapia')),
                ('grupo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='evoluciones_grupo', to='grupos.grupoterapeutico', verbose_name='Grupo Terapéutico')),
            ],
            options={
                'verbose_name': 'Evolución de Paciente',
                'verbose_name_plural': 'Evoluciones de Pacientes',
                'ordering': ['-fecha_sesion', '-hora_inicio'],
            },
        ),

        # Creación de Índices
        migrations.AddIndex(
            model_name='evolucionpaciente',
            index=models.Index(fields=['paciente', 'fecha_sesion'], name='procedimien_pacient_d67112_idx'),
        ),
        migrations.AddIndex(
            model_name='evolucionpaciente',
            index=models.Index(fields=['profesional', 'fecha_sesion'], name='procedimien_profesi_a03c89_idx'),
        ),
        migrations.AddIndex(
            model_name='evolucionpaciente',
            index=models.Index(fields=['terapia', 'fecha_sesion'], name='procedimien_terapia_ac659f_idx'),
        ),
    ]