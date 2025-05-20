# blog/urls.py
from django.urls import path
# from django.shortcuts import render # No parece necesario importarlo aquí
from . import views # Esto importa tu blog/views.py

urlpatterns = [
    # Este es el patrón para la raíz ('') en blog.urls.
    # Usa la vista `views.blog` (la que lista los posts)
    # y le asigna el nombre 'listar_posts' para que coincida con {% url 'blog:listar_posts' %}
    path('', views.blog, name='listar_posts'), # <-- CAMBIA views.posts A views.blog

    # Tus otros patrones de URL de blog:
    # La vista `views.post` en tu blog/views.py parece ser para el detalle del post.
    # Le asignaremos el nombre 'post_detalle' por claridad.
    path('<slug:slug>/', views.post, name='post_detalle'), # Renombrado 'post' a 'post_detalle'

    # La vista `views.post_preview` está decorada con @login_required, es probablemente para el admin/preview.
    path('prev/<slug:slug>/', views.post_preview, name='post_preview'), # Deja este nombre

    # Asegúrate de que si usas {% url 'blog:post' ... %} en otras plantillas,
    # cambies esos usos a {% url 'blog:post_detalle' ... %}.
]