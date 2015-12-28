from managers import *

def count_all_test(ano = 2009, saf=2):
    manager = SafManager()
    return manager.count_all(ano, saf)

def count_by_encuesta_test(saf=2, enc=120):
    manager = SafManager()
    return manager.count_by_encuesta(saf, enc)

def count_by_municipio_test(ano = 2009, saf=2, mun=3):
    manager = SafManager()
    return manager.count_by_municipio(ano, saf, mun)

def count_by_departamento_test(ano=2009, saf=2, dept=3):
    manager = SafManager()
    return manager.count_by_departamento(ano, saf, dept)

def run_all_saf():
    print "haciendo todos los test de saf"
    print "count_all()"
    print count_all_test()
    print "count_by_encuesta_test()"
    print count_by_encuesta_test()
    print "count_by_municipio_test()"
    print count_by_municipio_test()
    print "count_by_departamento_test()"
    print count_by_departamento_test()
    print "Seguridad: count_by_encuesta_seguridad_test()"
    print count_by_encuesta_seguridad_test()

def count_by_encuesta_seguridad_test(alimento=2, id_encuesta=24):
    manager = SeguridadAlimentariaManager()
    return manager.count_by_encuesta(alimento, id_encuesta)

def count_by_encuesta_educacion_test(id_sexo = 1, id_encuesta=24):
    manager = EducacionManager()
    return manager.count_by_encuesta(id_sexo, id_encuesta)
