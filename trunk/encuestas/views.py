 # -*- coding: UTF-8 -*-
from pygooglechart import PieChart3D, StackedVerticalBarChart, GroupedVerticalBarChart
from django.shortcuts import render_to_response, get_list_or_404
from django.views.generic.simple import direct_to_template
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.cache import cache_page
from forms import *
from encuestas.models import *
from lugar.models import *
from django.db.models import Sum, Count, Avg
from django.utils import simplejson
from decimal import Decimal
from decorators import session_required
from django.template.loader import get_template
from django.template import Context
import ho.pisa as pisa
import cStringIO as StringIO
import cgi
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib.auth import logout

def logout_page(request):
  logout(request)
  return HttpResponseRedirect('/')

def ayuda(request):
    return render_to_response("encuestas/ayuda.html")

def filtros_comunes(request):
    params = {}
    if 'fecha' in request.session:
        params['ano'] = request.session['fecha']
    #if 'finca' in  request.session:
    #    params['finca'] = request.session['finca']

    if request.session['comunidad']:
        params['finca__comunidad'] = request.session['comunidad']
    if request.session['municipio']:
        params['finca__comunidad__municipio'] = request.session['municipio']
    if request.session['departamento']:
        params['finca__comunidad__municipio__departamento'] = request.session['departamento']
               
    if request.session['propietario']:
        params['finca__propietario'] = request.session['propietario']
    
    #print params
    unvalid_keys = []
    for key in params:
        if not params[key]:
            unvalid_keys.append(key)
    
    for key in unvalid_keys:
        del params[key]
    
    
    if request.session['repetido'] == True:
        return Encuesta.objects.filter(**params).filter(finca__repetido=True)
    else:
        return Encuesta.objects.filter(**params)

def index(request):
    if request.method=='POST':
        mensaje = None
        form = FincaForm(request.POST)
        if form.is_valid():
            #TODO: reparar esto desde el forms.py
            request.session['fecha'] = form.cleaned_data['fecha'] 
            request.session['departamento'] = form.cleaned_data['departamento']
            
            if form.cleaned_data['tipo_busqueda']=='general':
                try:
                    municipio = Municipio.objects.get(id=form.cleaned_data['municipio']) 
                except:
                    municipio = None
                try:
                    comunidad = Comunidad.objects.get(id=form.cleaned_data['comunidad']) 
                except:
                    comunidad = None
                request.session['municipio'] = municipio 
                request.session['comunidad'] = comunidad
                request.session['finca'] = None
                if form.cleaned_data['propietario'] == 'nada':
                    request.session['propietario'] = None
                else:
                    request.session['propietario'] = form.cleaned_data['propietario'] 
                #le decimos que el usuario ha seleccionado los filtros del inicio
                mensaje = "Ahora puede seleccionar los datos con los botones de la derecha"
                request.session['repetido'] = form.cleaned_data['repetido'] 
                request.session['activo'] = True 
            elif form.cleaned_data['tipo_busqueda']=='especifica':
                try:
                    finca = Finca.objects.filter(nombre_productor__iexact = form.cleaned_data['productor'])[0]
                    request.session['activo'] = True 
                    mensaje = "Ahora puede seleccionar los datos con los botones de la derecha"
                except:
                    finca = None
                    request.session['activo'] = False 
                    mensaje = "Error, seleccione bien los valores para el productor"
                request.session['finca'] = finca
    else:
        form = FincaForm()
        mensaje = "" 
    dict = {'form': form, 'mensaje': mensaje,'user': request.user}
    return direct_to_template(request, 'encuestas/index.html', dict)

def __sistemas_agroforestales(request):
    encuestas = filtros_comunes(request)
    ids_saf = [dato[0] for dato in SISTEMAS_CHOICES] #linea bonita :-)
    data = []
    resultados = []
    #sumatoria_saf = encuestas.exclude(saf__sis_agroforestal = 5).aggregate(conteo=Count('saf'),
    #                                area_en_desarrollo=Sum('saf__area_en_desarrollo'),
    #                                area_en_produccion=Sum('saf__area_en_produccion'),
    #                                area_mal_manejo=Sum('saf__area_mal_manejo'),
    #                                area_manejo_regular=Sum('saf__area_manejo_regular'),
    #                                area_buen_manejo=Sum('saf__area_buen_manejo'))
    sumatoria_saf = {'area_en_desarrollo': 0, 'area_en_produccion': 0,
                     'area_mal_manejo': 0, 'area_manejo_regular': 0, 
                     'area_buen_manejo': 0, 'conteo': 0}

    for encuesta in encuestas:
        sumatoria = Saf.objects.filter(encuesta=encuesta).exclude(sis_agroforestal=5).aggregate(conteo=Count('id'),
                                    area_en_desarrollo=Sum('area_en_desarrollo'),
                                    area_en_produccion=Sum('area_en_produccion'),
                                    area_mal_manejo=Sum('area_mal_manejo'),
                                    area_manejo_regular=Sum('area_manejo_regular'),
                                    area_buen_manejo=Sum('area_buen_manejo'))
        for key in sumatoria.keys():
            sumatoria_saf[key] += sumatoria[key] if sumatoria[key] != None else 0

    for id in ids_saf:
        if id == 5: 
            datos = None
            #hack para calcular bien cerca viva
            #datos = encuestas.filter(saf__sis_agroforestal = id).aggregate(conteo=Count('saf'),
            #                            area_en_desarrollo=Sum('saf__area_en_desarrollo'),
            #                            area_en_produccion=Sum('saf__area_en_produccion'),
            #                            area_mal_manejo=Sum('saf__area_mal_manejo'),
            #                            area_manejo_regular=Sum('saf__area_manejo_regular'),
            #                            area_buen_manejo=Sum('saf__area_buen_manejo'))
            #datos['area_en_desarrollo'] = datos['area_en_desarrollo']/10000
            #datos['area_en_produccion'] = datos['area_en_produccion']/10000
            #datos['area_mal_manejo'] = datos['area_mal_manejo']/10000
            #datos['area_manejo_regular'] = datos['area_manejo_regular']/10000
            #datos['area_buen_manejo'] = datos['area_buen_manejo']/10000
        else:
            datos = encuestas.filter(saf__sis_agroforestal = id).aggregate(conteo=Count('saf'),
                                        area_en_desarrollo=Sum('saf__area_en_desarrollo'),
                                        area_en_produccion=Sum('saf__area_en_produccion'),
                                        area_mal_manejo=Sum('saf__area_mal_manejo'),
                                        area_manejo_regular=Sum('saf__area_manejo_regular'),
                                        area_buen_manejo=Sum('saf__area_buen_manejo'))
        if datos!=None:
            fila = []
            fila.append(SISTEMAS_CHOICES[id-1][1])
            fila.append(datos['conteo'])
            #porcentaje
            porcentaje = (float(datos['conteo'])/sumatoria_saf['conteo'])*100 if sumatoria_saf['conteo']!=0 else 0 
            fila.append("%.2f" % porcentaje)
            fila.append(datos['area_en_desarrollo']) if datos['area_en_desarrollo']!=None else fila.append(0)
            fila.append(datos['area_en_produccion']) if datos['area_en_produccion']!=None else fila.append(0)
            fila.append(datos['area_mal_manejo']) if datos['area_mal_manejo']!=None else fila.append(0)
            fila.append(datos['area_manejo_regular']) if datos['area_manejo_regular']!=None else fila.append(0)
            fila.append(datos['area_buen_manejo']) if datos['area_buen_manejo']!=None else fila.append(0)
            resultados.append(fila)

    #Totales
    totals=[]
    totals.append(sumatoria_saf['conteo'])
    totals.append(100)
    totals.append(sumatoria_saf['area_en_desarrollo'])
    totals.append(sumatoria_saf['area_en_produccion'])
    totals.append(sumatoria_saf['area_mal_manejo'])
    totals.append(sumatoria_saf['area_manejo_regular'])
    totals.append(sumatoria_saf['area_buen_manejo'])
    
    total_areas = totals[2] + totals[3]
    final_row = [(totals[4]/total_areas)*100, 
	(totals[5]/total_areas)*100, (totals[6]/total_areas)*100] if total_areas != 0 else [0,0,0]
             
    dict={'data': resultados, 'totals': totals, 'porcentajes': final_row, 
          'super_total': total_areas,'encuestas': encuestas.count()}
    return dict
    
# hoja spss para SAF
def __hoja_spss_saf__(request):
    encuestas = filtros_comunes(request)
    ids_saf = [dato[0] for dato in SISTEMAS_CHOICES] #linea bonita :-)
    data = []
        
    resultados = []
    for encuesta in encuestas:
        fila = []
        fila.append(encuesta.finca.all()[0].comunidad)
        fila.append(encuesta.finca.all()[0].nombre_productor)
        safs = encuesta.saf.all().count()
        for s in range(0,int(safs)):
            fila.append(encuesta.saf.all()[s].get_sis_agroforestal_display())
            fila.append(encuesta.saf.all()[s].area_en_desarrollo)
            fila.append(encuesta.saf.all()[s].area_en_produccion)
            fila.append(encuesta.saf.all()[s].area_mal_manejo)
            fila.append(encuesta.saf.all()[s].area_manejo_regular)
            fila.append(encuesta.saf.all()[s].area_buen_manejo)
            
        resultados.append(fila)
    dict = {'data': resultados}
    return dict
    
@session_required
def hoja_calculo_saf_xls(request):
    dict = __hoja_spss_saf__(request)
    return write_xls('encuestas/spss_saf.html', dict, 'hoja_saf_spss.xls')    

@session_required
def sistemas_agroforestales(request):
    dict = __sistemas_agroforestales(request)
    return direct_to_template(request, 'encuestas/sistemas_agroforestales.html', dict)   

@session_required
def sistemas_agroforestales_pdf(request):
    dict = __sistemas_agroforestales(request)
    return write_pdf('encuestas/sistemas_agroforestales_pdf.html', dict)

@session_required
def sistemas_agroforestales_xls(request):
    dict = __sistemas_agroforestales(request)
    return write_xls('encuestas/sistemas_agroforestales_pdf.html', dict, 'sistemas-agroforestales.xls')

def __seguridad_alimentaria(request):
    encuestas = filtros_comunes(request)
    data = []
    id_alimentos = [dato[0] for dato in ALIMENTO_CHOICES] 
    
    total_encuestas=encuestas.count() #usado para el porcentaje
    resultados = []
    for id in id_alimentos:
        datos = encuestas.filter(seguridad_alimentaria__alimentos=id).aggregate(producen=Sum('seguridad_alimentaria__producen'),
                                                                                compran=Sum('seguridad_alimentaria__comprar'))
        for key in datos.keys():
            if datos[key]==None:
                datos[key]=0
        nivel_consumo = encuestas.filter(seguridad_alimentaria__alimentos=id,
                                        seguridad_alimentaria__nivel_consumo_suficiente=2).aggregate(nivel=Count('seguridad_alimentaria'))
        fila=[]
        fila.append(ALIMENTO_CHOICES[id-1][1])
        fila.append(datos['producen'])
        porcentaje = (float(datos['producen'])/total_encuestas)*100
        fila.append("%.2f" % porcentaje) 
        fila.append(datos['compran'])
        porcentaje = (float(datos['compran'])/total_encuestas)*100
        fila.append("%.2f" % porcentaje) 
        fila.append(nivel_consumo['nivel'])
        porcentaje = (float(nivel_consumo['nivel'])/total_encuestas)*100
        fila.append("%.2f" % porcentaje) 
        resultados.append(fila)

    dict = {'data': resultados, 'encuestas': total_encuestas}
    return dict   

@session_required
def seguridad_alimentaria(request):
    dict = __seguridad_alimentaria(request)
    return direct_to_template(request,'encuestas/seguridad_alimentaria.html', dict)   

@session_required
def seguridad_alimentaria_pdf(request):
    dict = __seguridad_alimentaria(request)
    return write_pdf('encuestas/seguridad_alimentaria_pdf.html', dict)

@session_required
def seguridad_alimentaria_xls(request):
    dict = __seguridad_alimentaria(request)
    return write_xls('encuestas/seguridad_alimentaria_pdf.html', dict, 'seguridad_alimentaria.xls')
    
# hoja spss para seguridad alimentaria
def __hoja_spss_seguridad__(request):
    encuestas = filtros_comunes(request)
    data = []
    id_alimentos = [dato[0] for dato in ALIMENTO_CHOICES]
        
    resultados = []
    for encuesta in encuestas:
        fila = []
        fila.append(encuesta.finca.all()[0].comunidad)
        fila.append(encuesta.finca.all()[0].nombre_productor)
        seguridad = encuesta.seguridad_alimentaria.all().count()
        for s in range(0,int(seguridad)):
            fila.append(encuesta.seguridad_alimentaria.all()[s].get_alimentos_display())
            fila.append(encuesta.seguridad_alimentaria.all()[s].producen)
            fila.append(encuesta.seguridad_alimentaria.all()[s].comprar)
            fila.append(encuesta.seguridad_alimentaria.all()[s].get_nivel_consumo_suficiente_display())
            
        resultados.append(fila)
    dict = {'data':resultados}
    return dict    

@session_required
def hoja_calculo_seguridad_xls(request):
    dict = __hoja_spss_seguridad__(request)
    return write_xls('encuestas/spss_seguridad.html', dict, 'hoja_seguridad_alimentaria.xls')       

def __educacion(request):
    datos = filtros_comunes(request)
    
    resultados = []
    for i in [dato[0] for dato in SEXO_CHOICES]:
        suma = datos.filter(educacion__sexo_edad = i).aggregate(num_persona = Sum('educacion__num_persona'),
                                                            nosabe_leer = Sum('educacion__nosabe_leer'),
                                                            pri_completa = Sum('educacion__pri_completa'),
                                                            pri_incompleta = Sum('educacion__pri_incompleta'),
                                                            secu_incompleta = Sum('educacion__secu_incompleta'),
                                                            secu_completa = Sum('educacion__secu_completa'),
                                                            universitario = Sum('educacion__uni_o_tecnico'),
                                                            estudiando = Sum('educacion__estudiando'),
                                                            circ_estudio = Sum('educacion__circ_estudio_adulto')
                                                           )
        #validando...
        for key in suma.keys():
            if suma[key] == None:
                suma[key] = 0
        fila = []
        fila.append(SEXO_CHOICES[i-1][1])
        fila.append(suma['num_persona'])
        porcentaje = (float(suma['nosabe_leer'])/suma['num_persona'])*100 if suma['num_persona']!=0 else 0 
        fila.append("%.2f" % porcentaje)
        porcentaje = (float(suma['pri_incompleta'])/suma['num_persona'])*100 if suma['num_persona']!=0 else 0
        fila.append("%.2f" % porcentaje)
        porcentaje = (float(suma['pri_completa'])/suma['num_persona'])*100 if suma['num_persona']!=0 else 0
        fila.append("%.2f" % porcentaje)
        porcentaje = (float(suma['secu_incompleta'])/suma['num_persona'])*100 if suma['num_persona']!=0 else 0
        fila.append("%.2f" % porcentaje)
        porcentaje = (float(suma['secu_completa'])/suma['num_persona'])*100 if suma['num_persona']!=0 else 0
        fila.append("%.2f" % porcentaje)
        porcentaje = (float(suma['universitario'])/suma['num_persona'])*100 if suma['num_persona']!=0 else 0
        fila.append("%.2f" % porcentaje)
        porcentaje = (float(suma['estudiando'])/suma['num_persona'])*100 if suma['num_persona']!=0 else 0
        fila.append("%.2f" % porcentaje)
        porcentaje = (float(suma['circ_estudio'])/suma['num_persona'])*100 if suma['num_persona']!=0 else 0
        fila.append("%.2f" % porcentaje)
        resultados.append(fila)
    encuestas = datos.count()
    dict = {'data': resultados,'encuestas': encuestas}
    return dict

# hoja spss para educacion  
def __hoja_spss_educacion__(request):
    datos = filtros_comunes(request)
        
    resultados = []
    for encuesta in datos:
        fila = []
        fila.append(encuesta.finca.all()[0].comunidad.nombre)
        fila.append(encuesta.finca.all()[0].nombre_productor)
        educacion = encuesta.educacion.all().count()
        for a in range(0,int(educacion)):
            try:
                fila.append(encuesta.educacion.all()[a].get_sexo_edad_display()) 
                fila.append(encuesta.educacion.all()[a].num_persona)
                fila.append(encuesta.educacion.all()[a].nosabe_leer)
                fila.append(encuesta.educacion.all()[a].pri_incompleta)
                fila.append(encuesta.educacion.all()[a].pri_completa)
                fila.append(encuesta.educacion.all()[a].secu_incompleta)
                fila.append(encuesta.educacion.all()[a].secu_completa)
                fila.append(encuesta.educacion.all()[a].uni_o_tecnico)
                fila.append(encuesta.educacion.all()[a].estudiando)
                fila.append(encuesta.educacion.all()[a].circ_estudio_adulto)
            except:
                pass
            
        resultados.append(fila)
    dict = {'data': resultados}
    return  dict

@session_required
def hoja_calculo_educacion_xls(request):
    dict = __hoja_spss_educacion__(request)
    return write_xls('encuestas/spss_educacion.html', dict, 'hoja_educacion_spss.xls')           

@session_required
def educacion(request):
    dict = __educacion(request)
    return direct_to_template(request,'encuestas/educacion.html', dict)

@session_required
def educacion_pdf(request):
    dict = __educacion(request)
    return write_pdf('encuestas/educacion_pdf.html', dict)

@session_required
def educacion_xls(request):
    dict = __educacion(request)
    return write_xls('encuestas/educacion_pdf.html', dict, 'educacion.xls')

def __cobertura_boscosa(request):
    datos = filtros_comunes(request)

    suma = datos.aggregate(area_total = Sum('boscosa__area_total'),
                                bosque_primario = Sum('boscosa__bosque_primario'),
                                bosque_secundario= Sum('boscosa__bosque_secundario'),
                                bosque_galeria = Sum('boscosa__bosque_galeria'),
                                humedales = Sum('boscosa__humedales'),
                                tacotales = Sum('boscosa__tacotal'), 
                                cultivos_perennes = Sum('boscosa__cultivos_perennes'), 
                                cultivos_semiperennes = Sum('boscosa__cultivos_semiperennes'), 
                                cultivos_anuales = Sum('boscosa__cultivos_anuales'), 
                                huertos_mixtos = Sum('boscosa__huerto_mixto'), 
                                potrero_abierto = Sum('boscosa__potrero_abierto'),
                                potrero_arboles = Sum('boscosa__potrero_arboles'),
                                plantaciones_forestales= Sum('boscosa__plantaciones_forestales'),
                                parcela_energetica= Sum('boscosa__parcela_energetica')
                                )
    #validando que no existan valores none.
    for key in suma.keys():
        if suma[key] == None:
            suma[key]=0
    #contando de una manera fea pero ni modo :-(
    conteo = {}
    conteo['area_total'] = datos.count()
    conteo['bosque_primario'] = datos.filter(boscosa__bosque_primario__gt=0).count()
    conteo['bosque_secundario'] = datos.filter(boscosa__bosque_secundario__gt=0).count()
    conteo['bosque_galeria'] = datos.filter(boscosa__bosque_galeria__gt=0).count()
    conteo['humedales'] = datos.filter(boscosa__humedales__gt=0).count()
    conteo['tacotales'] = datos.filter(boscosa__tacotal__gt=0).count()
    conteo['cultivos_perennes'] = datos.filter(boscosa__cultivos_perennes__gt=0).count()
    conteo['cultivos_anuales'] = datos.filter(boscosa__cultivos_anuales__gt=0).count()
    conteo['cultivos_semiperennes'] = datos.filter(boscosa__cultivos_semiperennes__gt=0).count()
    conteo['huertos_mixtos'] = datos.filter(boscosa__huerto_mixto__gt=0).count()
    conteo['potrero_abierto'] = datos.filter(boscosa__potrero_abierto__gt=0).count()
    conteo['potrero_arboles'] = datos.filter(boscosa__potrero_arboles__gt=0).count()
    conteo['plantaciones_forestales'] = datos.filter(boscosa__plantaciones_forestales__gt=0).count()
    conteo['parcela_energetica'] = datos.filter(boscosa__parcela_energetica__gt=0).count()
    resultados = []
    try:
        porcentaje_cobertura_boscosa = (((float(suma['bosque_galeria']) * 1) + (float(suma['bosque_primario']) * 1) +
                             (float(suma['bosque_secundario'])*0.7) + (float(suma['cultivos_perennes'])*0.5) + 
                             (float(suma['cultivos_semiperennes'])*0.5) + (float(suma['huertos_mixtos']) * 0.5) + 
                             (float(suma['parcela_energetica'])*0.7) + (float(suma['plantaciones_forestales']) * 1) + 
                             (float(suma['potrero_arboles']) * 0.3))/float(suma['area_total']))*100
        porcentaje_cobertura_boscosa = "%.2f" % porcentaje_cobertura_boscosa
    except:
        porcentaje_cobertura_boscosa = 0
    #La magia comienza
    lista_llaves = suma.keys()
    lista_llaves.sort()
    for key in lista_llaves:
        fila = [] # [key, conteo, porcentaje, sumatoria manzanas, porcentaje area, cobertura]
        fila.append(key.replace('_', ' ').capitalize()) #tomamos la key del diccionario y la hacemos legible
        #conteo de las areas
        #el conteo esta bananoide
        fila.append(conteo[key])
        porcentaje_conteo = (float(conteo[key])/conteo['area_total'])*100 if conteo['area_total']!=0 else 0
        fila.append("%.2f" % porcentaje_conteo)
        fila.append(suma[key])
        porcentaje_area = (suma[key]/suma['area_total'])*100 if suma['area_total']!= 0  else 0
        fila.append("%.2f" % porcentaje_area)
        resultados.append(fila)

    dict = {'data': resultados,'total': datos.count(),
            'cobertura_boscosa': porcentaje_cobertura_boscosa}
    return dict

# hoja de spss para cobertura boscosa  
def __hoja_spss_cobertura_boscosa__(request):
    datos = filtros_comunes(request)
    
    resultados = []
    for encuesta in datos:
        fila = []
        fila.append(encuesta.finca.all()[0].nombre_productor)
        fila.append(encuesta.finca.all()[0].comunidad.nombre)
        boscosa = encuesta.boscosa.all().count()
        for a in range(0,int(boscosa)):
            try:
                fila.append(encuesta.boscosa.all()[a].bosque_primario)
                fila.append(encuesta.boscosa.all()[a].bosque_secundario)
                fila.append(encuesta.boscosa.all()[a].bosque_galeria)
                fila.append(encuesta.boscosa.all()[a].humedales)
                fila.append(encuesta.boscosa.all()[a].tacotal)
                fila.append(encuesta.boscosa.all()[a].cultivos_perennes)
                fila.append(encuesta.boscosa.all()[a].cultivos_semiperennes)
                fila.append(encuesta.boscosa.all()[a].cultivos_anuales)
                fila.append(encuesta.boscosa.all()[a].huerto_mixto)
                fila.append(encuesta.boscosa.all()[a].potrero_abierto)
                fila.append(encuesta.boscosa.all()[a].potrero_arboles)
                fila.append(encuesta.boscosa.all()[a].cerca_viva)
                fila.append(encuesta.boscosa.all()[a].cerca_muerta)
                fila.append(encuesta.boscosa.all()[a].plantaciones_forestales)
                fila.append(encuesta.boscosa.all()[a].parcela_energetica)
            except:
                pass
        resultados.append(fila)
    dict = {'datos': resultados}
    return dict
    
@session_required
def hoja_calculo_boscosa_xls(request):
    dict = __hoja_spss_cobertura_boscosa__(request)
    return write_xls('encuestas/spss_boscosa.html', dict, 'hoja_boscosa_spss.xls')  
        

@session_required
def cobertura_boscosa(request):
    dict = __cobertura_boscosa(request)
    return direct_to_template(request, 'encuestas/cobertura_boscosa.html', dict)

@session_required
def cobertura_boscosa_pdf(request):
    dict =  __cobertura_boscosa(request)
    return write_pdf('encuestas/cobertura_boscosa_pdf.html', dict)

@session_required
def cobertura_boscosa_xls(request):
    dict =  __cobertura_boscosa(request)
    return write_xls('encuestas/cobertura_boscosa_pdf.html', dict, 'cobertura_boscosa.xls')

def __jovenes_en_poder(request):
    #Esto puede estar malo por que no se que tipo de datos se introduciran
    #ya que actualmente no hay datos
    datos = filtros_comunes(request)

    suma_varones = datos.filter(cono_jo_rass_mata__jovenes__iexact = 'varones').count()
    suma_mujeres = datos.filter(cono_jo_rass_mata__jovenes__iexact = 'mujeres').count()
    total = suma_varones + suma_mujeres
    porcentaje_varones = (suma_varones/(total))*100 if total>0 else 0
    porcentaje_mujeres= (suma_mujeres/(total))*100 if total>0 else 0 
    dict = {'suma_varones': suma_varones, 'suma_mujeres': suma_mujeres, 
            'porcentaje_varones': porcentaje_varones, 'porcentaje_mujeres': porcentaje_mujeres,
            'total': total}
    return dict 

@session_required
def jovenes_en_poder(request):
    dict = __jovenes_en_poder(request)
    return direct_to_template(request,'encuestas/jovenes_en_poder.html', dict)

@session_required
def jovenes_en_poder_pdf(request):
    dict = __jovenes_en_poder(request)
    return write_pdf('encuestas/jovenes_en_poder_pdf.html', dict)

@session_required
def jovenes_en_poder_xls(request):
    dict = __jovenes_en_poder(request)
    return write_xls('encuestas/jovenes_en_poder_pdf.html', dict, 'jovenes_en_poder.xls')

# Indicador 1. Datos generales de las fincas
def __indicador1(request):
    indifinca = filtros_comunes(request)

    total_fincas = indifinca.count()
    # TODO: Frecuencia de animales
    bovino = indifinca.filter(finca__animal_bovino__gt=0).count()
    porcino = indifinca.filter(finca__animal_porcino__gt=0).count()
    equino = indifinca.filter(finca__animal_equino__gt=0).count()
    aves = indifinca.filter(finca__animal_aves__gt=0).count()
    caprino = indifinca.filter(finca__animal_caprino__gt=0).count()
    # TODO: Porcentajes de los animales
    por_bovino = (float(bovino) / total_fincas) * 100 if total_fincas != 0 else 0
    por_porcino = (float(porcino) / total_fincas) * 100 if total_fincas != 0 else 0
    por_equino = (float(equino) / total_fincas) * 100 if total_fincas != 0 else 0
    por_aves = (float(aves) / total_fincas) * 100 if total_fincas != 0  else 0
    por_caprino = (float(caprino) / total_fincas) * 100 if total_fincas != 0 else 0
    # TODO: totales por animales
    sum_bovino = indifinca.aggregate(Sum('finca__animal_bovino'))
    sum_porcino = indifinca.aggregate(Sum('finca__animal_porcino'))
    sum_equino = indifinca.aggregate(Sum('finca__animal_equino'))
    sum_aves = indifinca.aggregate(Sum('finca__animal_aves'))
    sum_caprino = indifinca.aggregate(Sum('finca__animal_caprino'))
    # TODO: promedio de los animales
    pro_bovino = indifinca.filter(finca__animal_bovino__gt=0).aggregate(Avg('finca__animal_bovino'))
    pro_porcino = indifinca.filter(finca__animal_porcino__gt=0).aggregate(Avg('finca__animal_porcino'))
    pro_equino = indifinca.filter(finca__animal_equino__gt=0).aggregate(Avg('finca__animal_equino'))
    pro_aves = indifinca.filter(finca__animal_aves__gt=0).aggregate(Avg('finca__animal_aves'))
    pro_caprino = indifinca.filter(finca__animal_caprino__gt=0).aggregate(Avg('finca__animal_caprino'))
    # TODO: tabla de areas de fincas
    cero = indifinca.filter(finca__area_finca=0).count()
    ini_cinco = str(0.1)
    fin_cinco = str(5.99)
    cinco = indifinca.filter(finca__area_finca__range=(ini_cinco, fin_cinco)).count()
    ini_veinte = 6
    fin_veinte = str(20.99)
    veinte = indifinca.filter(finca__area_finca__range=(ini_veinte, fin_veinte)).count()
    ini_cincuenta = 21
    fin_cincuenta = str(50.99)
    cincuenta = indifinca.filter(finca__area_finca__range=(ini_cincuenta, fin_cincuenta)).count()
    ini_may = str(51)
    mayor = indifinca.filter(finca__area_finca__gt=ini_may).count()
    # TODO: porcentajes en area de fincas
    por_cero = (float(cero) / total_fincas) * 100 if total_fincas != 0 else 0
    por_cinco = (float(cinco) / total_fincas) * 100 if total_fincas != 0 else 0
    por_veinte = (float(veinte) / total_fincas) * 100 if total_fincas != 0 else 0
    por_cincuenta = (float(cincuenta) / total_fincas) * 100 if total_fincas != 0 else 0
    por_mayor = (float(mayor) / total_fincas) * 100 if total_fincas != 0 else 0
    
    #FOTOS
    if indifinca.count() == 1:
        #si el count es igual a uno es que seleccionamos a un solo productor
       fotos = Fotos.objects.filter(encuesta=indifinca)
    else:
        fotos = None
    #ahora probar hacer el punto en el mapa
    if indifinca.count() == 1:
        lugar = Finca.objects.filter(encuesta=indifinca)
    else:
        lugar = None
    dict = {'encuestas':indifinca, 'total_fincas':total_fincas,
            'bovino': bovino, 'porcino': porcino, 'equino':equino, 
            'aves':aves, 'caprino':caprino, 'por_bovino':por_bovino, 
            'por_porcino':por_porcino, 'por_equino': por_equino, 
            'por_aves': por_aves, 'por_caprino': por_caprino, 
            'sum_bovino':sum_bovino, 'sum_porcino':sum_porcino, 
            'sum_equino': sum_equino, 'sum_aves': sum_aves, 
            'sum_caprino': sum_caprino, 'pro_bovino':pro_bovino, 
            'pro_porcino':pro_porcino, 'pro_equino':pro_equino, 
            'pro_aves':pro_aves, 'pro_caprino':pro_caprino,
            'cinco':cinco, 'veinte':veinte, 'cincuenta':cincuenta, 
            'mayor': mayor, 'por_cinco':por_cinco, 'por_veinte':por_veinte, 
            'por_cincuenta':por_cincuenta, 
            'por_mayor':por_mayor, 'fotos': fotos, 'cero':cero, 
            'por_cero': por_cero,'lugar':lugar}
    return dict

# hoja spss de datos generales
def __hoja_de_calculo(request):
    indifinca = filtros_comunes(request)
        
    resultados = []
    for encuesta in indifinca:
        fila = []
        fila.append(encuesta.finca.all()[0].finca)
        fila.append(encuesta.finca.all()[0].comunidad.nombre)
        fila.append(encuesta.finca.all()[0].nombre_productor)
        fila.append(encuesta.finca.all()[0].get_sexo_display())
        fila.append(encuesta.finca.all()[0].cedula_productor)
        fila.append(encuesta.finca.all()[0].area_finca)
        fila.append(encuesta.finca.all()[0].animal_bovino)
        fila.append(encuesta.finca.all()[0].animal_porcino)
        fila.append(encuesta.finca.all()[0].animal_equino)
        fila.append(encuesta.finca.all()[0].animal_aves)
        fila.append(encuesta.finca.all()[0].animal_caprino)
        fila.append(encuesta.finca.all()[0].get_tipo_casa_display())
        fila.append(encuesta.finca.all()[0].area_casa)
        fila.append(encuesta.finca.all()[0].get_fuente_agua_display())
        fila.append(encuesta.finca.all()[0].get_legalidad_display())
        fila.append(encuesta.finca.all()[0].propietario)
        resultados.append(fila)
        
    dict = {'datos': resultados}
    return  dict
    
@session_required
def hoja_calculo_indicador1_xls(request):
    dict = __hoja_de_calculo(request)
    return write_xls('encuestas/spss_indicador1.html', dict, 'hoja_datosgenerales_spss.xls')
                                     
@session_required
def indicador1(request):
    dict = __indicador1(request)
    return direct_to_template(request,"encuestas/indicador-uno.html", dict) 

@session_required
def indicador1_pdf(request):
    dict = __indicador1(request)
    return write_pdf('encuestas/indicador-uno-pdf.html', dict)

@session_required
def indicador1_xls(request):
    dict = __indicador1(request)
    return write_xls('encuestas/indicador-uno-pdf.html', dict, 'finca.xls')

# Indicador no. 5 Fuentes de Ingreso familiar 

def indicadorcount(numero, indifuente):
	return indifuente.filter(ingreso__fuente_ingreso=numero).count()

def indicadorsum(numero, indifuente):
	return indifuente.filter(ingreso__fuente_ingreso=numero).aggregate(Sum('ingreso__cantidad_vendida'))['ingreso__cantidad_vendida__sum']

def indicadoravg(numero, indifuente):
	return indifuente.filter(ingreso__fuente_ingreso=numero).aggregate(Avg('ingreso__precio_venta'))['ingreso__precio_venta__avg']

def fuente(numero):
	return FUENTE_CHOICES[numero-1][1]

def unidad(numero, indifuente):
    a=indifuente.filter(ingreso__fuente_ingreso=numero)
    b=a[0].ingreso
    c= b.filter(fuente_ingreso=numero)

    d=c[0]
    return d.get_unidad_display()

# comienza el views
@session_required
def __indicador5(request):
    indifuente = filtros_comunes(request)

    casos = indifuente.count()
    
    respuesta = {'casos':casos}
    # la suma de los ingresos
    respuesta['producto']=[]
    respuesta['ingreso_total']=0
#    respuesta['ingreso_total_final']=0
    respuesta['ingreso_neto']=0
    respuesta['ingreso_promedio']=0
    for i in range(1,41):
        respuesta['producto'].append({'nombre':fuente(i)})
        try:
            respuesta['producto'][i-1]['unidad'] = unidad(i, indifuente)
        except:
            pass
        try:
            respuesta['producto'][i-1]['count'] = indicadorcount(i, indifuente)
        except:
            pass
        try:
            respuesta['producto'][i-1]['sum'] = indicadorsum(i, indifuente)
        except:
            pass
        try:
            respuesta['producto'][i-1]['avg'] = indicadoravg(i, indifuente)
        except:
            pass
        try:
            respuesta['producto'][i-1]['ingreso'] = respuesta['producto'][i-1]['sum'] * Decimal(str(respuesta['producto'][i-1]['avg']))
            respuesta['ingreso_total'] += respuesta['producto'][i-1]['ingreso']
#            respuesta['ingreso_total_final']= round(respuesta['ingreso_total'],2)
            respuesta['ingreso_promedio'] = round(respuesta['ingreso_total'] / casos,2)
            respuesta['ingreso_neto'] = round(respuesta['ingreso_promedio'] * 0.40,2)
        except:
            pass
        
    for i in range(1,41):
        try:
            respuesta['producto'][i-1]['porcentaje'] = respuesta['producto'][i-1]['ingreso'] / respuesta['ingreso_total'] * 100
        except:
            pass
    return respuesta
    
# hoja spss de ingreso familiar
def __hoja_spss_ingreso__(request):
    indifuente = filtros_comunes(request)
        
    resultados = []
    for encuesta in indifuente:
        fila = []
        fila.append(encuesta.finca.all()[0].comunidad)
        fila.append(encuesta.finca.all()[0].nombre_productor)
        ingreso = encuesta.ingreso.all().count()
        for a in range(0,int(ingreso)):
            fila.append(encuesta.ingreso.all()[a].get_fuente_ingreso_display())
            fila.append(encuesta.ingreso.all()[a].get_unidad_display())
            fila.append(encuesta.ingreso.all()[a].cantidad_vendida)
            fila.append(encuesta.ingreso.all()[a].precio_venta)
            fila.append(encuesta.ingreso.all()[a].ingreso_venta)
            fila.append(encuesta.ingreso.all()[a].get_a_quien_vendio_display())
            fila.append(encuesta.ingreso.all()[a].quien_maneja_negocio)
            
        resultados.append(fila)
    dict = {'data':resultados}
    return dict
    
@session_required
def hoja_calculo_ingreso_xls(request):
    dict = __hoja_spss_ingreso__(request)
    return write_xls('encuestas/spss_ingreso.html', dict, 'hoja_ingreso_familiar_spss.xls')    
     
@session_required
def indicador5(request):
    dict = __indicador5(request)
    return direct_to_template(request,"encuestas/indicador-cinco.html", dict)

@session_required
def indicador5_pdf(request):
    dict = __indicador5(request)
    return write_pdf("encuestas/indicador-cinco-pdf.html", dict)

@session_required
def indicador5_xls(request):
    dict = __indicador5(request)
    return write_xls("encuestas/indicador-cinco-pdf.html", dict, 'ingreso_familiar.xls')
    
# Indicador no. 4 Produccion, comercializacion y precio

def produccioncount(numero, indiproduccion):
    return indiproduccion.filter(produc_comer_precio__prod_agroforestales=numero).count()

def agroforestalsum(numero, indiproduccion):
    return indiproduccion.filter(produc_comer_precio__prod_agroforestales=numero).aggregate(Sum('produc_comer_precio__area_cosecha_MZ'))['produc_comer_precio__area_cosecha_MZ__sum']

def prodanualsum(numero, indiproduccion):
    return indiproduccion.filter(produc_comer_precio__prod_agroforestales=numero).aggregate(Sum('produc_comer_precio__prod_total_anual'))['produc_comer_precio__prod_total_anual__sum']

def consumosum(numero, indiproduccion):
    return indiproduccion.filter(produc_comer_precio__prod_agroforestales=numero).aggregate(Sum('produc_comer_precio__auto_consumo'))['produc_comer_precio__auto_consumo__sum']

def norganizadasum(numero, indiproduccion):
    return indiproduccion.filter(produc_comer_precio__prod_agroforestales=numero).aggregate(Sum('produc_comer_precio__cant_venta_no_organizada'))['produc_comer_precio__cant_venta_no_organizada__sum']

def organizadasum(numero, indiproduccion):
    return indiproduccion.filter(produc_comer_precio__prod_agroforestales=numero).aggregate(Sum('produc_comer_precio__cant_venta_organizada'))['produc_comer_precio__cant_venta_organizada__sum']

# precio de venta no organizada
def noavg(numero, indiproduccion):
    return indiproduccion.filter(produc_comer_precio__prod_agroforestales=numero).aggregate(Avg('produc_comer_precio__precio_venta_no_organizada'))['produc_comer_precio__precio_venta_no_organizada__avg']

# precio de venta organizada
def siavg(numero, indiproduccion):
    return indiproduccion.filter(produc_comer_precio__prod_agroforestales=numero).aggregate(Avg('produc_comer_precio__precio_venta_organizada'))['produc_comer_precio__precio_venta_organizada__avg']

def produccion(numero):
    return PRODUCTO_CHOICES[numero-1][1]

def unidadprod(numero, indiproduccion):
    a = indiproduccion.filter(produc_comer_precio__prod_agroforestales=numero)
    b = a[0].produc_comer_precio
    c= b.filter(prod_agroforestales=numero)
    
    d=c[0]
    return d.get_unidad_medida_display()

def __indicador4(request):
    indiproduccion = filtros_comunes(request)
        
    casos = indiproduccion.count()
    respuestas = {'casos':casos}
    respuestas['producto']=[]
    respuestas['ingreso_no_org']=0
    respuestas['ingreso_org']=0
    respuestas['ingreso_total_no']=0
    respuestas['ingreso_total_si']=0
    for i in range(1,23):
        respuestas['producto'].append({'nombre':produccion(i)})
        try:
            respuestas['producto'][i-1]['unidad'] = unidadprod(i, indiproduccion)
        except:
        	pass
        try:
            respuestas['producto'][i-1]['count'] = produccioncount(i, indiproduccion)
        except:
            pass
        try:
            respuestas['producto'][i-1]['agro'] = agroforestalsum(i, indiproduccion)
        except:
            pass
        try:
            respuestas['producto'][i-1]['anual'] = prodanualsum(i, indiproduccion)
        except:
            pass
        try:
            respuestas['producto'][i-1]['consumo'] = consumosum(i, indiproduccion)
        except:
            pass
        try:
            respuestas['producto'][i-1]['no'] = norganizadasum(i, indiproduccion)
        except:
            pass
        try:
            respuestas['producto'][i-1]['si'] = organizadasum(i, indiproduccion)
        except:
            pass
        try:
            respuestas['producto'][i-1]['preciono'] = noavg(i, indiproduccion)
        except:
            pass
        try:
            respuestas['producto'][i-1]['preciosi'] = siavg(i, indiproduccion)
        except:
            pass
        try:
            respuestas['producto'][i-1]['ingreso_no_org'] = respuestas['producto'][i-1]['no'] * Decimal(str(respuestas['producto'][i-1]['preciono']))
            respuestas['ingreso_total_no']+=respuestas['producto'][i-1]['ingreso_no_org']
        except:
            pass
        try:
            respuestas['producto'][i-1]['ingreso_org'] = respuestas['producto'][i-1]['si'] * Decimal(str(respuestas['producto'][i-1]['preciosi']))
            respuestas['ingreso_total_si']+=respuestas['producto'][i-1]['ingreso_org']
        except:
            pass

    return respuestas 

@session_required
def indicador4(request):
    dict = __indicador4(request)
    return direct_to_template(request,"encuestas/indicador-cuatro.html", dict)

@session_required
def indicador4_pdf(request):
    dict = __indicador4(request)
    return write_pdf("encuestas/indicador-cuatro-pdf.html", dict)
    
@session_required
def indicador4_xls(request):
    dict = __indicador4(request)
    return write_xls("encuestas/indicador-cuatro-pdf.html", dict, 'produccion.xls')
    
# hoja spss de producion y comercializacion
def __hoja_spss_produccion__(request):
    indiproduccion = filtros_comunes(request)
        
    resultados = []
    for encuesta in indiproduccion:
        fila = []
        fila.append(encuesta.finca.all()[0].comunidad)
        fila.append(encuesta.finca.all()[0].nombre_productor)
        prod = encuesta.produc_comer_precio.all().count()
        for p in range(0,int(prod)):
            fila.append(encuesta.produc_comer_precio.all()[p].get_prod_agroforestales_display())
            fila.append(encuesta.produc_comer_precio.all()[p].area_cosecha_MZ)
            fila.append(encuesta.produc_comer_precio.all()[p].prod_total_anual)
            fila.append(encuesta.produc_comer_precio.all()[p].get_unidad_medida_display())
            fila.append(encuesta.produc_comer_precio.all()[p].auto_consumo)
            fila.append(encuesta.produc_comer_precio.all()[p].cant_venta_no_organizada)
            fila.append(encuesta.produc_comer_precio.all()[p].precio_venta_no_organizada)
            fila.append(encuesta.produc_comer_precio.all()[p].cant_venta_organizada)
            fila.append(encuesta.produc_comer_precio.all()[p].precio_venta_organizada)
            
        resultados.append(fila)
    dict = {'data':resultados}
    return dict
    
@session_required
def hoja_calculo_produccion_xls(request):
    dict = __hoja_spss_produccion__(request)
    return write_xls('encuestas/spss_produccion.html', dict, 'hoja_produccion_comercializacion_spss.xls')
                                     
    

#los Grafos se devuelven en JSON.
@session_required
def grafos(request):
    datos = filtros_comunes(request)
    
    dict = {'encuestas': datos.count()}
    return direct_to_template(request,"encuestas/grafos.html", dict)

@session_required
def grafo_tipo_de_casa(request):
    datos = filtros_comunes(request)
    data = []
    mensaje = "Tipo de casa"
    
    resultados=[] #lista de tuplas que contiene label y el value
    for i in range(1, len(TIPO_CHOICES)+1):
        suma = datos.filter(finca__tipo_casa = i).aggregate(Sum('finca__tipo_casa'))
        if suma['finca__tipo_casa__sum']==None:
            suma['finca__tipo_casa__sum'] = 0
        label = [data[1] for data in TIPO_CHOICES][i-1] #magia
        resultados.append((label, suma['finca__tipo_casa__sum']))
    
    grafo = PieChart3D(600,350)
    grafo.add_data([int(data[1]) for data in resultados])
    grafo.set_colours([ 'FFBC13','22A410','E6EC23','2B2133','BD0915','3D43BD'])
    #TODO: poner porcentajes y valores de datos
    grafo.set_legend([data[0] for data in resultados])
    porcentajes = saca_porcentajes([data[1] for data in resultados])
    grafo.set_pie_labels(porcentajes)
    grafo.set_legend_position("b")
    grafo.set_title(mensaje) #no estoy seguro de esto aun

    dict = {'url': grafo.get_url()}
    return HttpResponse(simplejson.dumps(dict), mimetype='application/javascript')

@session_required
def grafo_dueno_propiedad(request):
    datos = filtros_comunes(request)
    data = []
    mensaje = "Tipo de Propietarios"

    resultados = []
    for i in [a[0] for a in DUENO_CHOICES]: 
        suma = datos.filter(finca__propietario=i).aggregate(finca__propietario = Count('finca__propietario'))
        if suma['finca__propietario'] == None:
            suma['finca__propietario'] = 0
        label = i 
        resultados.append((label, suma['finca__propietario']))

    grafo = PieChart3D(600,350)
    grafo.add_data([int(data[1]) for data in resultados])
    grafo.set_colours([ 'FFBC13','22A410','E6EC23','2B2133','BD0915','3D43BD'])
    grafo.set_legend([data[0] for data in resultados])
    grafo.set_legend_position("b")
    porcentajes = saca_porcentajes([data[1] for data in resultados])
    grafo.set_pie_labels(porcentajes)
    grafo.set_title(mensaje)

    dict = {'url': grafo.get_url()}
    return HttpResponse(simplejson.dumps(dict), mimetype='application/javascript')


@session_required
def grafo_legalidad_propiedad(request):
    datos = filtros_comunes(request)
    data = []
    mensaje = "Legalidad de propiedades"

    resultados = []
    for i in range(1, len(LEGALIDAD_CHOICES)+1):
        suma = datos.filter(finca__legalidad=i).aggregate(Sum('finca__legalidad'))
        if suma['finca__legalidad__sum'] == None:
            suma['finca__legalidad__sum'] = 0
        label = [data[1] for data in LEGALIDAD_CHOICES][i-1]
        resultados.append((label, suma['finca__legalidad__sum']))

    grafo = PieChart3D(600,350)
    grafo.add_data([int(data[1]) for data in resultados])
    grafo.set_colours([ 'FFBC13','22A410','E6EC23','2B2133','BD0915','3D43BD'])
    porcentajes = saca_porcentajes([data[1] for data in resultados])
    grafo.set_legend([data[0] for data in resultados])
    grafo.set_legend_position("b")
    grafo.set_pie_labels(porcentajes)
    grafo.set_title(mensaje)

    dict = {'url': grafo.get_url()}
    return HttpResponse(simplejson.dumps(dict), mimetype='application/javascript')

@session_required
def grafo_fuente_de_agua(request):
    datos = filtros_comunes(request)
    data = []
    mensaje = "Fuentes de Agua"
    resultados = []
    for i in range(1, len(AGUA_CHOICES)+1):
        suma = datos.filter(finca__legalidad=i).aggregate(Sum('finca__fuente_agua'))
        if suma['finca__fuente_agua__sum'] == None:
            suma['finca__fuente_agua__sum'] = 0
        label = [data[1] for data in AGUA_CHOICES][i-1]
        resultados.append((label, suma['finca__fuente_agua__sum']))

    grafo = PieChart3D(600,350)
    grafo.add_data([int(data[1]) for data in resultados])
    grafo.set_colours([ 'FFBC13','22A410','E6EC23','2B2133','BD0915','3D43BD'])
    porcentajes = saca_porcentajes([data[1] for data in resultados])
    grafo.set_legend([data[0] for data in resultados])
    grafo.set_legend_position("b")
    grafo.set_pie_labels(porcentajes)
    grafo.set_title(mensaje)

    dict = {'url': grafo.get_url()}
    return HttpResponse(simplejson.dumps(dict), mimetype='application/javascript')


# Vistas para obtener los municipios del cosito de incio
def get_municipios(request, departamento):
    municipios = Municipio.objects.filter(departamento = departamento)
    lista = [(municipio.id, municipio.nombre) for municipio in municipios]
    return HttpResponse(simplejson.dumps(lista), mimetype='application/javascript')

def get_comunidad(request, municipio):
    comunidades = Comunidad.objects.filter(municipio = municipio )
    lista = [(comunidad.id, comunidad.nombre) for comunidad in comunidades]
    return HttpResponse(simplejson.dumps(lista), mimetype='application/javascript')

@session_required
def grafo_a_vendio(request):
    indifuente = filtros_comunes(request)
    mensaje = "A quienes venden"
        
    resultados=[]
    for i in range(1, len(QUIEN_CHOICES)+1):
        suma = indifuente.filter(ingreso__a_quien_vendio = i).aggregate(Sum('ingreso__a_quien_vendio'))
        if suma['ingreso__a_quien_vendio__sum']==None:
            suma['ingreso__a_quien_vendio__sum'] = 0
        label = [data[1] for data in QUIEN_CHOICES][i-1]
        resultados.append((label, suma['ingreso__a_quien_vendio__sum']))

    chart = PieChart3D(600,350)
    chart.set_colours([ 'FFBC13','22A410','E6EC23','2B2133','BD0915','3D43BD'])
    chart.add_data([int(data[1]) for data in resultados])
    chart.set_legend([data[0] for data in resultados])
    chart.set_pie_labels([str(data[1])+'%' for data in resultados])
    porcentajes = saca_porcentajes([data[1] for data in resultados])
    chart.set_pie_labels(porcentajes)
    chart.set_legend_position("b")
    chart.set_title(mensaje)

    dict = {'url': chart.get_url()}
    return HttpResponse(simplejson.dumps(dict), mimetype='application/javascript')

@session_required
def grafo_maneja_negocio(request):
    indifuente = filtros_comunes(request)
    mensaje = "Quien maneja los negocios para todas las encuestas"
        
    resultados=[]
    for i in [a[0] for a in DUENO_CHOICES]:
        suma = indifuente.filter(ingreso__quien_maneja_negocio = i).aggregate(conteo_quien = Count('ingreso__quien_maneja_negocio'))
        if suma['conteo_quien']==None:
            suma['conteo_quien'] = 0
        label = i
        resultados.append((label, suma['conteo_quien']))

    chart1 = PieChart3D(600,350)
    chart1.set_colours(['FFBC13','22A410','E6EC23','2B2133','BD0915','3D43BD'])
    chart1.add_data([int(data[1]) for data in resultados])
    chart1.set_legend([data[0] for data in resultados])
    porcentajes = saca_porcentajes([data[1] for data in resultados])
    chart1.set_pie_labels(porcentajes)
    chart1.set_legend_position("b")
    chart1.set_title(mensaje)

    dict = {'url': chart1.get_url()}
    return HttpResponse(simplejson.dumps(dict), mimetype='application/javascript')

# Con quien tiene credito
@session_required
def graph(request):
    indicredito = filtros_comunes(request)
   
    dict = {'casos': indicredito.count()}
    return direct_to_template(request,"encuestas/credito-grafos.html", dict)

@session_required
def grafo_credito(request):
    indicredito = filtros_comunes(request)
    mensaje = "Organizaciones que tienen creditos "
    
    resultados=[]
    for i in range(1, len(CREDITO_CHOICES)+1):
        suma = indicredito.filter(credito__con_que_organizacion_tiene_credito_actualmente = i).aggregate(Sum('credito__con_que_organizacion_tiene_credito_actualmente'))
        if suma['credito__con_que_organizacion_tiene_credito_actualmente__sum']==None:
            suma['credito__con_que_organizacion_tiene_credito_actualmente__sum'] = 0
        label = [data[1] for data in CREDITO_CHOICES][i-1]
        resultados.append((label, suma['credito__con_que_organizacion_tiene_credito_actualmente__sum']))

    graph1 = PieChart3D(600,350)
    graph1.set_colours(['FFBC13','22A410','E6EC23','2B2133','BD0915','3D43BD'])
    graph1.add_data([int(data[1]) for data in resultados])
    graph1.set_legend([data[0] for data in resultados])
    porcentajes = saca_porcentajes([data[1] for data in resultados])
    graph1.set_pie_labels(porcentajes)
    graph1.set_legend_position("b") 
    graph1.set_title(mensaje)

    dict = {'url': graph1.get_url() }
    return HttpResponse(simplejson.dumps(dict), mimetype='application/javascript')

# Uso del credito

@session_required
def grafo_credito_uso(request):
    indicredito = filtros_comunes(request)
    mensaje = "Uso de credito"
    
    resultados=[]
    for i in range(1, len(USO_CHOICES)+1):
        suma = indicredito.filter(credito__uso_del_credito = i).aggregate(Sum('credito__uso_del_credito'))
        if suma['credito__uso_del_credito__sum']==None:
            suma['credito__uso_del_credito__sum'] = 0
        label = [data[1] for data in USO_CHOICES][i-1]
        resultados.append((label, suma['credito__uso_del_credito__sum']))

    graph = PieChart3D(600,350)
    graph.set_colours([ 'FFBC13','22A410','E6EC23','2B2133','BD0915','3D43BD'])
    graph.add_data([int(data[1]) for data in resultados])
    graph.set_legend([data[0] for data in resultados])
    porcentajes = saca_porcentajes([data[1] for data in resultados])
    graph.set_pie_labels(porcentajes)
    graph.set_legend_position("b")
    graph.set_title(mensaje)

    dict = {'url': graph.get_url()}
    return HttpResponse(simplejson.dumps(dict), mimetype='application/javascript')

def saca_porcentajes(values):
    """sumamos los valores y devolvemos una lista con su porcentaje"""
    total = sum(values)
    valores_cero = [] #lista para anotar los indices en los que da cero el porcentaje
    for i in range(len(values)):
        porcentaje = (float(values[i])/total)*100
        values[i] = "%.2f" % porcentaje + '%' 
    return values

#PDF
def write_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(
    html.encode("utf-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    return HttpResponse('Error al procesar pdf %s' % cgi.escape(html))

def write_xls(template_src, context_dict, filename):
    response = render_to_response(template_src, context_dict)
    response['Content-Disposition'] = 'attachment; filename='+filename
    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Charset']='UTF-8'
    return response

#autocomplete
def productor_autocomplete(request):
    def iter_results(results):
        if results:
            for r in results:
                yield '%s|%s\n' % (r.nombre_productor, r.id)
                        
    if not request.GET.get('q'):
        return HttpResponse(mimetype='text/plain')
                                                    
    q = request.GET.get('q')
    limit = request.GET.get('limit', 15)
    try:
        limit = int(limit)
    except ValueError:
        return HttpResponseBadRequest() 

    foos = Finca.objects.filter(nombre_productor__icontains=q)[:limit]
    return HttpResponse(iter_results(foos), mimetype='text/plain')

autocomplete = cache_page(productor_autocomplete, 60 * 60)

@session_required
def tomar_decicion(request):
    inditoma = filtros_comunes(request)
    
    casos=inditoma.count()
    #Totales de participacion en toma de deciones
    mujeres_t=inditoma.filter(tomas_decisiones__quienes=1).count()
    jovenes_t=inditoma.filter(tomas_decisiones__quienes=2).count()
    total_t=mujeres_t + jovenes_t
    #Totales de jovenes entre 14 y 24 años
    total_mujeres=inditoma.filter(educacion__sexo_edad=4).count()
    total_hombres=inditoma.filter(educacion__sexo_edad=3).count()
    total_jovenes=total_mujeres + total_hombres
    #Totales de mujeres adultas por familia
    total_m_adulta=inditoma.filter(educacion__sexo_edad=2).count()
    #Porcentaje de participacion en toma de deciciones
    jovenes_p= (float(jovenes_t)/total_jovenes) * 100 
    mujeres_p=(float(mujeres_t)/total_m_adulta) * 100
    total_p=jovenes_p + mujeres_p
    #Calular las frecuencia de cargos y organizaciones solo para fadcanic
    #organizaciones
    orga_jovenes=inditoma.filter(tomas_decisiones__quienes=2,tomas_decisiones__organizaciones__icontains="fadcanic").count()
    orga_mujeres=inditoma.filter(tomas_decisiones__quienes=1,tomas_decisiones__organizaciones__icontains="fadcanic").count()
    total_orga=orga_jovenes + orga_mujeres
    
    return render_to_response("encuestas/tomar_decision.html",locals())

@session_required
def grafo_desicion(request):
    inditoma = filtros_comunes(request)
    mensaje = "Toma de decisiones "
    
    #Totales de participacion en toma de deciones
    mujeres_t=inditoma.filter(tomas_decisiones__quienes=1).count()
    jovenes_t=inditoma.filter(tomas_decisiones__quienes=2).count()
    total_t=mujeres_t + jovenes_t
    #Totales de jovenes entre 14 y 24 años
    total_mujeres=inditoma.filter(educacion__sexo_edad=4).count()
    total_hombres=inditoma.filter(educacion__sexo_edad=3).count()
    total_jovenes=total_mujeres + total_hombres
    #Totales de mujeres adultas por familia
    total_m_adulta=inditoma.filter(educacion__sexo_edad=2).count()
    #Porcentaje de participacion en toma de deciciones
    jovenes_p= (float(jovenes_t)/total_jovenes) * 100 
    mujeres_p=(float(mujeres_t)/total_m_adulta) * 100
    total_p=jovenes_p + mujeres_p
    #grafo en barra
    chart = GroupedVerticalBarChart(400,300,y_range=(0, total_p))
    chart.set_bar_width(77)
    chart.set_colours(['68660E', '2D6814'])
    chart.add_data([jovenes_p])
    chart.add_data([mujeres_p])
    chart.set_axis_range('y',0,total_p)
    chart.set_legend(['Jovenes','Mujeres'])
    chart.set_legend_position("b")
    chart.set_title('Tomas de decision en %')
    dict = {'url':chart.get_url()}
    return HttpResponse(simplejson.dumps(dict), mimetype='application/javascript')
#    data = [[jovenes_p],[mujeres_p]]
#    legends = ['jovenes', 'mujeres']
#    message = "Participacion en toma de decision"
#    return carlos.make_graph(data, legends, message, multiline=True,
#                            return_json=True, type=GroupedVerticalBarChart)
#*********************************************************************************
def buscar(request):
    indifinca = filtros_comunes(request)
   
    a =[]    
    for encuesta in indifinca.filter(ingreso__fuente_ingreso=25, ingreso__precio_venta__gt=100):
        a.append(encuesta.finca.get().nombre_productor)
                
    return render_to_response("encuestas/buscar.html",{'a':a})
