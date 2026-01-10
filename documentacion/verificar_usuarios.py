#!/usr/bin/env python
"""
Script de verificación para el módulo de Usuarios
Ejecutar desde la raíz del proyecto: python verificar_usuarios.py
"""
import os
import sys

def verificar_estructura():
    """Verifica que todos los archivos necesarios existan."""
    print("🔍 Verificando estructura de archivos...\n")
    
    archivos_requeridos = [
        'templates/usuarios/usuario_list.html',
        'templates/usuarios/usuario_detail.html',
        'templates/usuarios/usuario_form.html',
        'templates/usuarios/perfil_form.html',
        'templates/usuarios/partials/usuario_table.html',
        'templates/usuarios/partials/usuario_estado_badge.html',
    ]
    
    todos_ok = True
    for archivo in archivos_requeridos:
        if os.path.exists(archivo):
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - NO ENCONTRADO")
            todos_ok = False
    
    return todos_ok

def verificar_vistas():
    """Verifica que las vistas estén definidas."""
    print("\n🔍 Verificando vistas...\n")
    
    try:
        from apps.usuarios import views
        
        vistas_requeridas = [
            'usuario_list',
            'usuario_detail',
            'usuario_create',
            'usuario_update',
            'perfil_update',
            'usuario_toggle_estado',
        ]
        
        todos_ok = True
        for vista in vistas_requeridas:
            if hasattr(views, vista):
                print(f"✅ views.{vista}")
            else:
                print(f"❌ views.{vista} - NO ENCONTRADA")
                todos_ok = False
        
        return todos_ok
    except ImportError as e:
        print(f"❌ Error al importar views: {e}")
        return False

def verificar_urls():
    """Verifica que las URLs estén configuradas."""
    print("\n🔍 Verificando URLs...\n")
    
    try:
        from django.urls import reverse
        from django.urls.exceptions import NoReverseMatch
        
        urls_requeridas = [
            'usuario_list',
            'usuario_create',
            'usuario_detail',
            'usuario_update',
            'perfil_update',
            'usuario_toggle_estado',
        ]
        
        todos_ok = True
        for url in urls_requeridas:
            try:
                if 'pk' in url or url in ['usuario_detail', 'usuario_update', 'perfil_update', 'usuario_toggle_estado']:
                    # Estas necesitan parámetros
                    reverse(url, kwargs={'pk': 1})
                else:
                    reverse(url)
                print(f"✅ {url}")
            except NoReverseMatch:
                print(f"❌ {url} - NO CONFIGURADA")
                todos_ok = False
        
        return todos_ok
    except Exception as e:
        print(f"❌ Error al verificar URLs: {e}")
        return False

def verificar_modelos():
    """Verifica que los modelos existan."""
    print("\n🔍 Verificando modelos...\n")
    
    try:
        from apps.usuarios.models import Usuario, Perfil, RegistroAcceso
        
        print("✅ Modelo Usuario")
        print("✅ Modelo Perfil")
        print("✅ Modelo RegistroAcceso")
        
        # Verificar campos importantes
        campos_usuario = ['rol', 'estado', 'foto_perfil', 'cedula_profesional']
        for campo in campos_usuario:
            if hasattr(Usuario, campo):
                print(f"  ✅ Usuario.{campo}")
            else:
                print(f"  ❌ Usuario.{campo} - NO ENCONTRADO")
        
        return True
    except ImportError as e:
        print(f"❌ Error al importar modelos: {e}")
        return False

def main():
    """Función principal."""
    print("=" * 60)
    print("🔧 VERIFICADOR DEL MÓDULO DE USUARIOS")
    print("=" * 60)
    
    # Configurar Django
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()
    except Exception as e:
        print(f"❌ Error al configurar Django: {e}")
        print("\nEjecuta este script desde la raíz del proyecto:")
        print("  python verificar_usuarios.py")
        sys.exit(1)
    
    resultados = {
        'Estructura de archivos': verificar_estructura(),
        'Vistas': verificar_vistas(),
        'URLs': verificar_urls(),
        'Modelos': verificar_modelos(),
    }
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    for categoria, resultado in resultados.items():
        estado = "✅ OK" if resultado else "❌ FALLO"
        print(f"{estado} - {categoria}")
    
    if all(resultados.values()):
        print("\n🎉 ¡Todo está correcto! El módulo de Usuarios está listo.")
        print("\nPuedes acceder a:")
        print("  - Lista: http://localhost:8000/usuarios/")
        print("  - Crear: http://localhost:8000/usuarios/crear/")
    else:
        print("\n⚠️  Hay problemas que necesitan resolverse.")
        print("Revisa los errores marcados con ❌ arriba.")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
