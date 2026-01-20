from apps.terapias.models import Terapia
from apps.usuarios.models import Usuario

def run():
    # Ver terapias
    terapias = Terapia.objects.filter(activo=True)
    print(f"Terapias: {terapias.count()}")
    for t in terapias:
        print(f"  - {t.nombre}")

    # Ver profesionales
    profesionales = Usuario.objects.filter(
        rol__in=['TERAPEUTA', 'PSICOLOGO', 'MEDICO'],
        is_active=True
    )
    print(f"Profesionales: {profesionales.count()}")
    for p in profesionales:
        print(f"  - {p.get_full_name()} - {p.rol}")