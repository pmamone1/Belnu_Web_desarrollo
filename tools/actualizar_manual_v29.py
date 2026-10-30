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
BASE='d1644ce4ab7944381c6a3e0f2f86f279086e8b38'
MANUAL='Manual_MiDistri_Pedidos_Online.pdf'
GUIDE='docs/INTERVALOS_MARIADB_v29.md'
TITLE='MiDistri-Pedidos v29'
def main():
    styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=9.5;styles['BodyText'].leading=12
    styles['BodyText'].spaceAfter=5
    text=(ROOT/GUIDE).read_text(encoding='utf-8').split('## Guía de uso')[1].split('## Detalle técnico')[0].strip().splitlines()
    story=[Paragraph(TITLE+' - Guía actual',styles['Title']),
        Paragraph('Corrección de compatibilidad MariaDB para la medición. Este capítulo prevalece sobre instrucciones anteriores acerca de restricciones de intervalos. Conserva la captura activa y los eventos. La instalación productiva de v29 sigue pendiente; no se envían campañas.',styles['BodyText']),Spacer(1,4*mm)]
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
