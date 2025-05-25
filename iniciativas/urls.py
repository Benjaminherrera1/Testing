from django.urls import path
from django.shortcuts import render
from .views import (
    EmpresaStepView,
    ContactoStepView,
    IniciativaParteOneStepView,
    IniciativaParteTwoStepView
)

urlpatterns = [
    path('empresa_i/<int:id>', EmpresaStepView.as_view(), name='empresa_step_i'),
    path('contacto_i', ContactoStepView.as_view(), name='contacto_step_i'),
    path('iniciativa_i', IniciativaParteOneStepView.as_view(), name='iniciativa_parte1_step_i'),
    path('iniciativa_parte2_i', IniciativaParteTwoStepView.as_view(), name='iniciativa_parte2_step_i'),
    path('complete_i', lambda request: render(request, 'form_complete_i.html', {'tipo_postulacion': 'Iniciativa'}), name='form_complete_i'),
]
