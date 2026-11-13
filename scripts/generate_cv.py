"""Generate bilingual linked CV PDFs from the portfolio HTML. Requires reportlab."""
from html.parser import HTMLParser
from html import escape
from pathlib import Path
import re
import sys
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class Node:
    def __init__(self, tag='', attrs=()):
        self.tag, self.attrs, self.children = tag, dict(attrs), []
    def text(self):
        return re.sub(r'\s+', ' ', ''.join(c.text() if isinstance(c, Node) else c for c in self.children)).strip()
    def find(self, tag=None, cls=None, id=None):
        found=[]
        for n in self.children:
            if not isinstance(n, Node): continue
            if (not tag or n.tag==tag) and (not cls or cls in n.attrs.get('class','').split()) and (not id or n.attrs.get('id')==id): found.append(n)
            found.extend(n.find(tag,cls,id))
        return found
    def one(self, **kw): return self.find(**kw)[0]

class Parser(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.root=Node(); self.stack=[self.root]; self.feed(text)
    def handle_starttag(self, tag, attrs):
        n=Node(tag,attrs); self.stack[-1].children.append(n)
        if tag not in ('area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'): self.stack.append(n)
    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag,attrs)
        if self.stack[-1].tag==tag: self.stack.pop()
    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1,0,-1):
            if self.stack[i].tag==tag:
                self.stack=self.stack[:i]; break
    def handle_data(self,data): self.stack[-1].children.append(data)

BLUE=colors.HexColor('#2563eb'); INK=colors.HexColor('#15243c'); MUTED=colors.HexColor('#526079')
W,H=A4; LEFT=43; WIDTH=W-86

def make_pdf(source, output, lang, fonts):
    root=Parser(source.read_text(encoding='utf-8')).root
    en=lang=='en'; site='https://sergiocr9991-beep.github.io/CV-Sergio-Coll/'+('en/' if en else '')
    for name,filename in [('CV','arial.ttf'),('CV-Bold','arialbd.ttf')]:
        if name not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont(name,str(fonts/filename)))
    c=canvas.Canvas(str(output),pagesize=A4,pageCompression=1)
    c.setTitle('Sergio Coll Ramírez | CV | '+('English' if en else 'Español')); c.setAuthor('Sergio Coll Ramírez'); c.setSubject('Graphic design, motion graphics, CTV, OLV, UX/UI')
    styles={
        'body':ParagraphStyle('body',fontName='CV',fontSize=10.5,leading=14.5,textColor=INK,spaceAfter=0),
        'small':ParagraphStyle('small',fontName='CV',fontSize=9,leading=12.5,textColor=MUTED),
        'title':ParagraphStyle('title',fontName='CV-Bold',fontSize=11.5,leading=15,textColor=INK),
    }
    y=H-43
    def para(text,style='body',after=5):
        nonlocal y
        p=Paragraph(text,styles[style]); _,h=p.wrap(WIDTH,1000)
        if y-h<44: raise ValueError(f'Page overflow: {lang}: {text[:70]}')
        p.drawOn(c,LEFT,y-h); y-=h+after
    def text(s): return escape(s)
    def link(label,url): return '<link href="'+escape(url,quote=True)+'" color="#2563eb">'+text(label)+'</link>'
    def section(label):
        nonlocal y
        y-=6; c.setFillColor(BLUE); c.setFont('CV-Bold',10.2); c.drawString(LEFT,y,label.upper()); y-=9
        c.setStrokeColor(colors.HexColor('#d8e2f2')); c.line(LEFT,y,W-LEFT,y); y-=13
    def footer(num):
        c.setStrokeColor(colors.HexColor('#d8e2f2')); c.line(LEFT,34,W-LEFT,34)
        c.setFillColor(MUTED); c.setFont('CV',7.6); c.drawString(LEFT,22,'Sergio Coll Ramírez  |  '+('English' if en else 'Español'))
        c.drawRightString(W-LEFT,22,f'{num} / 2')
    c.setFillColor(BLUE); c.rect(0,H-8,W,8,fill=1,stroke=0)
    c.setFillColor(INK); c.setFont('CV-Bold',25); c.drawString(LEFT,y-22,'Sergio Coll Ramírez'); y-=43
    para('Professional in Graphic Design' if en else 'Profesional en Diseño Gráfico','title',8)
    para('Bogotá, Colombia  |  '+link('+57 305 761 6657','tel:+573057616657')+'  |  '+link('sergiocr9991@gmail.com','mailto:sergiocr9991@gmail.com'),'small',5)
    para('  /  '.join([link('Portfolio' if en else 'Portafolio',site),link('Behance','https://www.behance.net/Sergio_cr'),link('LinkedIn','https://www.linkedin.com/in/sergiocr99/'),link('YouTube','https://www.youtube.com/@sergioramirez6791/videos')]),'small',9)
    profile=root.one(id='perfil')
    section('Professional profile' if en else 'Perfil profesional')
    for p in profile.one(cls='profile-text').find(tag='p'): para(text(p.text()))
    experience=root.one(id='experiencia'); section('Work experience' if en else 'Experiencia laboral')
    for job in experience.find(cls='job-card'):
        para(text(job.one(tag='h3').text())+' <font size="8.3" color="#526079">| '+text(job.one(cls='pill').text())+'</font>','title',2)
        para(text(job.one(tag='h4').text()),'small',4)
        for p in job.find(tag='p'): para(text(p.text()),after=9)
    footer(1); c.showPage(); y=H-43
    c.setFillColor(BLUE); c.rect(0,H-8,W,8,fill=1,stroke=0)
    para('Sergio Coll Ramírez','title',4)
    section('Education' if en else 'Educación')
    for edu in root.one(id='educacion').find(cls='edu'):
        para(text(edu.one(tag='h3').text()),'title',2)
        para(text(edu.one(tag='h4').text())+' | '+text(edu.one(cls='pill').text()),'small',3)
        for p in edu.find(tag='p'): para(text(p.text()),after=7)
    section('Expertise and tools' if en else 'Capacidades y herramientas')
    caps=profile.one(cls='capabilities'); para(text(caps.one(tag='p').text()),after=4)
    for cap in caps.find(cls='cap'):
        para('<b>'+text(cap.one(tag='b').text())+':</b> '+text(cap.one(tag='span').text()),after=2)
    y-=3
    badges=root.one(cls='tools-card').find(cls='tool-badge')
    para('<b>'+('Tools' if en else 'Herramientas')+':</b> '+' · '.join(text(n.text()) for n in badges),after=4)
    para('<b>'+('Languages' if en else 'Idiomas')+':</b> '+('Spanish: Native · English: B2' if en else 'Español: Nativo · Inglés: B2'),after=5)
    section('Featured projects' if en else 'Proyectos destacados')
    for project in root.find(cls='project-card'):
        a=project.attrs
        para('<b>'+link(a['data-title'],a['data-url'])+'</b> <font size="8.3" color="#526079">| '+text(a['data-type'])+'</font>','body',2)
        para(text(a['data-desc']),after=7)
    footer(2); c.save()
    return y

if __name__=='__main__':
    base=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent
    output=base/'assets'/'cv'; output.mkdir(parents=True,exist_ok=True)
    fonts=Path(sys.argv[2]) if len(sys.argv)>2 else Path('C:/Windows/Fonts')
    for lang,default in [('es','index.html'),('en','en/index.html')]:
        source=base/default
        if not source.exists(): source=base/(lang+'-original.html')
        dest=output/f'Sergio-Coll-Ramirez-CV-{lang.upper()}.pdf'
        print(lang,make_pdf(source,dest,lang,fonts),dest)
