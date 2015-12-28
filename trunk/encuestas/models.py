 # -*- coding: UTF-8 -*-
#from managers import * 
from django.db import models
from django.conf import settings
from thumbs import ImageWithThumbsField
from lugar.models import Comunidad
import datetime
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Recolector(models.Model):
	nombre = models.CharField(max_length=100)

        def __unicode__(self):
                return self.nombre

ANO_ENCUESTA=((2009,"2009"),(2010,"2010"),(2011,"2011"),(2012,"2012"),(2013,"2013"),(2014,"2014"))


TIPO_CHOICES=((1,'Casa de madera rolliza con techo de paja'),(2,'Casa de madera y techo de paja'),(3,'Casa de madera con techo de zinc'),(4,'Casa minifalda con techo de zinc'),(5,'Casa de concreto con techo de zinc'))
AGUA_CHOICES=((1,'Ojo de agua'),(2,'Creeke'),(3,'Pozo con brocal'),(4,'Agua entubada'),(5,'Pozo rustico'),(6,'Agua por gravedad'),(7,'Otros'),(8,'Agua central certificado'),(9,'Pozo rustico sin manejo'))
LEGALIDAD_CHOICES=((1,'Derecho real'),(2,'Derecho procesorio'),(3,'Promesa de venta'),(4,'Titulo de reforma agraria'),(5,'Titulo comunitario'),(6,'Sin documentos'),(7,'Escritura publica'))

DUENO_CHOICES=(('hombre','Hombre'),('mujer','Mujer'),('ambos','Ambos'),('parientes','Parientes'))
SEXO_PRODUCTOR_CHOICES=((1,'Mujer'),(3,'Hombre'))

class Finca(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()
	finca = models.CharField("Nombre Finca",max_length=50,null=True,blank=True,help_text='Introduzca nombre de la finca')
	comunidad = models.ForeignKey(Comunidad,help_text='Introduzca nombre de la comunidad')
	coordenadas_gps = models.DecimalField('Coordenadas Latitud',max_digits=8, decimal_places=6 ,null=True,blank=True,help_text='Introduzca las coordenadas Latitud')
	coordenadas_lg = models.DecimalField('Coordenadas Longitud', max_digits=8, decimal_places=6, null=True, blank=True, help_text="Introduzca las coordenadas Longitud")
	nombre_productor = models.CharField(max_length=100,help_text='Introduzca nombre del productor')
	sexo = models.IntegerField('Sexo del productor', choices=SEXO_PRODUCTOR_CHOICES, null = True, blank=True)
	cedula_productor = models.CharField(max_length=25,null=True,blank=True,help_text='Introduzca cedula del productor')
	area_finca = models.DecimalField(max_digits=10,decimal_places=2,help_text='Introduzca el area de la finca en MZ')
	animal_bovino = models.IntegerField(help_text='Introduzca cuantos animales bovinos tiene')
	animal_porcino = models.IntegerField(help_text='Introduzca cuantos animales porcinos tiene')
	animal_equino = models.IntegerField(help_text='Introduzca cuantos animales equinos tiene')
	animal_aves = models.IntegerField(help_text='Introduzca cuantas aves tiene')
	animal_caprino = models.IntegerField(help_text='Introduzca cuantos animales caprino o pelibuey tiene')
	tipo_casa = models.IntegerField(max_length=60,choices=TIPO_CHOICES,help_text='Introduzca que tipo de casa tiene')
	area_casa = models.DecimalField(max_digits=10,decimal_places=2,help_text='Introduzca area de la casa en pie cuadrado')
	fuente_agua = models.IntegerField(max_length=60,choices=AGUA_CHOICES,help_text='Introduzca que fuente de agua tiene')
	legalidad = models.IntegerField(max_length=60,choices=LEGALIDAD_CHOICES, help_text='Introduzca la legalidad de la propiedad')
	propietario = models.CharField(max_length=50,choices=DUENO_CHOICES,help_text='Introduzca el propietario de la finca')
	recolector = models.ForeignKey(Recolector)
	repetido = models.BooleanField(blank=True)

	class Meta:
		ordering = ['finca']
		verbose_name_plural = "Finca"

	def __unicode__(self):
		return self.finca

SEXO_CHOICES=((1,'Hombre adultos de 25 adelante'),(2,'Mujeres adultas de 25 adelante'),(3,'Hombres Jovenes de 15 a 24'),(4,'Mujeres Jóvenes de 15 a 24'),(5,'Hombres adolescentes de 9 a 14'),(6,'Mujeres adolescentes de 9 a 14'),(7,'Hombres ninos de 1 a 8'),(8,'Mujeres ninas de 1 a 8'))

class Educacion(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()
	sexo_edad = models.IntegerField(choices=SEXO_CHOICES)
	num_persona = models.IntegerField()
	nosabe_leer = models.IntegerField()
	pri_incompleta = models.IntegerField()
	pri_completa = models.IntegerField()
	secu_incompleta = models.IntegerField()
	secu_completa = models.IntegerField()
	uni_o_tecnico = models.IntegerField()
	estudiando = models.IntegerField()
	circ_estudio_adulto = models.IntegerField()
    

	class Meta:
		ordering = ['sexo_edad']
		verbose_name_plural = "Indicador de Educacion"


class Boscosa(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()
	area_total = models.DecimalField(max_digits=10,decimal_places=2)
	bosque_primario = models.DecimalField(max_digits=10,decimal_places=2)
	bosque_secundario = models.DecimalField(max_digits=10,decimal_places=2)
	bosque_galeria = models.DecimalField(max_digits=10,decimal_places=2)
	humedales = models.DecimalField(max_digits=10,decimal_places=2)
	tacotal =  models.DecimalField(max_digits=10,decimal_places=2)
	cultivos_perennes = models.DecimalField(max_digits=10,decimal_places=2)
	cultivos_semiperennes = models.DecimalField(max_digits=10,decimal_places=2)
	cultivos_anuales = models.DecimalField(max_digits=10,decimal_places=2)
	huerto_mixto = models.DecimalField(max_digits=10,decimal_places=2)
	potrero_abierto = models.DecimalField(max_digits=10,decimal_places=2)
	potrero_arboles = models.DecimalField(max_digits=10,decimal_places=2)
	cerca_viva = models.DecimalField(max_digits=10,decimal_places=2)
	cerca_muerta = models.DecimalField(max_digits=10,decimal_places=2)
	plantaciones_forestales = models.DecimalField(max_digits=10,decimal_places=2)
	parcela_energetica = models.DecimalField(max_digits=10,decimal_places=2)
	
	class Meta:
                verbose_name_plural = "Indicador de aumento de cobertura boscosa en MZ"
	

SISTEMAS_CHOICES=((1,'Cafe bajo sombra'),(2,'Cacao bajo sombra'),(3,'Parcela energetica'),(4,'Parcela silvopastoril'),(5,'Cerca Viva'),(6,'Huerto mixto'),(7,'Parcela forrajera'),(8,'Parcela frutales'),(9,'Cultivos Anuales con Arboles'),(10,'Cultivo callejon'),(11,'Parcela agroforestal succecional'),(12,'Achiote con sombra'),(13,'Parcela de coco'),(14,'Parcela de pejibaye'),(15,'Parcela con raices'),(16,'Tuberculos'))

class Saf(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()
	sis_agroforestal = models.IntegerField(choices=SISTEMAS_CHOICES)
	area_en_desarrollo = models.DecimalField(max_digits=10,decimal_places=2)
	area_en_produccion = models.DecimalField(max_digits=10,decimal_places=2)
	area_mal_manejo = models.DecimalField(max_digits=10,decimal_places=2)
	area_manejo_regular = models.DecimalField(max_digits=10,decimal_places=2)
	area_buen_manejo = models.DecimalField(max_digits=10,decimal_places=2)
	class Meta:
		verbose_name_plural = "Indicadores de aumento de area SAF y mejora de manejo de SAF en MZ"

PRODUCTO_CHOICES=(
	(1,'Cafe'),
	(2,'Cacao'),
	(3,'Coco'),
	(4,'Lena'),
	(5,'Guineo'),
	(6,'Platano'),
	(7,'Madera'),
	(8,'Naranja'),
	(9,'Aguacate'),
	(10,'Pejibaye'),
	(11,'Achiote'),
	(12,'Guanabana'),
	(13,'Canela'),
	(14,'Limon'),
	(15,'Guabo'),
	(16,'Mamon chino'),
	(17,'Fruta de pan'),
	(18,'Castano'),
	(19,'Pina'),
	(20,'Naranjilla'),
	(21,'Mandarina'),
	(22,'Crema'),
	(23,'Mango')
	)

UNIDAD_COMER_CHOICES=(
	(1,'qq pergaminos'),
	(2,'qq'),
	(3,'Unidad'),
	(4,'Cienes'),
	(5,'Pie tablar'),
	(6,'Docenas'),
	(7,'Racimo'),
	(8,'Lbs'),
	(9,'Carga'),
	(10,'Cabezas'))

class ProducComerPrecio(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()
	prod_agroforestales = models.IntegerField(max_length=60,help_text='Introducir producto',choices=PRODUCTO_CHOICES)
	area_cosecha_MZ = models.DecimalField(max_digits=10,decimal_places=2)
	prod_total_anual = models.DecimalField(max_digits=10,decimal_places=2)
	unidad_medida = models.IntegerField(choices=UNIDAD_COMER_CHOICES)
	auto_consumo = models.DecimalField(max_digits=10,decimal_places=2)
	cant_venta_no_organizada = models.DecimalField(max_digits=10,decimal_places=2)
	precio_venta_no_organizada = models.DecimalField(max_digits=10,decimal_places=2)
	cant_venta_organizada = models.DecimalField(max_digits=10,decimal_places=2)
	precio_venta_organizada = models.DecimalField(max_digits=10,decimal_places=2)

	class Meta:
		verbose_name_plural = "Indicador de produccion, comercializacion y precio"
	
QUIEN_CHOICES=((1,'Intermediario'),(2,'Comunidad'),(3,'Mercado'),(4,'Org. Campesina'),(5,'Cooperativa'),(6,'Consumidor'))

FUENTE_CHOICES=(
	(1,'Venta Maiz'),
	(2,'Venta Frijol'),
	(3,'Venta Arroz'),
	(4,'Venta Yuca'),
	(5,'Venta Malanga'),
	(6,'Venta Quequisque'),
	(7,'Venta Naranjilla'),
	(8,'Venta de Maracuya'),
	(9,'Venta de cafe'),
	(10,'Venta de cacao'),
	(11,'Venta de coco'),
	(12,'Venta lena'),
	(13,'Venta Guineo'),
	(14,'Venta platano'),
	(15,'Venta madera'),
	(16,'Venta Naranja'),
	(17,'Venta aguacate'),
	(18,'Venta pejibaye'),
	(19,'Venta achiote'),
	(20,'Venta leche'),
	(21,'Venta cuajada'),
	(22,'Venta queso'),
	(23,'Venta de bovinos'),
	(24,'Venta de huevos'),
	(25,'Venta gallina'),
	(26,'Venta de pescado'),
	(27,'Venta de marisco'),
	(28,'Venta de cerdo'),
	(29,'Venta mandarina'),
	(30,'Venta piña'),
	(31,'Venta canela'),
	(32,'Venta Granadilla'),
	(33,'Venta Carne'),
	(34,'Venta guanabana'),
	(35,'Venta hortalizas'),
	(36,'Servicio de Transporte'),
	(37,'Venta de mano de obra'),
	(38,'Ingreso por salario'),
	(39,'Remesas'),
	(40,'Ingreso por negocio'),
	(41,'Venta Mango'),
	(42,'Venta de limones'),
	(43,'Venta de Fruta de Pan'),)

UNIDAD_INGRE_CHOICES=(
	(1,'qq pergaminos'),
	(2,'qq'),
	(3,'qq granza'),
	(4,'Unidad'),
	(5,'Cienes'),
	(6,'Pie tablar'),
	(7,'Docenas'),
	(8,'Racimo'),
	(9,'Libras'),
	(10,'Carga'),
	(11,'Litros'),
	(12,'Cabezas'),
	(13,'C$'),
	(14,'Mes'),
	(15,'saco')
	)
class Ingreso(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()
	fuente_ingreso = models.IntegerField(choices=FUENTE_CHOICES)
	unidad = models.IntegerField(choices=UNIDAD_INGRE_CHOICES)
	cantidad_vendida = models.DecimalField(max_digits=10,decimal_places=2)
	precio_venta = models.DecimalField(max_digits=10,decimal_places=2)
	ingreso_venta = models.DecimalField(max_digits=10,decimal_places=2)
	a_quien_vendio = models.IntegerField(choices=QUIEN_CHOICES)
	quien_maneja_negocio = models.CharField(max_length=50, choices=DUENO_CHOICES)

	class Meta:
		verbose_name_plural = "Indicador de aumento de ingreso familiar"
		
ALIMENTO_CHOICES=((1,'Agua'),(2,'Maiz'),(3,'Frijol'),(4,'Arroz'),(5,'Azucar'),(6,'Yuca'),(7,'Malanga'),(8,'Quequisque'),(9,'Naranjilla'),(10,'Parras'),(11,'Cafe'),(12,'Cacao'),(13,'Coco'),(14,'Leña'),(15,'Guineo'),(16,'Platano'),(17,'Madera'),(18,'Naranja'),(19,'Aguacate'),(20,'Pejibaye'),(21,'Achiote'),(22,'Leche'),(23,'Cuajada'),(24,'Queso'),(25,'Crema'),(26,'Carne de Res'),(27,'Huevos'),(28,'Gallinas'),(29,'Carne de Cerdo'),(30,'Pinolillo'),(31,'Avena'),(32,'Pescado'),(33,'Pan'),(34,'Aceite'),(35,'Manteca'),(36,'Papa'),(37,'Cebolla'),(38,'Chiltoma'),(39,'Tomate'))


CONSUMO_CHOICES=((1,'No suficiente'),(2,'Si suficiente'))

class SeguridadAlimentaria(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()
	alimentos = models.IntegerField(choices=ALIMENTO_CHOICES)
	producen = models.BooleanField()
	comprar = models.BooleanField()
	nivel_consumo_suficiente = models.IntegerField(choices=CONSUMO_CHOICES)

	class Meta:
		verbose_name_plural = "Indicador para Seguridad alimentaria" 

USO_CHOICES=((1,'Pecuario'),(2,'Agricultura'),(3,'Infraestructura'),(4,'Comercio'),(5,'Equipos y herramientas'))
CREDITO_CHOICES=((1,'Fadcanic'),(2,'Addac'),(3,'The Kukras'),(4,'Bancentro'),(5,'Banpro'),(6,'Caruna'),(7,'Prodesa'),(8,'Banex'),(9,'Procredit'),(10,'FDL'),(11,'Fundeser'),(12,'Nieborowsky'),(13, 'APPDR'), (14, 'AFODENIC'))
class Credito(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()
	con_que_organizacion_tiene_credito_actualmente = models.IntegerField(choices=CREDITO_CHOICES)
	uso_del_credito = models.IntegerField(choices=USO_CHOICES)
	desde_cuando_se_benefician_de_esta_fuente = models.DateField()
	no_personas_beneficiarias_de_la_familia = models.IntegerField()

	class Meta:
		verbose_name_plural = "Indicador de credito"

''' por aqui falta la lista
'''
QUIENES_CHOICES=((1,'Mujeres de la familia'),(2,'Jovenes de la familia'))

class TomasDeciciones(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()
	quienes = models.IntegerField(choices=QUIENES_CHOICES)
	nombre = models.CharField(max_length=100)
	cargo = models.CharField(max_length=100)
	organizaciones = models.CharField(max_length=60)
	desde_cuando = models.DateField()

	class Meta:
		verbose_name_plural = "Indicador de participacion en estructuras de toma de decisiones"

class ConoJoRassMata(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()
	jovenes = models.CharField(max_length=60)
	resp_correcta = models.IntegerField()

	class Meta:
		verbose_name_plural = "Indicador de conocimiento de los jovenes sobre los sistemas de tropico humedo RAAS y Matagalpa"

	def __unicode__(self):
		return self.jovenes

class Fotos(models.Model):
	content_type = models.ForeignKey(ContentType)
	object_id = models.IntegerField(db_index=True)
	content_object = generic.GenericForeignKey()
	nombre = models.CharField(max_length=200,help_text="Nombre de la foto a subir")
	adjunto = ImageWithThumbsField(upload_to="attachments",blank=True,help_text="Suba su archivo aqui",sizes=((125,125),(200,200)))

	def get_absolute_url(self):
		return '%s%s/%s' % (settings.MEDIA_URL,settings.ATTACHMENT_FOLDER, self.id)

	def get_download_url(self):
		return '%s%s/%s' % (settings.MEDIA_URL,settings.ATTACHMENT_FOLDER, self.nombre)

	class Meta:
		verbose_name_plural = "Subir archivos fotograficos de las familias de las fincas"
	def __unicode__(self):
		return self.nombre

class Encuesta(models.Model):
	fecha = models.DateField(help_text='Introduzca año-mes-dia')
	ano = models.IntegerField(choices=ANO_ENCUESTA,help_text="Introduzca el año de levantado de la encuesta")
	finca = generic.GenericRelation(Finca)
	educacion = generic.GenericRelation(Educacion)
	boscosa = generic.GenericRelation(Boscosa)
	saf = generic.GenericRelation(Saf)
	produc_comer_precio = generic.GenericRelation(ProducComerPrecio)
	ingreso = generic.GenericRelation(Ingreso)
	seguridad_alimentaria = generic.GenericRelation(SeguridadAlimentaria)
	credito = generic.GenericRelation(Credito)
	tomas_decisiones = generic.GenericRelation(TomasDeciciones)
	cono_jo_rass_mata = generic.GenericRelation(ConoJoRassMata)
	foto = generic.GenericRelation(Fotos)

	class Meta:
		verbose_name_plural = "Encuestas"

	def fincas(self):
		return self.finca.all()[0].finca
	def productores(self):
		return self.finca.all()[0].nombre_productor
	def comunidades(self):
		return self.finca.all()[0].comunidad
	def municipios(self):
		return self.finca.all()[0].comunidad.municipio
	def departamentos(self):
		return self.finca.all()[0].comunidad.municipio.departamento
	def propietarios(self):
		return self.finca.all()[0].get_propietario_display()

