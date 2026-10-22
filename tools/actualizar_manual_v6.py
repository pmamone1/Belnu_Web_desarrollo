"""Prepend the current guide and preserve all prior PDF page contents."""
from pathlib import Path
from io import BytesIO
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph,SimpleDocTemplate,Spacer
from pypdf import PdfReader,PdfWriter
ROOT=Path(__file__).resolve().parents[1]
BASE="dd4478782c4f1e341c6345743a86af289948e35f"
MANUAL="Manual_MiDistri_Pedidos_Online.pdf"
TITLE="MiDistri-Pedidos v6"
def main():
    styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=10.5;styles['BodyText'].leading=14
    styles['BodyText'].spaceAfter=7
    text=[["Pedidos parciales y catálogo","Heading1"],["Guía vigente del 22/10/2026. Instalación en producción pendiente. Este capítulo tiene prioridad sobre instrucciones y capturas anteriores. Instalar MiDistri v6 antes de Urban Soft v584.","BodyText"],["1. Elegir productos","Heading2"],["El catálogo permite buscar por nombre y categoría. Todos los visitantes ven Precio vendedor y PVP. El pedido requiere el enlace personal del vendedor y se calcula con el precio vendedor. No se paga online.","BodyText"],["2. Preparar sólo lo disponible","Heading2"],["La distribuidora marca el pedido OK. En Revisar preparación, incluye o desmarca productos e indica cantidades entre cero y lo solicitado. Los precios originales se conservan. Revisar el importe antes de confirmar.","BodyText"],["3. Confirmar y compartir el remito","Heading2"],["Si se piden 10 y se preparan 6, se cobran sólo 6; las 4 restantes se cancelan por falta de stock, sin quedar pendientes. La confirmación genera un único pedido, cargo y remito. Cero preparado cancela sin cargo. Abrir el remito para imprimir; la cola de Email usa ese mismo PDF.","BodyText"],["4. Ver el resultado y pedir abastecimiento","Heading2"],["Al abrir su pedido, el vendedor ve cantidades preparadas, canceladas y total. Si falla la conexión, se advierte que es la última copia guardada. En Mercadería necesaria se descarga el Excel para Urban Point, sin datos personales. El Excel de depósito por vendedor sigue separado.","BodyText"],["5. Contactos y campañas","Heading2"],["Cada Email habilitado del vendedor recibe su enlace independiente y los avisos correspondientes, respetando bajas. Dos contactos pueden entrar sin cerrar la sesión del otro. Revisar los destinatarios antes de confirmar una campaña. Esta actualización no envía la campaña existente.","BodyText"],["Permisos y recuperación","Heading2"],["Cada usuario mantiene su alcance actual; 20 incluye 65 sólo cuando ambas están autorizadas. Ante errores de instalación conservar la copia de código y consultar las instrucciones del paquete. No volver a código anterior que interprete una preparación parcial como completa.","BodyText"]]
    story=[Paragraph(TITLE+' - Manual vigente',styles['Title']),Spacer(1,3*mm)]
    story.extend(Paragraph(t,styles[s]) for t,s in text)
    buf=BytesIO()
    SimpleDocTemplate(buf,pagesize=A4,leftMargin=18*mm,rightMargin=18*mm,topMargin=16*mm,bottomMargin=16*mm).build(story)
    chapter=buf.getvalue()
    assert len(PdfReader(BytesIO(chapter)).pages)==1
    previous=subprocess.check_output(['git','-c','core.fsmonitor=false','show',BASE+':'+MANUAL],cwd=str(ROOT))
    writer=PdfWriter();writer.append(BytesIO(chapter));writer.append(BytesIO(previous))
    with (ROOT/MANUAL).open('wb') as f:writer.write(f)
    old=PdfReader(BytesIO(previous));new=PdfReader(ROOT/MANUAL)
    assert len(new.pages)==len(old.pages)+1
    assert all(a.get_contents().get_data()==b.get_contents().get_data() for a,b in zip(old.pages,new.pages[1:]))
    print(TITLE,str(len(new.pages))+' páginas, anteriores conservadas')
if __name__=='__main__':main()
