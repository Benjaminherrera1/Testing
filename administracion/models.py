from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.module_loading import import_string
from django.contrib.auth.models import User
from django.apps import apps
import uuid
import os


def document_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    unique_name = f"{uuid.uuid4()}.{ext}"
    return os.path.join("documentos", unique_name)

def logo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return os.path.join("site_media", "logos", f"site_logo.{ext}")


class Documento(models.Model):
    archivo = models.FileField(
        upload_to=document_upload_path ,
        storage=import_string(settings.STORAGES['private_files']["BACKEND"])(
            location=settings.STORAGES['private_files']["OPTIONS"]["location"]
        ),  
    )
    nombre = models.CharField(max_length=255)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    # Relación genérica
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  
    object_id = models.PositiveIntegerField()  
    content_object = GenericForeignKey('content_type', 'object_id')  

    def __str__(self):
        return f"{self.nombre} - Relacionado con ID {self.object_id} ({self.content_type})"

# Create your models here.
class Empresa (models.Model):
    id=models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    cantPersonas = models.IntegerField()
    año = models.IntegerField()
    actividad = models.CharField(max_length=255)
    pais = models.CharField(max_length=255)
    ciudad = models.CharField(max_length=255)
    isActive = models.BooleanField(default=True)
    def __str__(self):
        return self.nombre

class usuario_base(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    correo = models.CharField(max_length=255)
    contraseña = models.EmailField() 
    rol = models.CharField(max_length=100)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    es_activo = models.BooleanField(default=True)
    cargo = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20)
    empresa = models.ForeignKey('Empresa', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = 'Usuario Base'
        verbose_name_plural = 'Usuarios Base'


class solicitudContacto (models.Model):
    id=models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    cargo = models.CharField(max_length=255)
    correo = models.EmailField(max_length=255)
    telefono = models.CharField(max_length=20)
    empresa = models.CharField(max_length=255)
    pais = models.CharField(max_length=255)
    mensaje = models.TextField()
    origen = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)
    isActive = models.BooleanField(default=True)
    def __str__(self):
        return self.nombre


class Match (models.Model):
    id=models.AutoField(primary_key=True)
    estado = models.CharField(max_length=255)
    brl = models.CharField(max_length=255)
    trl = models.CharField(max_length=255)
    ejecutivo = models.ForeignKey(User, on_delete=models.CASCADE)
    desafio = models.ForeignKey('desafios.Desafio', on_delete=models.CASCADE)
    iniciativa = models.ForeignKey('iniciativas.Iniciativa', on_delete=models.CASCADE)

    isActive = models.BooleanField(default=True)
    def __str__(self):
        desafio_nombre = self.desafio.nombreDesafio if self.desafio else 'Sin Desafío'
        iniciativa_titulo = self.iniciativa.titulo if self.iniciativa else 'Sin Iniciativa'
        return f"Match ID {self.id}: {desafio_nombre} vs {iniciativa_titulo}"


class Objetivo (models.Model):
    id=models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    responsable = models.CharField(max_length=255)
    fechaObjetivo = models.DateTimeField()
    perspectiva = models.CharField(max_length=255)

    fecha = models.DateTimeField(auto_now_add=True)
    isActive = models.BooleanField(default=True)

    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='objetivos')
    def __str__(self):
        return f"{self.nombre} ({self.perspectiva})"

class Metrica (models.Model):
    id=models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    valorInicial = models.IntegerField()
    valorDeseado = models.IntegerField()
    periodo = models.CharField(max_length=255)

    fecha = models.DateTimeField(auto_now_add=True)
    isActive = models.BooleanField(default=True)

    objetivo = models.ForeignKey(Objetivo, on_delete=models.CASCADE, related_name='metricas') 
    def __str__(self):
        return f"{self.nombre} ({self.periodo})"

class Evaluacion (models.Model):
    id=models.AutoField(primary_key=True)
    valor = models.IntegerField()
    nota = models.TextField()

    fecha = models.DateTimeField()

    isActive = models.BooleanField(default=True)

    metrica = models.ForeignKey(Metrica, on_delete=models.CASCADE, related_name='evaluaciones') 
    def __str__(self):
        return f"Evaluación Metrica ID {self.metrica.id} - {self.fecha.strftime('%Y-%m-%d')}"

class Actividad (models.Model):
    id=models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    fechaCreacion = models.DateTimeField( auto_now_add=True)
    fechaRealizado = models.DateTimeField( blank=True, null=True)
    estado= models.CharField(max_length=255)
    responsable = models.CharField(max_length=255)

    isActive = models.BooleanField(default=True)

    metrica = models.ForeignKey(Metrica, on_delete=models.CASCADE, related_name='actividades') 
    def __str__(self):
        return f"Actividad: {self.nombre} ({self.estado})"


# --- ÚNICA DEFINICIÓN CORRECTA DE AdminConfig ---
class AdminConfig(models.Model):
    logo = models.ImageField(upload_to=logo_upload_path, null=True, blank=True, help_text="Logo principal del sitio. Se usa en el panel de administración y en el sitio público.")

    # Campo para guardar el color de fondo del header del sitio público
    public_header_background_color = models.CharField(
        max_length=7, # Para códigos hex como #RRGGBB
        default='#ffffff', # Color blanco por defecto
        help_text='Color de fondo del header principal del sitio (ej: #RRGGBB).',
        verbose_name='Color del Header Público'
    )

    # --- Campos específicos para el tema del panel de ADMIN ---
    BACKGROUND_THEME_CHOICES = [
        ('bg-light', 'Claro'),
        ('bg-dark', 'Oscuro'),
        ('bg-sky-light', 'Celeste Claro'),
        ('bg-sunset-soft', 'Atardecer Suave'),
        ('bg-forest-deep', 'Bosque Profundo'),
        ('bg-sandstone-warm', 'Arenisca Cálida'),
        ('bg-cool-grey', 'Gris Frío'),
        ('bg-teal-fresh', 'Verde Azulado Fresco'),
        # Añade aquí otros temas de fondo si los tienes
    ]
    background_theme = models.CharField(
        max_length=50,
        choices=BACKGROUND_THEME_CHOICES,
        default='bg-light', # Tema por defecto para el ADMIN
        help_text="Tema de fondo para el área de contenido del admin.",
        verbose_name="Tema de Fondo (Admin)"
    )

    SIDEBAR_THEME_CHOICES = [
        ('bar-darkblue', 'Azul Oscuro'), # Tu tema actual parece ser similar a este
        ('bar-midnight', 'Medianoche'),
        ('bar-lightgrey', 'Gris Claro'),
        ('bar-lila-elegant', 'Lila Elegante'),
        ('bar-gold-warm', 'Dorado Cálido'),
        ('bar-cyan-vibrant', 'Cyan Vibrante'),
        ('bar-clean-white', 'Blanco Limpio'),
        ('bar-maroon-bold', 'Granate Intenso'),
        ('bar-mint-pastel', 'Menta Pastel'),
        # Añade aquí otros temas de barra lateral si los tienes
    ]
    sidebar_theme = models.CharField(
        max_length=50,
        choices=SIDEBAR_THEME_CHOICES,
        default='bar-darkblue', # Tema por defecto para el ADMIN
         help_text="Tema de color para la barra lateral del admin.",
         verbose_name="Tema de Barra Lateral (Admin)"
    )

    class Meta:
        verbose_name = "Configuración del Sitio (Admin y Público)"
        verbose_name_plural = "Configuraciones del Sitio (Admin y Público)"

    # Singleton logic
    def save(self, *args, **kwargs):
        if not self.pk and AdminConfig.objects.exists():
             pass 

        if self.pk or not AdminConfig.objects.exists():
            super(AdminConfig, self).save(*args, **kwargs)


    def __str__(self):
        return "Configuración Principal del Sitio"