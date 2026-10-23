"""Validate metadata only. Never fetch a received media URL."""
from urllib.parse import urlsplit
from uuid import UUID
import re

VIDEO_HOSTS={'youtube.com','www.youtube.com','m.youtube.com','youtu.be','vimeo.com','www.vimeo.com','player.vimeo.com'}

def validar_multimedia(items,origen_urban):
    if not isinstance(items,list) or len(items)>30:raise ValueError('Multimedia inválida.')
    base=urlsplit(origen_urban);seen=set();clean=[];counts={'foto':0,'video':0}
    for i in items:
        try:
            if not isinstance(i,dict):raise ValueError
            ident=str(UUID(i['id']));tipo=i['tipo'];url=i['url'];description=i.get('descripcion','')
            if tipo not in ('foto','mp4','youtube','vimeo') or not isinstance(url,str) or len(url)>500:raise ValueError
            if not isinstance(description,str) or len(description)>300:raise ValueError
            order=i.get('orden',0);principal=i.get('principal',False)
            if type(order) is not int or not 0<=order<=2147483647 or type(principal) is not bool:raise ValueError
            if tipo!='foto' and principal:raise ValueError
            u=urlsplit(url)
            if u.scheme!='https' or u.username is not None or u.password is not None or u.port not in (None,443):raise ValueError
            if tipo in ('foto','mp4'):
                if u.netloc!=base.netloc or u.query or u.fragment:raise ValueError
                uuid_pattern=r'[0-9a-fA-F-]{36}'
                pattern=(r'/catalogo-imagenes/'+uuid_pattern+r'/[0-9a-f]{64}/') if tipo=='foto' else (r'/midistri-media/'+uuid_pattern+r'/')
                if not re.fullmatch(pattern,u.path):raise ValueError
                UUID(u.path.split('/')[2])
            else:
                if u.hostname not in VIDEO_HOSTS:raise ValueError
                if tipo=='youtube' and 'youtu' not in u.hostname:raise ValueError
                if tipo=='vimeo' and 'vimeo' not in u.hostname:raise ValueError
                if any(ord(c)<32 for c in url):raise ValueError
            key=(tipo,ident)
            if key in seen:continue
            seen.add(key);count='foto' if tipo=='foto' else 'video';counts[count]+=1
            if counts[count]>(20 if count=='foto' else 10):raise ValueError
            clean.append(dict(id=ident,tipo=tipo,url=url,descripcion=description,orden=order,principal=principal))
        except (ValueError,TypeError,KeyError,AttributeError):
            raise ValueError('Material público inválido; se conserva el catálogo anterior.') from None
    return sorted(clean,key=lambda x:(x['tipo']!='foto',not x['principal'],x['orden'],x['id']))
