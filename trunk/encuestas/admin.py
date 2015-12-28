from django.contrib import admin
from lugar.models import Comunidad
from encuestas.models import Recolector, Encuesta, Finca, Educacion, Boscosa, Saf, ProducComerPrecio, Ingreso, SeguridadAlimentaria, Credito,TomasDeciciones, ConoJoRassMata, Fotos
from django.contrib.contenttypes import generic


class FincaInline(generic.GenericStackedInline):
	model = Finca
	extra = 1
	max_num = 1
class EducacionInline(generic.GenericTabularInline):
	model = Educacion
	extra = 8
	max_num = 8
class BoscosaInline(generic.GenericStackedInline):
        model = Boscosa
        extra = 1
	max_num = 1
class SafInline(generic.GenericTabularInline):
        model = Saf
        extra = 14
	max_num = 14
class ProducComerPrecioInline(generic.GenericTabularInline):
        model = ProducComerPrecio
        extra = 11
	max_num = 11
class IngresoInline(generic.GenericTabularInline):
        model = Ingreso
        extra = 32
	max_num = 32
class SeguridadAlimentariaInline(generic.GenericTabularInline):
        model = SeguridadAlimentaria
        extra = 37
	max_num = 37
class CreditoInline(generic.GenericTabularInline):
        model = Credito
        extra = 6
	max_num = 6
class TomasDecicionesInline(generic.GenericTabularInline):
        model = TomasDeciciones
        extra = 5
	max_num = 5
class ConoJoRassMataInline(generic.GenericTabularInline):
        model = ConoJoRassMata
        extra = 6
	max_num = 6
class FotosInline(generic.GenericTabularInline):
	model = Fotos
	extra = 5
	max_num = 5
class EncuestaAdmin(admin.ModelAdmin):
	save_on_top = True
	actions_on_top = True
	
	inlines = [FincaInline,EducacionInline,BoscosaInline,SafInline,ProducComerPrecioInline,IngresoInline,SeguridadAlimentariaInline,CreditoInline,TomasDecicionesInline,ConoJoRassMataInline,FotosInline,]

	list_display = ['productores','fincas','comunidades','municipios','departamentos','propietarios']
	list_filter = ['fecha', 'ano']
	date_hierarchy = 'fecha'
	search_fields = ['finca__nombre_productor','finca__comunidad__nombre','finca__comunidad__municipio__nombre','finca__comunidad__municipio__departamento__nombre','finca__propietario']


admin.site.register(Encuesta, EncuestaAdmin)
admin.site.register(Recolector)
