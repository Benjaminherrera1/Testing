# administracion/context_processors.py
from .models import AdminConfig

def admin_config(request):
    """
    Context processor para añadir la configuración del admin al contexto.
    """
    try:
        config = AdminConfig.objects.get(pk=1)
    except AdminConfig.DoesNotExist:
        # Si no existe la configuración, crea una por defecto
        config = AdminConfig.objects.create(pk=1)

    return {
        'admin_config': config,
        # Pasa los nombres de las clases CSS al contexto
        'background_theme_class': config.background_theme,
        'sidebar_theme_class': config.sidebar_theme,
    }