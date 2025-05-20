from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', include(('home.urls', 'home'), namespace='home')),

    path('autenticacion/', include('autenticacion.urls')), 
    path('administracion/', include('administracion.urls')),
    path('admin/', admin.site.urls), 
    path('postulacion/', include('desafios.urls')),
    path('postulacionIniciativa/', include('iniciativas.urls')),
    path('blog/', include(('blog.urls', 'blog'), namespace='blog')),  
    path('captcha/', include('captcha.urls')), 
    path('summernote/', include('django_summernote.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)