# administracion/views.py

from django.shortcuts import render, redirect, get_object_or_404
from desafios.models import Desafio, PostulacionDesafio
from iniciativas.models import PostulacionIniciativa, Iniciativa
from .models import Empresa, usuario_base, Documento, solicitudContacto , Match, Objetivo, Metrica, Evaluacion, Actividad, AdminConfig
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from .forms import DesafioForm, DesafioBulkUpdateForm, PostForm, IniciativaForm, MatchForm, ObjetivoForm, MetricaForm, EvaluacionForm, ActividadForm, EjecutivoCreationForm, AdminConfigForm
from blog.models import Post
from django.urls import reverse
from django.http import Http404, FileResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
import os
from django.db.models import Q
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from django.utils.module_loading import import_string


def es_admin(user):
    return user.is_superuser

def truncate_text_exclude_images(contenido, word_limit):
    soup = BeautifulSoup(contenido, 'html.parser')

    for img in soup.find_all('img'):
        img.decompose()

    text = soup.get_text()
    words = text.split()
    truncated_text = ' '.join(words[:word_limit])

    return truncated_text


@login_required
def serve_document(request, filename):
    try:
        storage = import_string(settings.STORAGES['private_files']["BACKEND"])(
            location=settings.STORAGES['private_files']["OPTIONS"]["location"]
        )
        file_full_path = os.path.join("documentos", filename)

        if storage.exists(file_full_path):
             with storage.open(file_full_path, 'rb') as f:
                from mimetypes import guess_type
                content_type, encoding = guess_type(filename)
                response = HttpResponse(f.read(), content_type=content_type or 'application/octet-stream')
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(filename)}"'
                return response
        else:
             raise Http404("File not found")
    except Exception as e:
        print(f"Error serving document {filename}: {e}")
        raise Http404("File not found or error serving.")


@login_required
def metabase(request):
    import jwt
    import time

    METABASE_SECRET_KEY="0a68a280256d5c23aa1994bd64809b297106e0d5511ac97fc74da9b90c378473"
    METABASE_SITE_URL="https://metabase.camiongo.com"


    payload = {
        "resource": {"dashboard": 101},
        "params": {},
        "exp": round(time.time()) + (60 * settings.METABASE_SESSION_DURATION_MINUTES),
    }
    token = jwt.encode(payload, METABASE_SECRET_KEY, algorithm="HS256")

    iframeUrl = f"{METABASE_SITE_URL}/embed/dashboard/{token}#bordered=true&titled=true"

    return render(request, "dashboard.html", {
        'active_page': 'metabase',
        'title': 'Dashboard',
        "dashboard_url": iframeUrl
    })


@login_required
def matches(request):
    query = request.GET.get('q', '')
    matches = Match.objects.filter(isActive=True)
    if query:
        matches = matches.filter(
            Q(desafio__nombreDesafio__icontains=query) |
            Q(iniciativa__titulo__icontains=query) |
            Q(id__icontains=query)
        ).distinct()

    matches = matches.select_related('desafio', 'iniciativa').order_by('-id')

    return render(request, 'matches.html', {
        'active_page': 'matches',
        'title': 'Matches',
        'matches': matches,
        'query': query
    })

@login_required
def crear_match(request, desafio_id=0, iniciativa_id=0, match_id=None):
    desafio = None
    if desafio_id:
        desafio = get_object_or_404(Desafio, id=desafio_id)

    iniciativa = None
    if iniciativa_id:
        iniciativa = get_object_or_404(Iniciativa, id=iniciativa_id)

    match = None
    if match_id:
        match = get_object_or_404(Match.objects.select_related('desafio', 'iniciativa'), id=match_id, isActive=True)

    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save(commit=False)
            if not match_id:
                 match.ejecutivo = request.user
                 if desafio:
                      match.desafio = desafio
                 if iniciativa:
                      match.iniciativa = iniciativa

            match.save()
            messages.success(request, f"Match ID {match.id} guardado correctamente.")
            return redirect('matches')
        else:
            print(form.errors)
            messages.error(request, "Hubo un error al guardar el match. Revisa los campos.")
    else:
        if match:
            form = MatchForm(instance=match)
        elif desafio and iniciativa:
             form = MatchForm(initial={
                'desafio': desafio.id,
                'iniciativa': iniciativa.id
            })
        else:
             form = MatchForm()

    if 'ejecutivo' in form.fields and form.instance.pk is None:
        form.initial['ejecutivo'] = request.user.id


    return render(request, 'crear_match.html', {
        'form': form,
        'desafio': desafio,
        'iniciativa': iniciativa,
        'active_page': 'crear_match',
        'match': match,
    })

@login_required
def verEvaluacion(request, id):
    evaluacion = get_object_or_404(Evaluacion.objects.select_related('metrica__objetivo__match'), id=id, isActive=True)

    context = {
        'evaluacion': evaluacion,
        'active_page': 'matches',
        'title': 'Ver Evaluación',
    }

    return render(request, 'ver_evaluacion.html', context)

@login_required
@user_passes_test(es_admin)
def eliminarMatch(request, id):
    match = get_object_or_404(Match, id=id, isActive=True)
    if request.method == 'POST':
        match.isActive = False
        match.save()
        messages.success(request, f"Match ID {id} eliminado (marcado como inactivo) correctamente.")
    return redirect('matches')


@login_required
def gestionar_objetivo(request, match_id, objetivo_id=None):
    match = get_object_or_404(Match, id=match_id, isActive=True)
    objetivo = None

    if objetivo_id:
        objetivo = get_object_or_404(Objetivo, id=objetivo_id, match=match, isActive=True)

    if request.method == 'POST':
        form = ObjetivoForm(request.POST, instance=objetivo)
        if form.is_valid():
            objetivo = form.save(commit=False)
            objetivo.match = match
            objetivo.save()
            messages.success(request, "Objetivo guardado correctamente.")
            return redirect('matches')
        else:
            messages.error(request, "Error al guardar el objetivo. Revisa los campos.")
    else:
        form = ObjetivoForm(instance=objetivo)

    return render(request, 'gestionar_objetivo.html', {
        'form': form,
        'match': match,
        'objetivo': objetivo,
        'active_page': 'matches',
        'title': 'Gestionar Objetivo',
    })

@login_required
def gestionar_metrica(request, objetivo_id, metrica_id=None):
    objetivo = get_object_or_404(Objetivo.objects.select_related('match'), id=objetivo_id, isActive=True)
    metrica = None

    if metrica_id:
        metrica = get_object_or_404(Metrica, id=metrica_id, objetivo=objetivo, isActive=True)

    if request.method == 'POST':
        form = MetricaForm(request.POST, instance=metrica)
        if form.is_valid():
            metrica = form.save(commit=False)
            metrica.objetivo = objetivo
            metrica.save()
            messages.success(request, "Métrica guardada correctamente.")
            return redirect('matches')
        else:
            messages.error(request, "Error al guardar la métrica. Revisa los campos.")
    else:
        form = MetricaForm(instance=metrica)

    return render(request, 'gestionar_metrica.html', {
        'form': form,
        'objetivo': objetivo,
        'metrica': metrica,
        'active_page': 'matches',
        'title': 'Gestionar Métrica',
    })

@login_required
def gestionar_evaluacion(request, metrica_id, evaluacion_id=None):
    metrica = get_object_or_404(Metrica.objects.select_related('objetivo__match'), id=metrica_id, isActive=True)
    evaluacion = None

    if evaluacion_id:
        evaluacion = get_object_or_404(Evaluacion, id=evaluacion_id, metrica=metrica, isActive=True)

    if request.method == 'POST':
        form = EvaluacionForm(request.POST, instance=evaluacion)
        if form.is_valid():
            evaluacion = form.save(commit=False)
            evaluacion.metrica = metrica
            evaluacion.save()
            messages.success(request, "Evaluación guardada correctamente.")
            return redirect('matches')
        else:
            messages.error(request, "Error al guardar la evaluación. Revisa los campos.")
    else:
        form = EvaluacionForm(instance=evaluacion)

    return render(request, 'gestionar_evaluacion.html', {
        'form': form,
        'metrica': metrica,
        'evaluacion': evaluacion,
        'active_page': 'matches',
        'title': 'Gestionar Evaluación',
    })


@login_required
def gestionar_actividad(request, metrica_id, actividad_id=None):
    metrica = get_object_or_404(Metrica.objects.select_related('objetivo__match'), id=metrica_id, isActive=True)
    actividad = None

    if actividad_id:
        actividad = get_object_or_404(Actividad, id=actividad_id, metrica=metrica, isActive=True)

    if request.method == 'POST':
        form = ActividadForm(request.POST, instance=actividad)
        if form.is_valid():
            actividad = form.save(commit=False)
            actividad.metrica = metrica
            actividad.save()
            messages.success(request, "Actividad guardada correctamente.")
            return redirect('matches')
        else:
            messages.error(request, "Error al guardar la actividad. Revisa los campos.")
    else:
        form = ActividadForm(instance=actividad)

    return render(request, 'gestionar_actividad.html', {
        'form': form,
        'metrica': metrica,
        'actividad': actividad,
        'active_page': 'matches',
         'title': 'Gestionar Actividad',
    })


@login_required
def postulacionesDesafios(request):
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')

    postulaciones = PostulacionDesafio.objects.select_related('empresa').filter(isActive=True)

    if query:
        postulaciones = postulaciones.filter(
            Q(empresa__nombre__icontains=query) |
            Q(id__icontains=query) |
            Q(desafioFrase__icontains=query)
        )

    if estado:
        postulaciones = postulaciones.filter(estado=estado)

    postulaciones = postulaciones.order_by('-fecha')

    return render(request, 'postulaciones_desafio.html', {
        'active_page': 'postulacionesDesafios',
        'title': 'Postulaciones',
        'postulaciones': postulaciones,
        'estado_seleccionado': estado,
        'query': query,
    })

@login_required
def verPostulacionDesafio(request, id):
    postulacion = get_object_or_404(PostulacionDesafio.objects.select_related('empresa', 'contacto'), id=id, isActive=True)
    return render(request, 'ver_postulacion_desafio.html', {
        'active_page': 'postulacionesDesafios',
        'title': 'Ver Postulación',
        'postulacion': postulacion
    })

@login_required
@user_passes_test(es_admin)
def depurar_desafio(request,id):
    postulacion = get_object_or_404(PostulacionDesafio, id=id, isActive=True)
    desafio = Desafio.objects.filter(postulacion=postulacion, isActive=True).first()
    existing_documents=[]

    if not desafio:
        desafio = Desafio(
            postulacion=postulacion,
            empresa=postulacion.empresa,
            contacto=postulacion.contacto,
            ejecutivo=request.user,
            isActive=True
        )
    else:
        existing_documents = Documento.objects.filter(
            object_id=desafio.id,
            content_type=ContentType.objects.get_for_model(Desafio)
        )

    if request.method == 'POST':
        form = DesafioForm(request.POST, request.FILES, instance=desafio)

        documentos_a_eliminar_ids = request.POST.getlist('eliminar_documentos')

        if form.is_valid():
            desafio_instance = form.save(commit=False)

            desafio_instance.postulacion = postulacion
            desafio_instance.empresa = postulacion.empresa
            desafio_instance.contacto = postulacion.contacto
            desafio_instance.ejecutivo = request.user
            desafio_instance.isActive = True

            desafio_instance.save()

            Documento.objects.filter(
                id__in=documentos_a_eliminar_ids,
                object_id=desafio_instance.id,
                content_type=ContentType.objects.get_for_model(Desafio)
            ).delete()
            messages.info(request, f"{len(documentos_a_eliminar_ids)} documentos eliminados.")

            archivos = request.FILES.getlist('documentos')
            if archivos:
                content_type = ContentType.objects.get_for_model(Desafio)
                document_count = 0
                for archivo in archivos:
                    Documento.objects.create(
                        archivo=archivo,
                        nombre=archivo.name,
                        content_type=content_type,
                        object_id=desafio_instance.id
                    )
                    document_count += 1
                messages.success(request, f"{document_count} documentos subidos.")

            if postulacion.estado != 'Depurado':
                 postulacion.estado = 'Depurado'
                 postulacion.save()
                 messages.success(request, "Postulación marcada como 'Depurado'.")

            messages.success(request, "Desafío depurado y guardado correctamente.")
            return redirect('desafios')
        else:
             messages.error(request, "Error al depurar el desafío. Revisa los campos.")

    else:
        form = DesafioForm(instance=desafio)

    documents_for_template = Documento.objects.filter(
        content_type=ContentType.objects.get_for_model(Desafio),
        object_id=desafio.id if desafio else None
    )


    return render(request, 'depurar_desafio.html', {
        'active_page': 'postulacionesDesafios',
        'title': 'Depurar Desafío',
        'form': form,
        'postulacion': postulacion,
        'existing_documents': documents_for_template
    })


@login_required
@user_passes_test(es_admin)
def eliminarPostulacionDesafio(request, id):
    postulacion = get_object_or_404(PostulacionDesafio, id=id, isActive=True)
    if request.method == 'POST':
        postulacion.isActive = False
        postulacion.save()
        messages.success(request, f"Postulación Desafío ID {id} eliminada (marcada como inactiva) correctamente.")
    return redirect('postulaciones_desafios')

@login_required
def cambiar_estado_postulacion(request, id):
    postulacion = get_object_or_404(PostulacionDesafio, id=id, isActive=True)
    if request.method == 'POST':
        if postulacion.estado == "Por Depurar" or postulacion.estado == "Depurado" or postulacion.estado == "Por depurar":
            postulacion.estado = "Abandonado"
            messages.success(request, f"El estado de la postulación se ha actualizado a '{postulacion.estado}'.")
        elif postulacion.estado == "Abandonado":
            postulacion.estado = "Por Depurar"
            messages.success(request, f"El estado de la postulación se ha actualizado a '{postulacion.estado}'.")
        else:
            messages.warning(request, f"No se puede cambiar el estado '{postulacion.estado}'.")

        postulacion.save()
    return redirect('postulaciones_desafios')



@login_required
def desafios(request):
    query = request.GET.get('q', '')
    desafios_list = Desafio.objects.select_related('empresa', 'contacto').filter(isActive=True)

    if query:
        desafios_list = desafios_list.filter(
            Q(nombreDesafio__icontains=query) |
            Q(id__icontains=query) |
            Q(empresa__nombre__icontains=query)
        ).distinct()

    desafios_list = desafios_list.order_by('-id')


    return render(request, 'desafios_depurados.html', {
        'active_page': 'desafios',
        'title': 'Desafíos Depurados',
        'desafios': desafios_list,
        'query': query,
    })

@login_required
def verDesafio(request, id):
    desafio = get_object_or_404(Desafio.objects.select_related('empresa', 'contacto', 'postulacion'), id=id, isActive=True)
    documentos = Documento.objects.filter(content_type=ContentType.objects.get_for_model(Desafio), object_id=id)
    return render(request, 'ver_desafio.html', {
        'active_page': 'desafios',
        'title': 'Ver Desafío',
        'desafio': desafio,
        'documentos': documentos
    })

@login_required
@user_passes_test(es_admin)
def eliminarDesafio(request, id):
    desafio = get_object_or_404(Desafio, id=id, isActive=True)
    if request.method == 'POST':
        desafio.isActive = False
        desafio.save()
        messages.success(request, f"Desafío ID {id} eliminado (marcado como inactivo) correctamente.")
    return redirect('desafios')

@login_required
@user_passes_test(es_admin)
def actualizar_check_masivo(request):
    if request.method == 'POST':
        desafios_ids_in_form = [int(key.split('_')[1]) for key in request.POST if key.startswith('isPrincipal_')]
        desafios_to_update = Desafio.objects.filter(id__in=desafios_ids_in_form, isActive=True)

        for desafio in desafios_to_update:
            isPrincipal_checked = f'isPrincipal_{desafio.id}' in request.POST
            show_checked = f'show_{desafio.id}' in request.POST

            if desafio.isPrincipal != isPrincipal_checked:
                desafio.isPrincipal = isPrincipal_checked
                desafio.save()
            if desafio.isPrincipal and not desafio.show:
                 desafio.show = True
                 desafio.save()
            elif not desafio.isPrincipal and desafio.show != show_checked:
                 desafio.show = show_checked
                 desafio.save()


        messages.success(request, "Configuración masiva de desafíos actualizada correctamente.")

    return redirect('desafios')


@login_required
def empresas(request):
    empresas_list = Empresa.objects.filter(isActive=True).order_by('nombre')
    return render(request, 'empresas.html', {
        'active_page': 'empresas',
        'title': 'Empresas',
        'empresas': empresas_list
    })

@login_required
def verEmpresa(request, id):
    empresa = get_object_or_404(Empresa.objects, id=id, isActive=True)
    contactos = usuario_base.objects.filter(empresa=empresa, es_activo=True)

    return render(request, 'ver_empresa.html', {
        'active_page': 'empresas',
        'title': 'Ver Empresa',
        'empresa': empresa,
        'contactos': contactos
    })


@login_required
def postulacionesIniciativas(request):
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')

    postulaciones = PostulacionIniciativa.objects.select_related('empresa', 'desafio').filter(isActive=True)

    if query:
        postulaciones = postulaciones.filter(
            Q(empresa__nombre__icontains=query) |
            Q(id__icontains=query) |
            Q(titulo__icontains=query) |
            Q(desafio__nombreDesafio__icontains=query)
        )

    if estado:
        postulaciones = postulaciones.filter(estado=estado)

    postulaciones = postulaciones.order_by('-fecha')

    return render(request, 'postulaciones_iniciativa.html', {
        'active_page': 'postulacionesIniciativas',
        'title': 'Postulaciones Iniciativas',
        'postulaciones': postulaciones,
        'estado_seleccionado': estado,
        'query': query,
    })

@login_required
def verPostulacionIniciativa(request, id):
    postulacion = get_object_or_404(PostulacionIniciativa.objects.select_related('empresa', 'contacto', 'desafio'), id=id, isActive=True)
    return render(request, 'ver_postulacion_iniciativa.html', {
        'active_page': 'postulacionesIniciativas',
        'title': 'Ver Postulación Iniciativa',
        'postulacion': postulacion
    })

@login_required
@user_passes_test(es_admin)
def eliminarPostulacionIniciativa(request, id):
    postulacion = get_object_or_404(PostulacionIniciativa, id=id, isActive=True)
    if request.method == 'POST':
        postulacion.isActive = False
        postulacion.save()
        messages.success(request, f"Postulación Iniciativa ID {id} eliminada (marcada como inactiva) correctamente.")
    return redirect('postulaciones_iniciativas')

@login_required
def cambiar_estado_postulacion_i(request, id):
    postulacion = get_object_or_404(PostulacionIniciativa, id=id, isActive=True)
    if request.method == 'POST':
        estado_norm = postulacion.estado.lower().replace(" ", "")
        if estado_norm in ["pordepurar", "depurado"]:
            postulacion.estado = "Abandonado"
            messages.success(request, f"El estado de la postulación se ha actualizado a '{postulacion.estado}'.")
        elif estado_norm == "abandonado":
            postulacion.estado = "Por Depurar"
            messages.success(request, f"El estado de la postulación se ha actualizado a '{postulacion.estado}'.")
        else:
            messages.warning(request, f"No se puede cambiar el estado '{postulacion.estado}'.")

        postulacion.save()
    return redirect('postulaciones_iniciativas')

@login_required
def depurar_iniciativa(request,id):
    postulacion = get_object_or_404(PostulacionIniciativa.objects.select_related('desafio'), id=id, isActive=True)
    iniciativa = Iniciativa.objects.filter(postulacion=postulacion, isActive=True).first()
    existing_documents=[]

    if not iniciativa:
        iniciativa = Iniciativa(
            postulacion=postulacion,
            empresa=postulacion.empresa,
            contacto=postulacion.contacto,
            ejecutivo=request.user,
            desafio=postulacion.desafio,
            isActive=True
        )
    else:
        existing_documents = Documento.objects.filter(
            object_id=iniciativa.id,
            content_type=ContentType.objects.get_for_model(Iniciativa)
        )

    if request.method == 'POST':
        action = request.POST.get('action')
        form = IniciativaForm(request.POST, request.FILES, instance=iniciativa)

        documentos_a_eliminar_ids = request.POST.getlist('eliminar_documentos')

        if form.is_valid():
            iniciativa_instance = form.save(commit=False)

            iniciativa_instance.postulacion = postulacion
            iniciativa_instance.empresa = postulacion.empresa
            iniciativa_instance.contacto = postulacion.contacto
            iniciativa_instance.ejecutivo = request.user
            iniciativa_instance.desafio = postulacion.desafio
            iniciativa_instance.isActive = True

            iniciativa_instance.save()

            Documento.objects.filter(
                id__in=documentos_a_eliminar_ids,
                object_id=iniciativa_instance.id,
                content_type=ContentType.objects.get_for_model(Iniciativa)
            ).delete()
            messages.info(request, f"{len(documentos_a_eliminar_ids)} documentos eliminados.")

            archivos = request.FILES.getlist('documentos')
            if archivos:
                content_type = ContentType.objects.get_for_model(Iniciativa)
                document_count = 0
                for archivo in archivos:
                    Documento.objects.create(
                        archivo=archivo,
                        nombre=archivo.name,
                        content_type=content_type,
                        object_id=iniciativa_instance.id
                    )
                    document_count += 1
                messages.success(request, f"{document_count} documentos subidos.")

            if postulacion.estado != 'Depurado':
                 postulacion.estado = 'Depurado'
                 postulacion.save()
                 messages.success(request, "Postulación marcada como 'Depurado'.")


            messages.success(request, "Iniciativa depurada y guardada correctamente.")

            if action == 'save_and_redirect':
                if iniciativa_instance.desafio:
                     messages.info(request, "Redirigiendo para crear Match...")
                     return redirect(reverse('crear_match', args=[iniciativa_instance.desafio.id, iniciativa_instance.id]))
                else:
                     messages.warning(request, "Iniciativa guardada, pero no tiene un desafío asociado. No se puede crear el match automáticamente.")
                     return redirect('iniciativas')

            return redirect('iniciativas')

        else:
            messages.error(request, "Error al depurar la iniciativa. Revisa los campos.")


    else:
        form = IniciativaForm(instance=iniciativa)

    documents_for_template = Documento.objects.filter(
        content_type=ContentType.objects.get_for_model(Iniciativa),
        object_id=iniciativa.id if iniciativa else None
    )

    return render(request, 'depurar_iniciativa.html', {
        'active_page': 'postulacionesIniciativas',
        'title': 'Depurar Iniciativa',
        'form': form,
        'postulacion': postulacion,
        'existing_documents': documents_for_template
    })


@login_required
def iniciativas(request):
    query = request.GET.get('q', '')
    iniciativas_list = Iniciativa.objects.select_related('empresa', 'contacto', 'desafio').filter(isActive=True)

    if query:
        iniciativas_list = iniciativas_list.filter(
            Q(titulo__icontains=query) |
            Q(id__icontains=query) |
            Q(empresa__nombre__icontains=query) |
            Q(desafio__nombreDesafio__icontains=query)
        ).distinct()

    iniciativas_list = iniciativas_list.order_by('-id')

    return render(request, 'iniciativas_depuradas.html', {
        'active_page': 'iniciativas',
        'title': 'Iniciativas Depuradas',
        'iniciativas': iniciativas_list,
        'query': query,
    })


@login_required
def verIniciativa(request, id):
    iniciativa = get_object_or_404(Iniciativa.objects.select_related('empresa', 'contacto', 'postulacion', 'desafio'), id=id, isActive=True)
    documentos = Documento.objects.filter(content_type=ContentType.objects.get_for_model(Iniciativa), object_id=id)
    return render(request, 'ver_iniciativa.html', {
        'active_page': 'iniciativas',
        'title': 'Ver Iniciativa',
        'iniciativa': iniciativa,
        'documentos': documentos
    })


@login_required
@user_passes_test(es_admin)
def eliminarIniciativa(request, id):
    iniciativa = get_object_or_404(Iniciativa, id=id, isActive=True)
    if request.method == 'POST':
        iniciativa.isActive = False
        iniciativa.save()
        messages.success(request, f"Iniciativa ID {id} eliminada (marcada como inactiva) correctamente.")
    return redirect('iniciativas')


@login_required
def crear_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        action = request.POST.get('action')

        if form.is_valid():
            post = form.save(commit=False)
            if not post.autor:
                 post.autor = request.user.get_full_name() or request.user.username

            if action == 'publicar':
                post.publico = True
                post.save()
                messages.success(request, f"Post '{post.titulo}' publicado correctamente.")
                return redirect(reverse('blog:post_detalle', kwargs={'slug': post.slug}))
            else:
                post.publico = False
                post.save()
                messages.success(request, f"Post '{post.titulo}' guardado como borrador correctamente.")
                return redirect('posts')
        else:
            messages.error(request, "Error al crear el post. Revisa los campos.")
            print(form.errors)

    else:
        form = PostForm()
        if 'autor' in form.fields:
             form.initial['autor'] = request.user.get_full_name() or request.user.username

    return render(request, 'crear_post.html', {
        'active_page': 'crear_post',
        'title': 'Crear Post',
        'form': form
    })

@login_required
def posts(request):
    posts_list = Post.objects.filter(is_active=True).order_by('-fecha')
    return render(request, 'posts.html', {
        'active_page': 'posts',
        'title': 'Posts',
        'posts': posts_list
    })

@login_required
def editar_post(request, id):
    post = get_object_or_404(Post, id=id, is_active=True)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        action = request.POST.get('action')

        if form.is_valid():
            post_instance = form.save(commit=False)

            if action == 'publicar':
                post_instance.publico = True
                messages.success(request, f"Post '{post_instance.titulo}' publicado correctamente.")
            else:
                post_instance.publico = False
                messages.success(request, f"Post '{post_instance.titulo}' guardado como borrador correctamente.")

            post_instance.save()

            if post_instance.publico:
                return redirect(reverse('blog:post_detalle', kwargs={'slug': post_instance.slug}))
            else:
                return redirect('posts')

        else:
            messages.error(request, "Error al editar el post. Revisa los campos.")
            print(form.errors)

    else:
        form = PostForm(instance=post)

    return render(request, 'editar_post.html', {
        'active_page': 'posts',
        'title': 'Editar Post',
        'form': form,
        'post': post
    })

@login_required
@user_passes_test(es_admin)
def eliminarPost(request, id):
    post = get_object_or_404(Post, id=id, is_active=True)
    if request.method == 'POST':
        post.is_active = False
        post.save()
        messages.success(request, f"Post '{post.titulo}' eliminado (marcado como inactivo) correctamente.")
    return redirect('posts')

@login_required
@user_passes_test(es_admin)
def actualizar_check_masivo_post(request):
    if request.method == 'POST':
        post_ids_in_form = [int(key.split('_')[1]) for key in request.POST if key.startswith('publico_')]
        posts_to_update = Post.objects.filter(id__in=post_ids_in_form, is_active=True)

        for post in posts_to_update:
            is_public_checked = f'publico_{post.id}' in request.POST
            if post.publico != is_public_checked:
                post.publico = is_public_checked
                post.save()

        messages.success(request, "Configuración masiva de posts actualizada correctamente.")
    return redirect('posts')


@login_required
def post_preview(request,slug):
    post = get_object_or_404(Post.objects, slug=slug)

    return render(request, 'post_prev.html', {'post': post})

@login_required
def solicitudes_contacto(request):
    solicitudes_list = solicitudContacto.objects.filter(isActive=True).order_by('-fecha')
    return render(request, 'solicitudes_contacto.html', {
        'active_page': 'solicitudes_contacto',
        'title': 'Solicitudes de Contacto',
        'solicitudes': solicitudes_list
    })

@login_required
def verSolicitud(request, id):
    solicitud = get_object_or_404(solicitudContacto.objects, id=id, isActive=True)
    return render(request, 'ver_solicitud.html', {
        'active_page': 'solicitudes_contacto',
        'title': 'Ver Solicitud',
        'solicitud': solicitud
    })

@login_required
@user_passes_test(es_admin)
def eliminarSolicitud(request, id):
    solicitud = get_object_or_404(solicitudContacto, id=id, isActive=True)
    if request.method == 'POST':
        solicitud.isActive = False
        solicitud.save()
        messages.success(request, f"Solicitud de contacto ID {id} eliminada (marcada como inactiva) correctamente.")
    return redirect('solicitudes_contacto')


@login_required
@user_passes_test(es_admin)
def gestionar_usuarios(request):
    ejecutivos_base = usuario_base.objects.filter(rol="ejecutivo", es_activo=True)

    return render(request, 'gestionar_usuarios.html', {
        'active_page': 'usuarios',
        'title': 'Gestión de Usuarios Ejecutivos',
        'usuarios': ejecutivos_base
    })

@login_required
@user_passes_test(es_admin)
def crear_ejecutivo(request):
    if request.method == 'POST':
        form = EjecutivoCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            email = form.cleaned_data.get('email')
            usuario_base_obj, created = usuario_base.objects.get_or_create(
                 correo=email,
                 defaults={
                    'nombre': form.cleaned_data.get('nombre_completo'),
                    'contraseña': email,
                    'rol': "ejecutivo",
                    'es_activo': True,
                    'cargo': form.cleaned_data.get('cargo'),
                    'telefono': form.cleaned_data.get('telefono') or "",
                    'empresa': None
                 }
            )
            if not created:
                 usuario_base_obj.nombre = form.cleaned_data.get('nombre_completo')
                 usuario_base_obj.rol = "ejecutivo"
                 usuario_base_obj.es_activo = True
                 usuario_base_obj.cargo = form.cleaned_data.get('cargo')
                 usuario_base_obj.telefono = form.cleaned_data.get('telefono') or ""
                 usuario_base_obj.save()

            messages.success(request, f'Usuario ejecutivo "{user.username}" creado/actualizado correctamente.')
            return redirect('gestionar_usuarios')
        else:
            messages.error(request, "Error al crear el usuario ejecutivo. Revisa los campos.")
            print(form.errors)
    else:
        form = EjecutivoCreationForm()

    return render(request, 'crear_ejecutivo.html', {
        'active_page': 'usuarios',
        'title': 'Crear Usuario Ejecutivo',
        'form': form
    })

@login_required
@user_passes_test(es_admin)
def desactivar_ejecutivo(request, id):
    usuario_base_obj = get_object_or_404(usuario_base, id=id, rol="ejecutivo", es_activo=True)

    if request.method == 'POST':
        usuario_base_obj.es_activo = False
        usuario_base_obj.save()

        try:
            user = User.objects.get(email=usuario_base_obj.correo, is_active=True)
            user.is_active = False
            user.save()
        except User.DoesNotExist:
            pass

        messages.success(request, f'Usuario ejecutivo "{usuario_base_obj.nombre}" desactivado correctamente.')
        return redirect('gestionar_usuarios')

    return render(request, 'confirmar_desactivar_ejecutivo.html', {
        'usuario': usuario_base_obj,
        'active_page': 'usuarios',
        'title': 'Confirmar Desactivación',
    })


@login_required
@user_passes_test(es_admin)
def configuracion_admin_view(request):
    config, created = AdminConfig.objects.get_or_create(pk=1)

    if request.method == 'POST':
        form = AdminConfigForm(request.POST, request.FILES, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Configuración guardada correctamente.')
            return redirect('configuracion_admin')
        else:
            messages.error(request, "Error al guardar la configuración. Revisa los campos.")
            print(form.errors)

    else:
        form = AdminConfigForm(instance=config)

    current_logo_url = config.logo.url if config and config.logo else None

    sidebar_themes_data = [{'name': choice[0], 'label': choice[1], 'css_class': choice[0]} for choice in AdminConfig.SIDEBAR_THEME_CHOICES]
    background_themes_data = [{'name': choice[0], 'label': choice[1], 'css_class': choice[0]} for choice in AdminConfig.BACKGROUND_THEME_CHOICES]


    context = {
        'form': form,
        'active_page': 'configuracion_admin',
        'title': 'Configuración del Sitio',
        'current_logo_url': current_logo_url,
        'sidebar_themes_data': sidebar_themes_data,
        'background_themes_data': background_themes_data,
    }
    return render(request, 'configuracion.html', context)