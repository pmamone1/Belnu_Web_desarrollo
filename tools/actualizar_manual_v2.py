"""Prepend v580 to the unchanged v579 manual; create the portal's own support PDF."""
from io import BytesIO
from pathlib import Path
import subprocess
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph,SimpleDocTemplate,PageBreak,Spacer
ROOT=Path(__file__).resolve().parents[1]
def chapter(portal=False):
    styles=getSampleStyleSheet()
    styles['Title'].fontSize=22;styles['Title'].leading=27;styles['Title'].textColor=colors.HexColor('#1d4a3a')
    styles['BodyText'].fontSize=11;styles['BodyText'].leading=16;styles['BodyText'].spaceAfter=10
    story=[]
    def add(text,style='BodyText'):story.append(Paragraph(text,styles[style]))
    add('MiDistri - Pedidos Online v2' if portal else 'Urban Soft - Manual vigente v1.18.580','Title')
    add('Pedidos online por distribuidora','Heading1')
    add('Instalación productiva pendiente. Este capítulo prevalece para la integración MiDistri. El resto de la operación de Urban Soft v579 se conserva.')
    add('1. Publicar el catálogo - Urban Point','Heading2')
    add('En Urban Soft: <b>Urban Point &gt; MiDistri - Catálogo</b>. Crear una conexión, elegir distribuidoras y guardar su clave sólo en el cPanel de MiDistri. Buscar productos, elegir proveedor y publicar. Elegir Belgrano20 o Barracas65 incluye la pareja permitida20/65. Esta pantalla no muestra vendedores.')
    add('2. Invitar al vendedor - Distribuidora','Heading2')
    add('En <b>Comunicaciones &gt; MiDistri - Pedidos online</b>, buscar y elegir vendedor. Crear su enlace para copiar o compartir. Para Email, seleccionar contacto habilitado y escribir el Email exacto. Es personal, vence en48h y se consume al tocar Entrar. No publicarlo.')
    add('3. Elegir y revisar - Vendedor','Heading2')
    add('Abrir el enlace, tocar Entrar y revisar nombre, distribuidora, LIN y VV. Elegir cantidades y revisar precio vendedor y PVP antes de enviar. No se paga en el portal. Mis pedidos conserva estados y remitos. Si falla la conexión, reintentar el mismo pedido guardado.')
    story.append(PageBreak())
    add('Preparar, confirmar y comunicar','Title')
    add('4. Revisar y llevar al depósito','Heading2')
    add('El pedido aparece como Recibido. Revisar y marcar OK para preparar. Seleccionar pedidos OK y descargar el Excel, que identifica distribuidora, LIN, VV, vendedor, productos y cantidades. <b>Recibir, marcar OK y exportar no generan cargos.</b>')
    add('5. Confirmar preparado o cancelar','Heading2')
    add('Si falta stock, cancelar antes de emitir. Cuando la mercadería esté preparada, un usuario con autorización financiera pulsa <b>Confirmar preparación, generar cargo y remito</b>. Se usa el saldo y remito nativos. Repetir la confirmación no duplica el cargo. La anulación posterior corresponde al circuito documentado de Urban.')
    add('6. Comprender los avisos de Email','Heading2')
    add('Se usa el remitente de la distribuidora y los contactos habilitados de su agenda; se respetan bajas. Aceptado significa que el proveedor SMTP lo aceptó, no que fue leído. Pendiente puede procesarse. Por conciliar o Enviando requiere verificar el resultado; si se interrumpió el proceso, esperar15min.')
    add('7. Conciliar sin duplicar','Heading2')
    add('Tras verificar con el proveedor, elegir Aceptado o No fue aceptado, indicar motivo y confirmar. <b>Guardar conciliación no envía Email ni cambia saldos.</b> Sólo una certeza de no envío permite dejarlo pendiente para reintentar.')
    add('Protección de la información','Heading2')
    add('Cada distribuidora opera dentro de su alcance privado; se conserva la excepción actual de SuperUsuario. Urban Point común administra catálogo, sin datos personales. Matrícula no se muestra. Instalación y publicación no habilitan portal, cron ni Email automáticamente.')
    buf=BytesIO();SimpleDocTemplate(buf,pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,topMargin=17*mm,bottomMargin=17*mm).build(story)
    return buf.getvalue()
def main():
    target=ROOT/'Manual_MiDistri_Pedidos_Online.pdf'
    target.write_bytes(chapter(portal=True))
    print('Manual propio:',target)
if __name__=='__main__':main()
