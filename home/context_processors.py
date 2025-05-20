from administracion.models import AdminConfig

def site_config(request):

    try:

        config = AdminConfig.objects.get(pk=1)
    except AdminConfig.DoesNotExist:
        
        config = None 
    site_logo_url = config.logo.url if config and config.logo else None
    site_header_bg_color = config.public_header_background_color if config and config.public_header_background_color else '#ffffff'

    return {
        'site_logo_url': site_logo_url,
        'site_header_bg_color': site_header_bg_color,
    }