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
BASE='f76e3b59d34a3dbc210c15a260296d3469098757'
MANUAL='Manual_MiDistri_Pedidos_Online.pdf'
GUIDE='docs/CATALOGO_PRESENTACION_v26.md'
TITLE='MiDistri-Pedidos v26'
def main():
    styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=9.5;styles['BodyText'].leading=12
    styles['BodyText'].spaceAfter=5
    text=(ROOT/GUIDE).read_text(encoding='utf-8').split('## Guía de uso')[1].split('## Detalle técnico')[0].strip().splitlines()
    story=[Paragraph(TITLE+' - Guía actual',styles['Title']),
        Paragraph('Tarjetas alineadas y botones breves del catálogo. Esta guía prevalece sobre instrucciones anteriores de edición y pedidos. Instalación productiva pendiente; sin campaña.',styles['BodyText']),Spacer(1,4*mm)]
    for index,line in enumerate(text):
        story.append(Paragraph(escape(line.replace("→", ">").replace("−", "-")),styles['BodyText']))
    chapter=BytesIO()
    SimpleDocTemplate(chapter,pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=16*mm,bottomMargin=16*mm).build(story)
    oldbytes=subprocess.check_output(['git','-c','core.fsmonitor=false','show',BASE+':'+MANUAL],cwd=str(ROOT))
    new=PdfReader(BytesIO(chapter.getvalue()));old=PdfReader(BytesIO(oldbytes))
    assert 1<=len(new.pages)<=2,'El capítulo debe tener una o dos páginas'
    writer=PdfWriter();writer.append(new);writer.append(old)
    with (ROOT/MANUAL).open('wb') as f:writer.write(f)
    result=PdfReader(ROOT/MANUAL)
    assert len(result.pages)==len(old.pages)+len(new.pages)
    assert all(a.get_contents().get_data()==b.get_contents().get_data() for a,b in zip(old.pages,result.pages[len(new.pages):]))
    print(TITLE+': '+str(len(result.pages))+' páginas; anteriores conservadas')
if __name__=='__main__':main()
