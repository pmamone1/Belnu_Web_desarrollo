"""Prepend release guidance; preserve the committed manual pages byte-for-byte in content streams."""
from pathlib import Path
from io import BytesIO
import subprocess
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]
BASE = '486afe185416e80d6f6c202561791f3845f1d4ea'
MANUAL = 'Manual_MiDistri_Pedidos_Online.pdf'
GUIDE = 'docs/CARRITO_NAVBAR_v49.md'
TITLE = 'MiDistri-Pedidos v49'
NOTICE = 'Esta guía del carrito prevalece sobre las instrucciones anteriores para este flujo.'

def main():
    styles = getSampleStyleSheet()
    styles['BodyText'].fontSize = 9.5
    styles['BodyText'].leading = 12
    styles['BodyText'].spaceAfter = 6
    styles['Heading2'].fontSize = 12
    styles['Heading2'].leading = 15
    styles['Heading2'].spaceBefore = 8
    story = [Paragraph(TITLE + ' - Guía vigente', styles['Title']),
             Paragraph(NOTICE, styles['BodyText']), Spacer(1, 3 * mm)]
    section = (ROOT / GUIDE).read_text(encoding='utf-8').split('## Guía de uso')[1].split('## Detalle técnico')[0]
    for line in section.strip().splitlines():
        if not line.strip():
            continue
        heading = line.startswith('### ')
        text = line[4:] if heading else line
        text = text.replace('—', '-').replace('–', '-').replace('−', '-').replace('→', '>')
        story.append(Paragraph(escape(text), styles['Heading2' if heading else 'BodyText']))
    chapter = BytesIO()
    SimpleDocTemplate(chapter, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                      topMargin=16 * mm, bottomMargin=16 * mm).build(story)
    oldbytes = subprocess.check_output(['git', '-c', 'core.fsmonitor=false', 'show', BASE + ':' + MANUAL], cwd=str(ROOT))
    new = PdfReader(BytesIO(chapter.getvalue()))
    old = PdfReader(BytesIO(oldbytes))
    assert len(new.pages) == 1 and len(old.pages) == 50, 'Revisar extensión de la guía y el manual de base'
    writer = PdfWriter()
    writer.append(new)
    writer.append(old)
    with (ROOT / MANUAL).open('wb') as handle:
        writer.write(handle)
    result = PdfReader(ROOT / MANUAL)
    assert len(result.pages) == len(old.pages) + len(new.pages)
    assert all(a.get_contents().get_data() == b.get_contents().get_data()
               for a, b in zip(old.pages, result.pages[len(new.pages):]))
    assert all(a.extract_text() == b.extract_text()
               for a, b in zip(old.pages, result.pages[len(new.pages):]))
    print(TITLE + ': capítulo ' + str(len(new.pages)) + ' páginas; anterior ' + str(len(old.pages))
          + '; total ' + str(len(result.pages)) + '; contenido histórico conservado')

if __name__ == '__main__':
    main()
