"""Prepend the current compatibility note and preserve every v4 manual page."""
from pathlib import Path
from io import BytesIO
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph,SimpleDocTemplate,Spacer
from pypdf import PdfReader,PdfWriter
ROOT=Path(__file__).resolve().parents[1]
BASE='43ae0875f80d13857efa810385cc10a027763e85'
MANUAL='Manual_MiDistri_Pedidos_Online.pdf'

def main():
    styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=11;styles['BodyText'].leading=16
    styles['BodyText'].spaceAfter=12
    text=[
        ('MiDistri-Pedidos v5','Title'),
        ('Catálogo con presentación opcional','Heading1'),
        ('Guía vigente del 22/10/2026. Instalación en producción pendiente. Esta nota tiene prioridad sobre instrucciones anteriores acerca de la sincronización. El panel y las tareas del manual v4 siguen vigentes.','BodyText'),
        ('Qué mejora','Heading2'),
        ('Los productos que tienen Display en cero en Urban Soft se muestran como productos sin presentación informada. Ese dato opcional ya no impide actualizar el catálogo completo. Las presentaciones positivas siguen mostrándose.','BodyText'),
        ('Actualizar el catálogo','Heading2'),
        ('Después de instalar v5 en MiDistri, entrar desde Urban Soft a <b>Administrar MiDistri-Pedidos > Productos</b>. Si aparece el aviso de sincronización pendiente, pulsar <b>Actualizar copia del catálogo</b>. No volver a publicar una selección que Urban ya guardó.','BodyText'),
        ('Fotos y precios','Heading2'),
        ('Las fotos disponibles, el precio vendedor y el PVP se toman de Urban Soft. Esta corrección no cambia esos datos ni genera pedidos, stock, cargos o remitos. Tampoco envía invitaciones por Email.','BodyText'),
        ('Productos pendientes de revisión','Heading2'),
        ('Los productos excluidos por decisión comercial permanecen sin publicar. Revisar sus datos en Urban Soft antes de agregarlos al catálogo. Las cuatro Esferas coleccionables señaladas por el usuario quedan pendientes de revisar precios.','BodyText'),
        ('Instalación separada','Heading2'),
        ('Se actualiza únicamente MiDistri en belnuweb, sobre v4. No se reinstala Urban Soft ni se cambian sus variables. No hay nuevas migraciones. Las instrucciones completas se incluyen en el ZIP de v5.','BodyText')
    ]
    story=[Paragraph(t,styles[s]) for t,s in text]
    buf=BytesIO()
    SimpleDocTemplate(buf,pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,topMargin=18*mm,bottomMargin=18*mm).build(story)
    assert len(PdfReader(BytesIO(buf.getvalue())).pages)==1
    previous=subprocess.check_output(['git','-c','core.fsmonitor=false','show',BASE+':'+MANUAL],cwd=str(ROOT))
    writer=PdfWriter();writer.append(BytesIO(buf.getvalue()));writer.append(BytesIO(previous))
    with (ROOT/MANUAL).open('wb') as f:writer.write(f)
    old=PdfReader(BytesIO(previous));new=PdfReader(ROOT/MANUAL)
    assert len(new.pages)==len(old.pages)+1
    assert all(a.get_contents().get_data()==b.get_contents().get_data() for a,b in zip(old.pages,new.pages[1:]))
    print('Manual v5: nueva página y todas las anteriores conservadas.')
if __name__=='__main__':main()
