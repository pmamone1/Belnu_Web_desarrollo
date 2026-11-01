from random import Random
from types import SimpleNamespace as NS
from django.test import TestCase,SimpleTestCase,override_settings
from .models import Distribuidora,Publicacion

class OrdenSesionTests(SimpleTestCase):
    def products(self):return [NS(pk=i,indicadores={'orden_ventas':i} if i<12 else {}) for i in range(1,45)]
    def test_mezcla_sin_duplicados_y_conserva_sin_ventas(self):
        from .catalogo_rotacion import ordenar_mezcla
        result=ordenar_mezcla(self.products(),Random(1))
        self.assertEqual({p.pk for p in result},set(range(1,45)))
        self.assertEqual(len(result),44)
        self.assertNotEqual([p.pk for p in result],list(range(1,45)))
        self.assertTrue(any(p.pk>11 for p in result[:6]))
    def test_orden_congelado_no_incluye_altas_nuevas(self):
        from .catalogo_rotacion import orden_sesion
        request=NS(session={});products=self.products()
        first=orden_sesion(request,20,products,rng=Random(1))
        self.assertEqual(orden_sesion(request,20,products[::-1]+[NS(pk=99,indicadores={})],rng=Random(9)),first)
        other=orden_sesion(NS(session={}),20,products,rng=Random(9));self.assertNotEqual(first,other)
    def test_pestanas_y_perfiles_aislados(self):
        from .catalogo_rotacion import orden_sesion
        from .sesion_pestana import TabSession
        original={};a=NS(datos={});b=NS(datos={})
        r1=NS(session=TabSession(original,a));r2=NS(session=TabSession(original,b))
        x=orden_sesion(r1,20,self.products(),perfil={'id':1},rng=Random(1))
        y=orden_sesion(r2,20,self.products(),perfil={'id':2},rng=Random(9))
        self.assertNotEqual(x,y);self.assertNotIn('midistri_catalogo_orden',original)
        self.assertEqual(orden_sesion(r1,20,self.products(),perfil={'id':1},rng=Random(9)),x)

class CatalogoRotacionTests(TestCase):
    def setUp(self):
        self.d=Distribuidora.objects.create(pk=20,nombre='QA')
        self.other=Distribuidora.objects.create(pk=61,nombre='Otra')
        for i in range(1,55):
            Publicacion.objects.create(distribuidora=self.d,producto_id=i,nombre='Producto %02d'%i,codigo='S'+str(i),categoria='Alimentos',
                clasificacion={'categorias':['Alimentos'],'subcategoria':'Alfajores' if i%2 else 'Bebidas'},precio=10,pvp=20,
                imagenes=['https://example.test/p.jpg'],indicadores={'orden_ventas':i} if i<12 else {})
        Publicacion.objects.create(distribuidora=self.other,producto_id=100,nombre='Ajeno',categoria='Juguetes',clasificacion={'categorias':['Juguetes'],'subcategoria':'Muñecas'},precio=10,pvp=20,imagenes=['https://example.test/a.jpg'])
    def get(self,**kw):return self.client.get('/portal/',dict(distribuidora=20,**kw))
    def test_default_recomendados_paginado_estable_y_sin_repetir(self):
        a=self.get();b=self.get(page=2);c=self.get()
        self.assertEqual(a.context['orden'],'recomendados')
        ids=lambda r:[p.pk for p in r.context['productos']]
        self.assertEqual(ids(a),ids(c));self.assertFalse(set(ids(a))&set(ids(b)))
        self.assertEqual(a.context['productos'].paginator.count,54)
    def test_filtro_subcategoria_y_url_conservada(self):
        r=self.get(categoria='Alimentos',subcategoria='Alfajores',page_size=24)
        self.assertEqual(r.context['productos'].paginator.count,27)
        self.assertContains(r,'name="subcategoria"');self.assertContains(r,'subcategoria=Alfajores')
        self.assertNotContains(r,'Muñecas');self.assertTrue(all(p.clasificacion['subcategoria']=='Alfajores' for p in r.context['productos']))
    def test_baja_publicacion_se_oculta_y_precio_sigue_actual(self):
        a=self.get();pub=a.context['productos'][0];pub.activa=False;pub.save()
        other=a.context['productos'][1];other.precio=19;other.save()
        b=self.get();self.assertNotIn(pub.pk,[p.pk for p in b.context['productos']])
        self.assertEqual(next(p.precio for p in b.context['productos'] if p.pk==other.pk),19)
    def test_nueva_publicacion_espera_proxima_sesion(self):
        self.get();p=Publicacion.objects.create(distribuidora=self.d,producto_id=999,nombre='Nuevo',precio=1,pvp=2,imagenes=['https://example.test/n.jpg'])
        a=self.get();self.assertEqual(a.context['productos'].paginator.count,54)
        self.assertNotIn(p.pk,[x.pk for x in a.context['productos']])
    def test_busqueda_exacta_tiene_prioridad(self):
        r=self.get(q='Producto 54');self.assertEqual(r.context['productos'][0].nombre,'Producto 54')
    @override_settings(MIDISTRI_LOGIN_CODIGO_ENABLED=True,MIDISTRI_ACCESO_RECORDADO_ENABLED=True)
    def test_acceso_continuar_y_sin_instruccion_de_salida(self):
        r=self.client.get('/portal/acceso/')
        self.assertContains(r,'<button>Continuar</button>',html=True)
        self.assertNotContains(r,'Recibir código');self.assertNotContains(r,'Salir y olvidar')
