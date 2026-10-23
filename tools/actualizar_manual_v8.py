"""Prepend current guidance while preserving every prior PDF page."""
from pathlib import Path
from io import BytesIO
import subprocess
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph,SimpleDocTemplate,Spacer,PageBreak
from pypdf import PdfReader,PdfWriter
ROOT=Path(__file__).resolve().parents[1]
BASE='e6453191fff892e8d8d7dfa39c0881c5374ecb2b'
MANUAL='Manual_MiDistri_Pedidos_Online.pdf'
GUIDE='docs/FOTOS_PRESENTACION_v8.md'
TITLE='MiDistri-Pedidos v8'
def main():
    styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=11;styles['BodyText'].leading=15
    styles['BodyText'].spaceAfter=9
    text=(ROOT/GUIDE).read_text(encoding='utf-8').split('## Guía de uso')[1].split('## Implementación')[0].strip().splitlines()
    story=[Paragraph(TITLE+' - Guía actual',styles['Title']),
        Paragraph('Este capítulo prevalece sobre los textos y temas de versiones anteriores. Fotos en carrito y detalle, con los precios históricos conservados. Instalación v8 productiva pendiente. La campaña no se envía.',styles['BodyText']),Spacer(1,4*mm)]
    for index,line in enumerate(text):
        story.append(Paragraph(escape(line),styles['BodyText']))
    chapter=BytesIO()
    SimpleDocTemplate(chapter,pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=16*mm,bottomMargin=16*mm).build(story)
    oldbytes=subprocess.check_output(['git','-c','core.fsmonitor=false','show',BASE+':'+MANUAL],cwd=str(ROOT))
    new=PdfReader(BytesIO(chapter.getvalue()));old=PdfReader(BytesIO(oldbytes))
    assert len(new.pages)==1,'El capítulo debe tener una página'
    writer=PdfWriter();writer.append(BytesIO(chapter.getvalue()));writer.append(BytesIO(oldbytes))
    with (ROOT/MANUAL).open('wb') as f:writer.write(f)
    result=PdfReader(ROOT/MANUAL)
    assert len(result.pages)==len(old.pages)+1
    assert all(a.get_contents().get_data()==b.get_contents().get_data() for a,b in zip(old.pages,result.pages[1:]))
    print(TITLE+': '+str(len(result.pages))+' páginas; anteriores conservadas')
if __name__=='__main__':main()
