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
BASE='8bcbfb1add88917efb831e2ce4d6e9fd7c06d78b'
MANUAL='Manual_MiDistri_Pedidos_Online.pdf'
GUIDE='docs/ACCESO_EMAIL_v14.md'
TITLE='MiDistri-Pedidos v14'
def main():
    styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=9.5;styles['BodyText'].leading=12
    styles['BodyText'].spaceAfter=5
    text=(ROOT/GUIDE).read_text(encoding='utf-8').split('## Guía de uso')[1].split('## Instalación y operación técnica')[0].strip().splitlines()
    story=[Paragraph(TITLE+' - Guía actual',styles['Title']),
        Paragraph('Ingreso por Email y perfiles. Esta guía prevalece sobre las instrucciones anteriores de acceso. Se conservan permisos y remitentes propios; instalación productiva pendiente. Sin campaña.',styles['BodyText']),Spacer(1,4*mm)]
    for index,line in enumerate(text):
        story.append(Paragraph(escape(line.replace("→", ">")),styles['BodyText']))
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
