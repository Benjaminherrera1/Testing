# home/urls.py
from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='index'), 
    path('detalle/<int:id>/', views.detalle, name='detalle'),
    path('contacto/', views.contacto, name='contacto'),
    path('postula/', views.postula, name='postula'),
]