from copy import deepcopy
from random import Random
from django.core.exceptions import ValidationError
from django.test import TestCase,override_settings
from .models import Distribuidora,Tienda,Publicacion
from . import pagina as p

@override_settings(MIDISTRI_MULTIMEDIA_ENABLED=True)
class BannerAutomaticoTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(pk=20,nombre='QA');self.t=Tienda.objects.create(distribuidora=self.d)
        self.other=Distribuidora.objects.create(pk=61,nombre='Otra')
        self.items=[]
        for i in range(1,10):self.items.append(Publicacion.objects.create(distribuidora=self.d,producto_id=i,nombre='P'+str(i),precio=10,pvp=20,imagenes=['https://example.test/'+str(i)+'.jpg']))
        Publicacion.objects.create(distribuidora=self.other,producto_id=99,nombre='Ajeno',precio=10,pvp=20,imagenes=['https://example.test/otro.jpg'])
        self.block={'id':'promo','tipo':'banner','activo':True,'origen':'catalogo_aleatorio','cantidad':6,'diapositivas':[]}
    def test_automatico_fijo_por_sesion_sin_ajenos_ni_repetidos(self):
        from .banners_automaticos import slides_automaticos
        session={};a=slides_automaticos(self.block,20,session,rng=Random(1));b=slides_automaticos(self.block,20,session,rng=Random(9))
        self.assertEqual([x['publicacion'] for x in a],[x['publicacion'] for x in b]);self.assertEqual(len(a),6)
        self.assertEqual(len({x['publicacion'] for x in a}),6);self.assertTrue(all(x['producto'].distribuidora_id==20 for x in a))
    def test_retirado_y_sin_foto_o_precios_no_se_muestran(self):
        from .banners_automaticos import slides_automaticos
        session={};a=slides_automaticos(self.block,20,session,rng=Random(1))
        for row in a:Publicacion.objects.filter(pk=row['publicacion']).update(activa=False)
        self.assertEqual(slides_automaticos(self.block,20,session),[])
        Publicacion.objects.filter(distribuidora=self.d).update(imagenes=[],multimedia=[])
        self.assertEqual(slides_automaticos(self.block,20,{}),[])
    def test_preview_no_modifica_la_sesion_publica(self):
        from .banners_automaticos import slides_automaticos
        session={};slides_automaticos(self.block,20,session,preview=True)
        self.assertEqual(session,{})
    def test_validacion_y_bloque_publico_con_slides_generadas(self):
        data=p.inicial(self.t);data['bloques'].insert(0,self.block)
        clean=p.validar_pagina(data,20)
        self.assertEqual(clean['bloques'][0]['origen'],'catalogo_aleatorio')
        result=p.bloques_vigentes(clean,20,session={})
        self.assertEqual(len(result[0]['diapositivas']),6)
        for bad in [0,21,True,'6']:
            altered=deepcopy(data);altered['bloques'][0]['cantidad']=bad
            with self.assertRaises(ValidationError):p.validar_pagina(altered,20)
        altered=deepcopy(data);altered['bloques'][0]['tipo']='texto'
        with self.assertRaises(ValidationError):p.validar_pagina(altered,20)
    def test_manual_sigue_igual_y_automatico_vacio_se_oculta(self):
        s={'tipo':'foto','url':self.items[0].imagenes[0],'publicacion':self.items[0].pk}
        block=dict(self.block,origen='manual',diapositivas=[s])
        data=p.inicial(self.t);data['bloques'].insert(0,block)
        result=p.bloques_vigentes(p.validar_pagina(data,20),20)
        self.assertEqual(result[0]['diapositivas'][0]['publicacion'],self.items[0].pk)
        data['bloques'][0]=self.block;Publicacion.objects.filter(distribuidora=self.d).update(activa=False)
        self.assertNotIn('promo',[b['id'] for b in p.bloques_vigentes(p.validar_pagina(data,20),20,session={})])
