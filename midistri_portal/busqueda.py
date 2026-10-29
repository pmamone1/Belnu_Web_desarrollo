"""Small Spanish-aware catalogue search, scoped before matching."""
import re
import unicodedata
from difflib import SequenceMatcher

def normalizar(text):
    return ''.join(c for c in unicodedata.normalize('NFKD',text.casefold()) if not unicodedata.combining(c))
def raiz(word):
    if len(word)>5 and word.endswith('es'):return word[:-2]
    return word[:-1] if len(word)>3 and word.endswith('s') else word

def clasificar(product):
    data=product.clasificacion or {}
    return data.get('categorias',[product.categoria] if product.categoria else []),data.get('subcategoria','')

def distancia(a,b,limite):
    if abs(len(a)-len(b))>limite:return limite+1
    prev=list(range(len(b)+1))
    for i,ca in enumerate(a,1):
        row=[i]
        for j,cb in enumerate(b,1):row.append(min(row[-1]+1,prev[j]+1,prev[j-1]+(ca!=cb)))
        if min(row)>limite:return limite+1
        prev=row
    return prev[-1]

def buscar(qs,query):
    from django.db.models import Case,When,Value,IntegerField
    tokens=re.findall(r'[a-z0-9]+',normalizar(query))[:12]
    if not tokens:return qs.none().annotate(_similitud=Value(0,output_field=IntegerField()))
    matches={}
    for product in qs.iterator():
        categories,sub=clasificar(product)
        full=normalizar(' '.join([product.nombre,product.codigo]+categories+[sub]));words=re.findall(r'[a-z0-9]+',full)
        def score(term):
            if term in words:return 100
            if any(w.startswith(term) for w in words):return 80
            if term.isdigit():return 0
            stem=raiz(term)
            if any(stem==raiz(w) for w in words):return 90
            if term in full:return 60
            if len(term)<4 or not term.isalpha():return 0
            limit=1 if len(stem)<6 else 2
            for w in words:
                if not w.isalpha():continue
                word=raiz(w)
                # Prefix comparison also finds a misspelled beginning (koni -> conitos).
                if distancia(stem,word,limit)<=limit or len(word)>len(stem) and distancia(stem,word[:len(stem)],limit)<=limit:return 40
            return 0
        scores=[score(t) for t in tokens]
        if all(scores):
            exact=normalizar(query) in (normalizar(product.nombre),normalizar(product.codigo))
            matches[product.pk]=sum(scores)+(1000 if exact else 0)
    return qs.filter(pk__in=matches).annotate(_similitud=Case(*[When(pk=pk,then=Value(value)) for pk,value in matches.items()],default=Value(0),output_field=IntegerField()))
