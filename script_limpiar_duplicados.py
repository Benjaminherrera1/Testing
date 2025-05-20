# Script para limpiar duplicados en la base de datos
# Ejecutar con: python manage.py shell < script_limpiar_duplicados.py

from administracion.models import usuario_base
from django.db.models import Count

# Encontrar correos duplicados
duplicados = usuario_base.objects.values('correo').annotate(
    count=Count('correo')
).filter(count__gt=1)

print(f"Se encontraron {len(duplicados)} correos con registros duplicados")

# Para cada correo duplicado
for dup in duplicados:
    correo = dup['correo']
    print(f"Procesando duplicados para: {correo}")
    
    # Obtener todos los registros con este correo
    registros = usuario_base.objects.filter(correo=correo).order_by('-es_activo', 'id')
    
    # Mantener el primer registro (el más reciente o activo) y eliminar el resto
    primer_registro = registros.first()
    print(f"Manteniendo registro ID: {primer_registro.id}, Nombre: {primer_registro.nombre}")
    
    for registro in registros[1:]:
        print(f"Eliminando registro ID: {registro.id}, Nombre: {registro.nombre}")
        registro.delete()

print("Limpieza de duplicados completada")
