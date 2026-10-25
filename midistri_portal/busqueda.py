"""Small Spanish-aware catalogue search, scoped before matching."""
import re
import unicodedata
from difflib import SequenceMatcher

def normalizar(text):
    return ''.join(c for c in unicodedata.normalize('NFKD',text.casefold()) if not unicodedata.combining(c))
def raiz(word):
    if len(word)>5 and word.endswith('es'):return word[:-2]
    return word[:-1] if len(word)>3 and word.endswith('s') else word

def buscar(qs,query):
    tokens=re.findall(r'[a-z0-9]+',normalizar(query))[:12]
    if not tokens:return qs.none()
    matches=[]
    for pk,nombre,codigo,categoria in qs.values_list('pk','nombre','codigo','categoria').iterator():
        full=normalizar(' '.join((nombre,codigo,categoria)));words=re.findall(r'[a-z0-9]+',full)
        def hit(term):
            stem=raiz(term)
            return term in full or any(stem==raiz(w) or len(term)>=4 and abs(len(term)-len(w))<=2 and SequenceMatcher(None,term,w).ratio()>=.82 for w in words)
        if all(hit(term) for term in tokens):matches.append(pk)
    return qs.filter(pk__in=matches)
