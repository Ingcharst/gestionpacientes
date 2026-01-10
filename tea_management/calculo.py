
from datetime import datetime

def calcular_edad(nacio):
    """Calcula la edad actual del paciente."""
    fecha = datetime.strptime(nacio, "%Y-%m-%d").date()

    today = datetime.now().date()
    age = today.year - fecha.year
    cumplio_este_año = (today.month, today.day) >= (fecha.month, fecha.day)
    
    if not cumplio_este_año:
        age -= 1
    
    if age >= 2:
        print(f"{age} años")
        return age
    else:
        meses = (today.year - fecha.year) * 12 + (today.month - fecha.month)
        if today.day < fecha.day:
            meses -= 1
        print(f"{meses} meses")
        return round(meses / 12, 2)

nacimiento = input("Ingrese la fecha de nacimiento (YYYY-MM-DD): ")
edad = calcular_edad(nacimiento)
print(f"La edad calculada es: {edad}")
