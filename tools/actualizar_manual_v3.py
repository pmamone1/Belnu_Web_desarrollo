"""Prepend the current correction while preserving all prior manual pages."""
from pathlib import Path
from io import BytesIO
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph,SimpleDocTemplate,Spacer
from pypdf import PdfReader,PdfWriter
ROOT=Path(__file__).resolve().parents[1]
BASE='8189c03821a79b1e1e38f92b03cd27ab4dd0caf1'
MANUAL='Manual_MiDistri_Pedidos_Online.pdf'
TITLE='MiDistri Pedidos Online v3'
def main():
    styles=getSampleStyleSheet()
    styles['BodyText'].fontSize=11;styles['BodyText'].leading=16
    styles['BodyText'].spaceAfter=11
    story=[Paragraph(TITLE+' - Manual vigente',styles['Title']),Spacer(1,5*mm)]
    paragraphs=[
      ('Guardar formularios de MiDistri','Heading1'),
      ('Este capítulo tiene prioridad sobre instrucciones anteriores sobre formularios. La instalación productiva de esta corrección está pendiente de confirmación.','BodyText'),
      ('Qué corrige','Heading2'),
      ('La versión anterior podía mostrar Prohibido (403) al guardar el catálogo, crear un acceso o enviar un formulario. Se corrigió la cabecera de privacidad que impedía al navegador identificar el sitio de origen.','BodyText'),
      ('Cómo seguir después de actualizar','Heading2'),
      ('1. Instalar el paquete correspondiente en cada aplicación. Urban Soft y MiDistri conservan sus paquetes y entornos separados.','BodyText'),
      ('2. Abrir nuevamente la pantalla desde su enlace. Evitar reenviar el formulario de la página que mostraba el error.','BodyText'),
      ('3. Revisar producto, distribuidora y precios antes de guardar. El piloto pendiente es para Belgrano20 y Barracas65. Publicar catálogo no genera pedidos, cargos ni Email.','BodyText'),
      ('4. Conservar la integración y los Email apagados hasta configurar la conexión y comprobar el piloto autorizado. La instalación no crea ni cambia claves privadas.','BodyText'),
      ('Protección e historial','Heading2'),
      ('Los formularios siguen requiriendo token y origen válido. Se conserva la privacidad frente a sitios externos, los permisos y el alcance por distribuidora. No se cambian datos, importes, remitos, saldos ni migraciones. No se necesita un nuevo respaldo completo por esta corrección de archivos.','BodyText')]
    story.extend(Paragraph(text,styles[style]) for text,style in paragraphs)
    buf=BytesIO();SimpleDocTemplate(buf,pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,
        topMargin=18*mm,bottomMargin=18*mm).build(story)
    cover=buf.getvalue();assert len(PdfReader(BytesIO(cover)).pages)==1
    previous=subprocess.check_output(['git','show',BASE+':'+MANUAL],cwd=str(ROOT))
    writer=PdfWriter();writer.append(BytesIO(cover));writer.append(BytesIO(previous))
    with (ROOT/MANUAL).open('wb') as f:writer.write(f)
    new=PdfReader(ROOT/MANUAL);old=PdfReader(BytesIO(previous))
    assert len(new.pages)==len(old.pages)+1
    assert all(a.get_contents().get_data()==b.get_contents().get_data()
        for a,b in zip(old.pages,new.pages[1:]))
    print(TITLE,len(new.pages),'pages; previous pages preserved')
if __name__=='__main__':main()
