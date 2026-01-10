#!/usr/bin/env python
"""
Script para ejecutar tests del proyecto TEA Management con reporte visual.
Uso: python run_tests.py [modulo]
"""
import sys
import os
import subprocess
from datetime import datetime

# Colores para terminal
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Imprime el header del script."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}TEA MANAGEMENT - EJECUTOR DE TESTS{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado."""
    print(f"{Colors.YELLOW}► {description}...{Colors.END}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        print(f"{Colors.GREEN}✓ {description} completado{Colors.END}\n")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"{Colors.RED}✗ {description} falló{Colors.END}")
        print(f"{Colors.RED}{e.stderr}{Colors.END}\n")
        return False, e.stderr

def run_all_tests():
    """Ejecuta todos los tests."""
    modules = ['usuarios', 'terapias', 'consultorios', 'procedimientos']
    results = {}
    
    for module in modules:
        print(f"\n{Colors.BOLD}Testing: apps.{module}{Colors.END}")
        print("-" * 60)
        success, output = run_command(
            f"python manage.py test apps.{module} --verbosity=2",
            f"Tests de {module.capitalize()}"
        )
        results[module] = success
    
    return results

def run_coverage():
    """Ejecuta tests con coverage."""
    print(f"\n{Colors.BOLD}Ejecutando tests con coverage...{Colors.END}\n")
    
    # Run tests with coverage
    success1, _ = run_command(
        "coverage run --source='apps' manage.py test",
        "Ejecutar tests con coverage"
    )
    
    if success1:
        # Generate report
        success2, output = run_command(
            "coverage report",
            "Generar reporte de coverage"
        )
        
        if success2:
            print(output)
        
        # Generate HTML
        run_command(
            "coverage html",
            "Generar reporte HTML"
        )
        print(f"\n{Colors.GREEN}Reporte HTML disponible en: htmlcov/index.html{Colors.END}")

def print_summary(results):
    """Imprime resumen de resultados."""
    print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}RESUMEN DE RESULTADOS{Colors.END}")
    print(f"{Colors.BOLD}{'='*60}{Colors.END}\n")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed
    
    for module, success in results.items():
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if success else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"  {module.capitalize():<20} {status}")
    
    print(f"\n{Colors.BOLD}Total: {total} | Passed: {Colors.GREEN}{passed}{Colors.END} | Failed: {Colors.RED}{failed}{Colors.END}{Colors.BOLD}{Colors.END}\n")
    
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}¡Todos los tests pasaron! 🎉{Colors.END}\n")
    else:
        print(f"{Colors.RED}{Colors.BOLD}Algunos tests fallaron. Por favor revisa los errores arriba.{Colors.END}\n")

def main():
    """Función principal."""
    print_header()
    
    if len(sys.argv) > 1:
        module = sys.argv[1]
        if module == 'all':
            results = run_all_tests()
            print_summary(results)
        elif module == 'coverage':
            run_coverage()
        elif module in ['usuarios', 'terapias', 'consultorios', 'procedimientos']:
            success, _ = run_command(
                f"python manage.py test apps.{module} --verbosity=2",
                f"Tests de {module.capitalize()}"
            )
            print_summary({module: success})
        else:
            print(f"{Colors.RED}Módulo inválido: {module}{Colors.END}")
            print("\nMódulos disponibles: usuarios, terapias, consultorios, procedimientos, all, coverage")
            sys.exit(1)
    else:
        # Menú interactivo
        print("Opciones:")
        print("1) Ejecutar TODOS los tests")
        print("2) Tests de Usuarios")
        print("3) Tests de Terapias")
        print("4) Tests de Consultorios")
        print("5) Tests de Procedimientos")
        print("6) Tests con Coverage")
        print("7) Salir")
        
        try:
            option = input(f"\n{Colors.BOLD}Selecciona una opción (1-7): {Colors.END}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Cancelado por el usuario{Colors.END}")
            sys.exit(0)
        
        if option == '1':
            results = run_all_tests()
            print_summary(results)
        elif option == '2':
            success, _ = run_command("python manage.py test apps.usuarios --verbosity=2", "Tests de Usuarios")
            print_summary({'usuarios': success})
        elif option == '3':
            success, _ = run_command("python manage.py test apps.terapias --verbosity=2", "Tests de Terapias")
            print_summary({'terapias': success})
        elif option == '4':
            success, _ = run_command("python manage.py test apps.consultorios --verbosity=2", "Tests de Consultorios")
            print_summary({'consultorios': success})
        elif option == '5':
            success, _ = run_command("python manage.py test apps.procedimientos --verbosity=2", "Tests de Procedimientos")
            print_summary({'procedimientos': success})
        elif option == '6':
            run_coverage()
        elif option == '7':
            print(f"\n{Colors.YELLOW}Saliendo...{Colors.END}")
            sys.exit(0)
        else:
            print(f"{Colors.RED}Opción inválida{Colors.END}")
            sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests cancelados por el usuario{Colors.END}\n")
        sys.exit(0)
