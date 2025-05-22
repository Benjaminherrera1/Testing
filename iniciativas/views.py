from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import (
    EmpresaForm,
    ContactoEmpresaForm,
    PostulacionIniciativaParteOneForm,
    PostulacionIniciativaParteTwoForm
)
from .models import PostulacionIniciativa
from administracion.models import Empresa, usuario_base
from desafios.models import Desafio
from django.db import transaction

class EmpresaStepView(View):
    def get(self, request, id):
        request.session['desafio_id'] = id
        initial_data = request.session.get('empresa_data', {})
        form = EmpresaForm(initial=initial_data)
        return render(request, 'form_empresa_i.html', {'form': form})
    
    def post(self, request, id):
        form = EmpresaForm(request.POST)
        if form.is_valid():
            request.session['empresa_data'] = form.cleaned_data
            return redirect('contacto_step_i')
        return render(request, 'form_empresa_i.html', {'form': form})

class ContactoStepView(View):
    def get(self, request):
        initial_data = request.session.get('contacto_data', {})
        form = ContactoEmpresaForm(initial=initial_data)
        desafio_id = request.session.get('desafio_id')
        return render(request, 'form_contacto_i.html', {
            'form': form,
            'id_objeto': desafio_id
        })

    def post(self, request):
        form = ContactoEmpresaForm(request.POST)
        if form.is_valid():
            request.session['contacto_data'] = form.cleaned_data
            return redirect('iniciativa_parte1_step_i')
        return render(request, 'form_contacto_i.html', {'form': form})

class IniciativaParteOneStepView(View):
    def get(self, request):
        initial_data = request.session.get('iniciativa_parte1_data', {})
        form = PostulacionIniciativaParteOneForm(initial=initial_data)
        return render(request, 'form_iniciativa_parte1.html', {'form': form})
    
    def post(self, request):
        post_data = request.POST.copy()
        post_data['latam'] = request.POST.get('latam', '')
        form = PostulacionIniciativaParteOneForm(post_data)
        if form.is_valid():
            request.session['iniciativa_parte1_data'] = form.cleaned_data
            return redirect('iniciativa_parte2_step_i')
        return render(request, 'form_iniciativa_parte1.html', {'form': form})

class IniciativaParteTwoStepView(View):
    def get(self, request):
        initial_data = request.session.get('iniciativa_parte2_data', {})
        form = PostulacionIniciativaParteTwoForm(initial=initial_data)
        return render(request, 'form_iniciativa_parte2.html', {'form': form})
    
    def post(self, request):
        form = PostulacionIniciativaParteTwoForm(request.POST)
        if form.is_valid():
            request.session['iniciativa_parte2_data'] = form.cleaned_data
            iniciativa_parte1_data = request.session.get('iniciativa_parte1_data', {})
            iniciativa_data = {**iniciativa_parte1_data, **form.cleaned_data}
            try:
                with transaction.atomic():
                    empresa_data = request.session.get('empresa_data')
                    empresa = Empresa.objects.create(**empresa_data)
                    
                    contacto_data = request.session.get('contacto_data')
                    contacto = usuario_base.objects.create(empresa=empresa, **contacto_data)
                    
                    desafio_id = request.session.get('desafio_id')
                    desafio = None if desafio_id == 0 else get_object_or_404(Desafio, id=desafio_id)

                    PostulacionIniciativa.objects.create(
                        empresa=empresa,
                        contacto=contacto,
                        desafio=desafio,
                        titulo=iniciativa_data['titulo'],
                        descripcion=iniciativa_data['descripcion'],
                        latam=iniciativa_data['latam'],
                        video=iniciativa_data['video'],
                        diferenciacion=iniciativa_data['diferenciacion'],
                        traccion=iniciativa_data['traccion'],
                        piloto=iniciativa_data['piloto'],
                        pregunta=iniciativa_data['pregunta'],
                        origen=iniciativa_data['origen']
                    )

                    # Limpiar datos de sesión
                    for key in [
                        'empresa_data',
                        'contacto_data',
                        'iniciativa_parte1_data',
                        'iniciativa_parte2_data'
                    ]:
                        request.session.pop(key, None)

                    return redirect('form_complete_i')

            except Exception as e:
                print("Error al guardar:", e)
                return render(request, 'form_error_i.html', {
                    'template_base': 'postulacion_iniciativa.html',
                    'empresa_step_url_name': 'empresa_step_i'
                })

        return render(request, 'form_iniciativa_parte2.html', {'form': form})
