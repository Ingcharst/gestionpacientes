#!/bin/bash

# ============================================
# Script de Instalación Automatizada
# Sistema de Gestión TEA - Sprint 1
# ============================================

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     Sistema de Gestión TEA - Instalación Automatizada         ║"
echo "║                     Sprint 1 - v1.0.0                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Colores para mensajes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    print_error "Error: No se encontró manage.py"
    print_info "Asegúrate de estar en el directorio tea_management"
    exit 1
fi

print_info "Directorio del proyecto verificado"
echo ""

# ============================================
# 1. Verificar Python
# ============================================
print_info "Verificando instalación de Python..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado"
    print_info "Por favor instala Python 3.8 o superior"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
print_success "Python encontrado: $PYTHON_VERSION"
echo ""

# ============================================
# 2. Crear entorno virtual
# ============================================
print_info "Creando entorno virtual..."

if [ -d "venv" ]; then
    print_warning "El entorno virtual ya existe"
    read -p "¿Deseas recrearlo? (s/n): " recreate
    if [ "$recreate" = "s" ]; then
        print_info "Eliminando entorno virtual existente..."
        rm -rf venv
        python3 -m venv venv
        print_success "Entorno virtual recreado"
    else
        print_info "Usando entorno virtual existente"
    fi
else
    python3 -m venv venv
    print_success "Entorno virtual creado"
fi
echo ""

# ============================================
# 3. Activar entorno virtual y instalar dependencias
# ============================================
print_info "Activando entorno virtual..."

# Detectar sistema operativo
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/Mac
    source venv/bin/activate
fi

print_success "Entorno virtual activado"
echo ""

print_info "Instalando dependencias..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    print_success "Dependencias instaladas correctamente"
else
    print_error "Error al instalar dependencias"
    exit 1
fi
echo ""

# ============================================
# 4. Configurar archivo .env
# ============================================
print_info "Configurando archivo de entorno..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    print_success "Archivo .env creado desde .env.example"
    print_warning "IMPORTANTE: Edita el archivo .env con tus configuraciones"
    print_info "Especialmente: DB_NAME, DB_USER, DB_PASSWORD, SECRET_KEY"
else
    print_warning "El archivo .env ya existe"
fi
echo ""

# ============================================
# 5. Solicitar configuración de base de datos
# ============================================
print_info "Configuración de Base de Datos MySQL"
print_warning "Asegúrate de tener MySQL instalado y corriendo"
echo ""

read -p "¿Deseas configurar la base de datos ahora? (s/n): " config_db

if [ "$config_db" = "s" ]; then
    read -p "Nombre de la base de datos [tea_management]: " db_name
    db_name=${db_name:-tea_management}
    
    read -p "Usuario MySQL [root]: " db_user
    db_user=${db_user:-root}
    
    read -sp "Contraseña MySQL: " db_password
    echo ""
    
    read -p "Host MySQL [localhost]: " db_host
    db_host=${db_host:-localhost}
    
    read -p "Puerto MySQL [3306]: " db_port
    db_port=${db_port:-3306}
    
    # Actualizar archivo .env
    sed -i.bak "s/DB_NAME=.*/DB_NAME=$db_name/" .env
    sed -i.bak "s/DB_USER=.*/DB_USER=$db_user/" .env
    sed -i.bak "s/DB_PASSWORD=.*/DB_PASSWORD=$db_password/" .env
    sed -i.bak "s/DB_HOST=.*/DB_HOST=$db_host/" .env
    sed -i.bak "s/DB_PORT=.*/DB_PORT=$db_port/" .env
    
    print_success "Configuración de base de datos actualizada en .env"
    
    # Intentar crear la base de datos
    print_info "Intentando crear la base de datos..."
    mysql -u$db_user -p$db_password -h$db_host -P$db_port -e "CREATE DATABASE IF NOT EXISTS $db_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        print_success "Base de datos '$db_name' creada o ya existe"
    else
        print_warning "No se pudo crear la base de datos automáticamente"
        print_info "Créala manualmente con:"
        echo "    mysql -u$db_user -p"
        echo "    CREATE DATABASE $db_name CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    fi
fi
echo ""

# ============================================
# 6. Ejecutar migraciones
# ============================================
print_info "Ejecutando migraciones de base de datos..."

python manage.py makemigrations
if [ $? -eq 0 ]; then
    print_success "Migraciones creadas"
else
    print_error "Error al crear migraciones"
    exit 1
fi

python manage.py migrate
if [ $? -eq 0 ]; then
    print_success "Migraciones aplicadas correctamente"
else
    print_error "Error al aplicar migraciones"
    print_warning "Verifica la configuración de la base de datos en .env"
    exit 1
fi
echo ""

# ============================================
# 7. Crear superusuario
# ============================================
print_info "Creación de superusuario"

read -p "¿Deseas crear un superusuario ahora? (s/n): " create_super

if [ "$create_super" = "s" ]; then
    python manage.py createsuperuser
    if [ $? -eq 0 ]; then
        print_success "Superusuario creado exitosamente"
    else
        print_warning "No se pudo crear el superusuario"
    fi
else
    print_info "Puedes crear el superusuario después con:"
    echo "    python manage.py createsuperuser"
fi
echo ""

# ============================================
# 8. Ejecutar tests
# ============================================
print_info "¿Deseas ejecutar los tests para verificar la instalación?"
read -p "(s/n): " run_tests

if [ "$run_tests" = "s" ]; then
    print_info "Ejecutando tests..."
    python manage.py test
    if [ $? -eq 0 ]; then
        print_success "Todos los tests pasaron exitosamente"
    else
        print_warning "Algunos tests fallaron"
    fi
fi
echo ""

# ============================================
# 9. Crear directorios necesarios
# ============================================
print_info "Creando directorios necesarios..."

mkdir -p media/usuarios/fotos
mkdir -p static
mkdir -p logs

print_success "Directorios creados"
echo ""

# ============================================
# 10. Resumen final
# ============================================
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║              ✅ Instalación Completada                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

print_success "El sistema está listo para usar!"
echo ""

print_info "Para iniciar el servidor de desarrollo, ejecuta:"
echo "    python manage.py runserver"
echo ""

print_info "URLs disponibles:"
echo "    Frontend:   http://127.0.0.1:8000/"
echo "    Admin:      http://127.0.0.1:8000/admin/"
echo "    API Docs:   http://127.0.0.1:8000/api/docs/"
echo ""

print_info "Comandos útiles:"
echo "    python manage.py test              # Ejecutar tests"
echo "    python manage.py createsuperuser   # Crear superusuario"
echo "    python manage.py shell             # Shell interactivo"
echo ""

print_warning "Recuerda revisar y actualizar el archivo .env con:"
echo "    - SECRET_KEY (genera uno nuevo para producción)"
echo "    - Configuración de base de datos"
echo "    - Configuración de email (opcional)"
echo ""

print_info "Documentación disponible:"
echo "    - README.md          : Documentación completa"
echo "    - INICIO_RAPIDO.md   : Guía de inicio rápido"
echo "    - SPRINT_1_REVIEW.md : Detalles del Sprint 1"
echo ""

print_success "¡Disfruta desarrollando! 🚀"
