 # -*- coding: UTF-8 -*-

from django import forms
from django.forms import ModelForm
from encuestas.models import *
from lugar.models import *
from widgets import JQueryAutoComplete


ANOS_CHOICES = ((2009,'2009'),(2010,'2010'),(2011,'2011'))

COBERTURA_CHOICES = (('area total','Area Total'),('bosque primario','Bosque Primario'),('bosque secundario','Bosque Secundario'),('bosque galeria','Bosque Galeria'),('humedales','Humedales'),('tacotal','Tacotal'),('cultivos perennes','Cultivos Perennes'),('cultivos semiperennes','Cultivos Semiperennes'),('cultivos anuales','Cultivos Anuales'),('huerto mixto','Huerto Mixto'),('potrero abierto','Potrero Abierto'),('potrero arboles','Potrero Arboles'),('cerca viva','Cerca Viva'),('cerca muerta','Cerca Muerta'),('plantaciones forestales','Plantaciones Forestales'),('parcela energetica','Parcela Energetica'))

DUENO_CHOICES=(('','-----'),('hombre','Hombre'),('mujer','Mujer'),('ambos','Ambos'),('parientes','Parientes'))

def get_anios():
    years = []
    for en in Encuesta.objects.order_by('-ano').values_list('ano', flat=True):
        years.append((en, en))
    return list(set(years))

class EncuestaForm(forms.ModelForm):
	ano = forms.ChoiceField(choices=get_anios(), required=False)
	class Meta:
		model = Encuesta
		fields = ('ano',)

class BoscosaForm(forms.Form):
	coberturas = forms.ChoiceField(choices=COBERTURA_CHOICES, required=False)
	class Meta:
		model = Boscosa
		
class LugarForm(forms.ModelForm):
	nombre = forms.ModelChoiceField(queryset=Comunidad.objects.all(), required=False)
	class Meta:
		model = Comunidad
		fields = ('nombre',)
		
# Formulario de entrada.
class FincaForm(forms.Form):
    fecha = forms.ChoiceField(choices=get_anios(), required=False)
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False, empty_label="Todos los Departamento")
    municipio = forms.CharField(widget = forms.Select, required=False)
    comunidad = forms.CharField(widget = forms.Select, required=False)
    propietario = forms.ChoiceField(choices=DUENO_CHOICES, required=False)
    repetido = forms.BooleanField(required=False)
    productor = forms.CharField(widget=JQueryAutoComplete('/ajax/productor'), required=False)
    tipo_busqueda = forms.CharField(widget = forms.HiddenInput, required = False, initial='general')
