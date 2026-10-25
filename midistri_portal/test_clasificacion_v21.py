from copy import deepcopy
from django.test import TestCase
from .models import Distribuidora,Publicacion
from .services import validar_snapshot,aplicar_snapshot

class ClasificacionTests(TestCase):
    def data(self):
        return {'version':1,'completo':True,'distribuidoras':[{'id':20,'nombre':'QA'}],'publicaciones':[{'producto_id':1,'distribuidora_id':20,'nombre':'Alma de Campeon','codigo':'123456','categoria':'Alimentos','clasificacion':{'categorias':['Alimentos','Golosinas'],'subcategoria':'Alfajores'},'precio':'10.00','pvp':'20.00','imagenes':[{'url':'https://urban.example/catalogo-imagenes/qa'}]}]}
    def test_contrato_nuevo_y_anterior(self):
        from django.test import override_settings
        with override_settings(URBAN_API_BASE='https://urban.example/api'):
            d=self.data();aplicar_snapshot(d)
            self.assertEqual(Publicacion.objects.get().clasificacion,d['publicaciones'][0]['clasificacion'])
            del d['publicaciones'][0]['clasificacion'];aplicar_snapshot(d)
            self.assertEqual(Publicacion.objects.get().clasificacion,{'categorias':['Alimentos'],'subcategoria':''})
    def test_clasificacion_invalida_conserva_copia(self):
        from django.test import override_settings
        with override_settings(URBAN_API_BASE='https://urban.example/api'):
            d=self.data();aplicar_snapshot(d)
            for bad in ({'categorias':['Alimentos'],'subcategoria':'','costo':1},{'categorias':'Golosinas','subcategoria':''},{'categorias':['Alimentos','Alimentos'],'subcategoria':''},{'categorias':['Golosinas'],'subcategoria':''},{'categorias':['Alimentos'],'subcategoria':True}):
                dd=deepcopy(d);dd['publicaciones'][0]['clasificacion']=bad
                with self.assertRaises(ValueError):aplicar_snapshot(dd)
                self.assertEqual(Publicacion.objects.get().clasificacion,d['publicaciones'][0]['clasificacion'])
    def test_busqueda_y_filtro_no_mezclan_tiendas(self):
        d=Distribuidora.objects.create(pk=20,nombre='QA');other=Distribuidora.objects.create(pk=61,nombre='Otra QA')
        args=dict(nombre='Alma de Campeon',codigo='123456',categoria='Alimentos',clasificacion={'categorias':['Alimentos','Golosinas'],'subcategoria':'Alfajores'},precio=10,pvp=20,imagenes=['https://example.test/a.jpg'])
        p=Publicacion.objects.create(distribuidora=d,producto_id=1,**args);Publicacion.objects.create(distribuidora=other,producto_id=2,**dict(args,nombre='Ajeno'))
        for params in ({'q':'alfajor'},{'q':'alfajro'},{'q':'golosinas'},{'categoria':'Golosinas'},{'q':'alma campeom'}):
            r=self.client.get('/portal/',dict(params,distribuidora=20));self.assertEqual([x.pk for x in r.context['productos']],[p.pk]);self.assertNotContains(r,'Ajeno')
        self.assertContains(r,'Golosinas');self.assertContains(r,'Alfajores')
        r=self.client.get('/portal/',{'distribuidora':20,'q':'123457','categoria':''});self.assertEqual(len(r.context['productos']),0)
