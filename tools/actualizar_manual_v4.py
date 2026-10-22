"""Prepend the current guide while preserving every older manual page."""
from pathlib import Path
from io import BytesIO
import subprocess
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph,SimpleDocTemplate,Spacer,PageBreak
from pypdf import PdfReader,PdfWriter
ROOT=Path(__file__).resolve().parents[1]
BASE='4893961c7370410c568b358837f8d9c320e9f916'
MANUAL='Manual_MiDistri_Pedidos_Online.pdf'
TITLE='MiDistri-Pedidos v4'

def main():
    styles=getSampleStyleSheet();styles['BodyText'].fontSize=11;styles['BodyText'].leading=16
    styles['BodyText'].spaceAfter=10
    pages=[
    [
      ('Administrar MiDistri-Pedidos','Heading1'),
      ('Guía vigente - instalación en producción pendiente. Este capítulo tiene prioridad sobre instrucciones anteriores de configuración o pruebas. Urban Soft v583 y MiDistri v4 se instalan por separado.','BodyText'),
      ('Entrar como Distribuidor','Heading2'),
      ('En Urban Soft abrir <b>Salidas / Anuncios > Pedidos > Administrar MiDistri-Pedidos</b>. Revisar la conexión y las distribuidoras y pulsar Entrar. No se necesita otra cuenta ni contraseña. Si el acceso no aparece, un responsable debe revisar los permisos y la habilitación de la integración.','BodyText'),
      ('Productos: publicar todo o elegir','Heading2'),
      ('Elegir <b>Productos</b> y el proveedor para las altas. Usar <b>Publicar catálogo completo</b> o marcar productos. Revisar altas, existentes, reactivados y exclusiones antes de confirmar. Los precios vienen de Urban Soft; los productos ya publicados conservan su proveedor. Publicar no crea stock ni cargos.','BodyText'),
      ('Si falta actualizar el catálogo','Heading2'),
      ('Cuando Urban guarda pero la sincronización falla, pulsar <b>Actualizar copia del catálogo</b>. No volver a publicar por ese motivo. Ocultar un producto evita nuevos pedidos y conserva los anteriores.','BodyText'),
      ('Pedidos y preparación','Heading2'),
      ('Recibido: revisar disponibilidad. Marcar OK permite descargar el Excel para depósito, con línea y número de vendedor. Sólo el paso separado <b>Revisar preparación > Confirmar preparación y generar cargo / remito</b> genera deuda. Requiere permiso financiero. Sin stock, cancelar antes de preparar.','BodyText'),
      ('Mi tienda','Heading2'),
      ('Cambiar logo, Email/teléfono de contacto, bienvenida e instrucciones. Son datos públicos de esa tienda. Logo JPG/PNG/WebP hasta 2 MB y ocho megapíxeles; el sistema lo adapta a 768 píxeles. No modifica el remitente de los Email.','BodyText')
    ],
    [
      ('Invitar a vendedores desde Campañas','Heading1'),
      ('En Urban Soft abrir <b>Comunicaciones > Campañas > Enviar accesos a MiDistriPedidos</b>. La instalación no manda invitaciones por sí sola.','BodyText'),
      ('1. Preparar el mensaje','Heading2'),
      ('Elegir el tipo Acceso a MiDistriPedidos, conexión, distribuidora y canal Email. Revisar asunto y explicación. Guardar el borrador. El sistema agregará el enlace personal al procesar el envío. No pegar un enlace de un vendedor en el mensaje común.','BodyText'),
      ('2. Elegir destinatarios','Heading2'),
      ('Usar Todos, Por líneas o Vendedores puntuales. En una selección individual se puede elegir otro contacto habilitado. La vista previa muestra vendedor, LIN, VV, Email y exclusiones. Los contactos dados de baja se respetan. Sin Email se excluye con motivo.','BodyText'),
      ('3. Confirmar la vista previa','Heading2'),
      ('Confirmar encola una vez. El procesador habitual de campañas envía un Email por vendedor; dos vendedores con la misma dirección reciben enlaces distintos. No se necesita otro cron para esta campaña. Revisar el resumen de aceptados, fallidos e inciertos. Un resultado incierto requiere conciliación, no reenvío automático.','BodyText'),
      ('Enlaces y privacidad','Heading2'),
      ('El enlace vence en 48 horas desde su preparación para envío y se utiliza una sola vez. Una nueva invitación reemplaza anteriores aún sin usar; conviene utilizar la última emitida. Cada vendedor entra a su catálogo y pedidos. Nunca compartir su enlace con otro vendedor.','BodyText'),
      ('Alcance y permisos','Heading2'),
      ('20 incluye 65 sólo si usuario y conexión autorizan ambas. Cada tienda mantiene su presentación. Los permisos de catálogo publicado y presentación son independientes; no conceden edición global de productos. El SuperUsuario funcional conserva su excepción actual. Salir de administración cierra el acceso delegado.','BodyText'),
      ('Activación de esta actualización','Heading2'),
      ('Después de instalar ambos paquetes, habilitar MIDISTRI_ADMIN_ENABLED=True en ambas aplicaciones y reiniciarlas. Para enviar accesos se requieren además las habilitaciones de Email, remitentes y clave privada de comunicaciones. Los detalles de cPanel y recuperación están en el paquete.','BodyText')
    ]]
    story=[]
    for idx,paragraphs in enumerate(pages):
        if idx:story.append(PageBreak())
        story.append(Paragraph(TITLE+' - Manual vigente',styles['Title']))
        story.append(Spacer(1,4*mm))
        story.extend(Paragraph(text,styles[style]) for text,style in paragraphs)
    buf=BytesIO();SimpleDocTemplate(buf,pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,
        topMargin=18*mm,bottomMargin=18*mm).build(story)
    chapter=buf.getvalue();assert len(PdfReader(BytesIO(chapter)).pages)==2
    previous=subprocess.check_output(['git','-c','core.fsmonitor=false','show',BASE+':'+MANUAL],cwd=str(ROOT))
    writer=PdfWriter();writer.append(BytesIO(chapter));writer.append(BytesIO(previous))
    with (ROOT/MANUAL).open('wb') as f:writer.write(f)
    old=PdfReader(BytesIO(previous));new=PdfReader(ROOT/MANUAL)
    assert len(new.pages)==len(old.pages)+2
    assert all(a.get_contents().get_data()==b.get_contents().get_data() for a,b in zip(old.pages,new.pages[2:]))
    print(TITLE,str(len(new.pages))+' páginas; anteriores conservadas')
if __name__=='__main__':main()
