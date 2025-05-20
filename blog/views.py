# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post # ¡Importante! Asegúrate de que Post se importa desde .models
from django.contrib import messages # Importado pero no usado en las vistas públicas aquí
from bs4 import BeautifulSoup
from django.http import JsonResponse # Importado pero no usado
from django.db.models import Q
from django.contrib.auth.decorators import login_required # Usado para post_preview
# Create your views here.

# Función auxiliar
def truncate_text_exclude_images(contenido, word_limit):
    soup = BeautifulSoup(contenido, 'html.parser')

    for img in soup.find_all('img'):
        img.decompose()

    text = soup.get_text()
    words = text.split()
    truncated_text = ' '.join(words[:word_limit])

    return truncated_text

# Vista 1: blog(request)
def blog(request):
    query = request.GET.get('q', '')
    posts = Post.objects.filter(is_active=True,publico=True).order_by('-fecha')

    if query:
        # Filtra los posts por título o contenido
        posts = posts.filter(Q(titulo__icontains=query) | Q(contenido__icontains=query))

    for post in posts:
        post.contenido_preview = truncate_text_exclude_images(post.contenido, 15)

    return render(request, 'blog.html', {'posts': posts, 'query': query})


# Vista 2: post(request, slug)
def post(request, slug):
    post = get_object_or_404(Post.objects, slug=slug) # Considera filtrar por publico=True, is_active=True
    return render(request, 'post.html', {'post': post})

# Vista 3: post_preview(request, slug)
@login_required
def post_preview(request,slug):
    post = get_object_or_404(Post.objects, slug=slug) # Considera filtrar por is_active=True si no es público

    post.contenido_preview = truncate_text_exclude_images(post.contenido, 15)

    return render(request, 'post_prev.html', {'post': post})