#!/bin/bash
# Script para ejecutar tests del proyecto TEA Management

echo "============================================"
echo "   TEA MANAGEMENT - EJECUTOR DE TESTS"
echo "============================================"
echo ""

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para ejecutar tests
run_tests() {
    local module=$1
    local description=$2
    
    echo -e "${YELLOW}► Ejecutando tests: $description${NC}"
    python manage.py test apps.$module --verbosity=2
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Tests de $description completados exitosamente${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ Tests de $description fallaron${NC}"
        echo ""
        return 1
    fi
}

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo -e "${RED}Error: No se encontró manage.py${NC}"
    echo "Por favor ejecuta este script desde la raíz del proyecto"
    exit 1
fi

# Menú
echo "Selecciona una opción:"
echo "1) Ejecutar TODOS los tests"
echo "2) Tests de Usuarios"
echo "3) Tests de Terapias"
echo "4) Tests de Consultorios"
echo "5) Tests de Procedimientos"
echo "6) Tests con Coverage"
echo "7) Tests rápidos (sin coverage)"
echo ""
read -p "Opción: " option

case $option in
    1)
        echo -e "${YELLOW}Ejecutando todos los tests...${NC}"
        echo ""
        run_tests "usuarios" "Usuarios"
        run_tests "terapias" "Terapias"
        run_tests "consultorios" "Consultorios"
        run_tests "procedimientos" "Procedimientos"
        echo -e "${GREEN}=== Todos los tests completados ===${NC}"
        ;;
    2)
        run_tests "usuarios" "Usuarios"
        ;;
    3)
        run_tests "terapias" "Terapias"
        ;;
    4)
        run_tests "consultorios" "Consultorios"
        ;;
    5)
        run_tests "procedimientos" "Procedimientos"
        ;;
    6)
        echo -e "${YELLOW}Ejecutando tests con coverage...${NC}"
        coverage run --source='apps' manage.py test
        echo ""
        echo -e "${YELLOW}Generando reporte de coverage...${NC}"
        coverage report
        coverage html
        echo ""
        echo -e "${GREEN}✓ Reporte HTML generado en htmlcov/index.html${NC}"
        ;;
    7)
        echo -e "${YELLOW}Ejecutando tests rápidos...${NC}"
        python manage.py test --parallel --failfast
        ;;
    *)
        echo -e "${RED}Opción inválida${NC}"
        exit 1
        ;;
esac

echo ""
echo "============================================"
echo "   Tests finalizados"
echo "============================================"
