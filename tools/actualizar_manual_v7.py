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
BASE='6734ce86aced5cc199fd8320231eaffb80774c72'
MANUAL='Manual_MiDistri_Pedidos_Online.pdf'
GUIDE='docs/ACCESO_TIENDA_v7.md'
TITLE='MiDistri-Pedidos v7 r2'
def main():
    styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=11;styles['BodyText'].leading=15
    styles['BodyText'].spaceAfter=9
    text=(ROOT/GUIDE).read_text(encoding='utf-8').split('## Guía de uso')[1].strip().splitlines()
    story=[Paragraph(TITLE+' - Guía actual',styles['Title']),
        Paragraph('Prioridad sobre capturas e instrucciones antiguas. Corrección de configuración: usar el paquete r2 para retomar la instalación v7 interrumpida. Instalación r2 y activación en producción pendientes. La campaña no se envía.',styles['BodyText']),Spacer(1,4*mm)]
    for index,line in enumerate(text):
        if index==5:story.extend([PageBreak(),Paragraph('Administrar la tienda y compartir',styles['Title'])])
        story.append(Paragraph(escape(line),styles['BodyText']))
    chapter=BytesIO()
    SimpleDocTemplate(chapter,pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=16*mm,bottomMargin=16*mm).build(story)
    oldbytes=subprocess.check_output(['git','-c','core.fsmonitor=false','show',BASE+':'+MANUAL],cwd=str(ROOT))
    new=PdfReader(BytesIO(chapter.getvalue()));old=PdfReader(BytesIO(oldbytes))
    assert len(new.pages)==2,'El capítulo debe tener dos páginas'
    writer=PdfWriter();writer.append(BytesIO(chapter.getvalue()));writer.append(BytesIO(oldbytes))
    with (ROOT/MANUAL).open('wb') as f:writer.write(f)
    result=PdfReader(ROOT/MANUAL)
    assert len(result.pages)==len(old.pages)+2
    assert all(a.get_contents().get_data()==b.get_contents().get_data() for a,b in zip(old.pages,result.pages[2:]))
    print(TITLE+': '+str(len(result.pages))+' páginas; anteriores conservadas')
if __name__=='__main__':main()
