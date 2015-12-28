from django.contrib import admin
from lugar.models import Departamento, Municipio, Microcuenca, Comunidad

class ComunidadAdmin(admin.ModelAdmin):
	list_display = ['nombre', 'municipio']
class DepartamentoAdmin(admin.ModelAdmin):
	pass
class MicrocuencaAdmin(admin.ModelAdmin):
	pass
class MunicipioAdmin(admin.ModelAdmin):
	list_display = ['nombre', 'departamento']


admin.site.register(Departamento,DepartamentoAdmin )
admin.site.register(Municipio, MunicipioAdmin)
admin.site.register(Microcuenca,MicrocuencaAdmin)
admin.site.register(Comunidad, ComunidadAdmin) 
