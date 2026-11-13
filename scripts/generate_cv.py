"""Rebuild the supplied visual CV layout using current portfolio content."""
from pathlib import Path
from html import escape
import sys
import re
from io import BytesIO
from urllib.request import urlopen
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image

from html.parser import HTMLParser
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



BLUE=colors.HexColor('#323187'); LIGHTBLUE=colors.HexColor('#4557ab')
INK=colors.HexColor('#17171d'); MUTED=colors.HexColor('#45454b')
W,H=A4

def create_cv(source,output,lang,assets):
    root=Parser(source.read_text(encoding='utf-8')).root
    en=lang=='en'
    for weight in ['Regular','Medium','SemiBold','Bold']:
        font=assets/f'Montserrat-{weight}.ttf'
        if not font.exists():
            font.parent.mkdir(parents=True,exist_ok=True)
            with urlopen('https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/'+font.name) as response:
                font.write_bytes(response.read())
        pdfmetrics.registerFont(TTFont('M-'+weight,str(font)))
    pdfmetrics.registerFontFamily('M-Regular',normal='M-Regular',bold='M-Bold',italic='M-Regular',boldItalic='M-Bold')
    c=canvas.Canvas(str(output),pagesize=A4,pageCompression=1)
    c.setTitle('Sergio Coll Ramírez | CV | '+('English' if en else 'Español'))
    c.setAuthor('Sergio Coll Ramírez'); c.setSubject('Designer | Digital advertising, CTV, OLV, motion graphics')
    c.setCreator('Sergio Coll Ramírez - updated portfolio CV')
    def line(x1,t1,x2,t2,width=0.8,color=INK):
        c.setStrokeColor(color);c.setLineWidth(width);c.line(x1,H-t1,x2,H-t2)
    def rect(x,t,w,h,color):
        c.setFillColor(color);c.rect(x,H-t-h,w,h,fill=1,stroke=0)
    def text(txt,x,t,size=9,font='M-Regular',color=INK,align='left',tracking=0):
        c.saveState()
        c.setFillColor(color);c.setFont(font,size)
        if tracking:
            obj=c.beginText(x,H-t-size);obj.setFont(font,size);obj.setCharSpace(tracking);obj.textOut(txt);c.drawText(obj)
        elif align=='center': c.drawCentredString(x,H-t-size,txt)
        else:c.drawString(x,H-t-size,txt)
        c.restoreState()
    def para(txt,x,t,w,size=8.2,leading=10.8,maxh=None,bold=False,color=INK):
        p=Paragraph(txt,ParagraphStyle('p',fontName='M-Bold' if bold else 'M-Regular',fontSize=size,leading=leading,textColor=color))
        _,h=p.wrap(w,1000)
        if maxh is not None and h>maxh+.01:raise ValueError(f'Overflow {lang}: {h}>{maxh}: {txt[:60]}')
        p.drawOn(c,x,H-t-h);return h
    def image(file,x,t,w,h): c.drawImage(ImageReader(str(assets/file)),x,H-t-h,w,h,mask='auto')
    def link(url,x,t,w,h):c.linkURL(url,(x,H-t-h,x+w,H-t),relative=0,thickness=0)
    def round_gradient(x,t,w,h,r=12):
        c.saveState();p=c.beginPath();p.roundRect(x,H-t-h,w,h,r);c.clipPath(p,stroke=0,fill=0)
        c.linearGradient(x,H-t,x+w,H-t,(BLUE,LIGHTBLUE),extend=True);c.restoreState()
    def section(label,t,x=23,width=549,size=15):
        text(label,x,t,size,'M-Bold');labelw=pdfmetrics.stringWidth(label,'M-Bold',size)
        line(x+labelw+9,t+11,x+width-11,t+11,color=MUTED)
        c.setFillColor(MUTED);c.circle(x+width-3,H-t-11,3.1,fill=1,stroke=0)
    def mini_heading(label,x,t,w):
        text(label,x+43,t,14,'M-Bold'); lw=pdfmetrics.stringWidth(label,'M-Bold',14)
        line(x,t+10,x+35,t+10,color=MUTED)
        line(x+43+lw+8,t+10,x+w-26,t+10,color=MUTED)
        for k in range(3):c.setFillColor(MUTED);c.circle(x+w-18+k*9,H-t-10,2.4,fill=1,stroke=0)
    def badge(label,x,t,w):
        round_gradient(x,t,w,16,8);text(label,x+w/2,t+2.5,7.2,'M-Bold',colors.white,'center')
    # The blue edge bands and diagonal strokes follow the supplied originals.
    rect(0,14,484,17,BLUE)
    for i in range(6):
        x=487+i*16.5;p=c.beginPath();p.moveTo(x,H-39);p.lineTo(x+8,H-14);p.lineTo(x+17,H-14);p.lineTo(x+9,H-39);p.close();c.setFillColor(LIGHTBLUE if i%2==0 else BLUE);c.drawPath(p,fill=1,stroke=0)
    text('Sergio Coll Ramírez',32,15.2,11.7,'M-Bold',colors.white)
    text('CV / EN' if en else 'CV / ES',446,18,6.6,'M-Medium',colors.white)
    c.setFillColor(MUTED);c.circle(28,H-61,2.8,fill=1,stroke=0);line(35,61,57,61,color=MUTED)
    tagline='Graphic Designer | Digital Design & Motion Graphics' if en else 'Diseñador Gráfico | Diseño Digital & Motion Graphics'
    text(tagline,64,51,10.8,'M-SemiBold',BLUE,tracking=.9)
    # Profile frame, with the original portrait and asymmetric clipping.
    c.setStrokeColor(BLUE);c.setLineWidth(.85);c.roundRect(115,H-229,440,141,10,fill=0,stroke=1)
    c.saveState();p=c.beginPath();x,t,w,h=33,80,158,198;y=H-t-h
    p.moveTo(x,y+h);p.lineTo(x+w-77,y+h);p.curveTo(x+w-28,y+h,x+w,y+h-28,x+w,y+h-77);p.lineTo(x+w,y);p.lineTo(x+77,y);p.curveTo(x+28,y,x,y+28,x,y+77);p.close();c.clipPath(p,stroke=0,fill=0)
    image('X33.jpg',x,t,w,h);c.restoreState()
    text('Professional Profile' if en else 'Perfil Profesional',207,99,15.2,'M-Bold')
    profile=root.one(id='perfil').one(cls='profile-text')
    content=' '.join(escape(p.text()) for p in profile.find(tag='p'))
    # Keep every current profile statement, including ShowHeroes and AI workflows.
    content=content.replace('Designer en ShowHeroes Group','<b>Designer en ShowHeroes Group</b>').replace('Designer at ShowHeroes Group','<b>Designer at ShowHeroes Group</b>')
    para(content,207,126,335,8.5,11.2,maxh=98)
    # Contact strip: the original asset includes the phone/mail/location icons.
    image('X29.png',207,244,348,35)
    text('+57 305 761 6657',239,257,6.7,'M-Medium',colors.white)
    text('sergiocr9991@gmail.com',342,257,6.5,'M-Medium',colors.white)
    text('Bogotá, Colombia',474,257,6.7,'M-Medium',colors.white)
    link('tel:+573057616657',213,247,113,29);link('mailto:sergiocr9991@gmail.com',328,247,132,29)
    # Education uses the same two-column structure and date capsules.
    section('Education' if en else 'Educación',296)
    for edu,x in zip(root.one(id='educacion').find(cls='edu'),[25,305]):
        label=edu.one(cls='pill').text()
        badge(label,x,323,116 if '2026' in label else 95)
        title=edu.one(tag='h3').text();school=edu.one(tag='h4').text()
        para(escape(title),x+127,321,137,8.1,10,maxh=31,bold=True)
        para(escape(school),x,353,260,7.8,10,maxh=21,color=MUTED)
        para(escape(edu.one(tag='p').text()),x,371,260,8.1,10.5,maxh=43)
    # Four current roles, in chronological reading order.
    section('Professional Experience' if en else 'Experiencia laboral',414)
    jobs=root.one(id='experiencia').find(cls='job-card')
    dates_en=['NOV 2026 - PRESENT','JAN 2025 - OCT 2026','MAY 2024 - JAN 2025','AUG 2023 - JAN 2024']
    dates_es=['NOV 2026 - ACTUALIDAD','ENE 2025 - OCT 2026','MAY 2024 - ENE 2025','AGO 2023 - ENE 2024']
    for i,job in enumerate(jobs):
        x=[25,305][i%2];t=437 if i<2 else 553
        badge((dates_en if en else dates_es)[i],x,t,149)
        para(escape(job.one(tag='h3').text()),x,t+21,260,9,11,maxh=13,bold=True)
        para(escape(job.one(tag='h4').text()),x,t+36,260,7.6,9.5,maxh=11,color=MUTED)
        para(escape(job.one(tag='p').text()),x,t+50,260,7.8,9.8,maxh=61 if i<2 else 51)
    # Original software icon artwork, with live text labels and AI skill.
    mini_heading('Software' if en else 'Herramientas',25,661,256)
    icons=Image.open(assets/'X80.png').convert('RGBA')
    crops=[(8,61,137,191),(155,61,285,191),(304,61,434,191),(8,202,137,332),(155,202,285,332),(304,202,434,332)]
    labels=['Photoshop','Illustrator','After Effects','Premiere Pro','Figma','InDesign']
    for i,(crop,label) in enumerate(zip(crops,labels)):
        ix=51+(i%3)*78;it=687+(i//3)*59
        c.drawImage(ImageReader(icons.crop(crop)),ix,H-it-39,39,39,mask='auto')
        text(label,ix+19.5,it+42,7.2,'M-SemiBold',align='center')
    text('AI-assisted design' if en else 'IA aplicada al diseño',157,806,7.2,'M-Medium',BLUE,'center')
    # Language rings and portfolio/contact retain the supplied visual hierarchy.
    mini_heading('Languages' if en else 'Idiomas',305,661,257)
    for cx,value,label in [(385,'B2','ENGLISH' if en else 'INGLÉS'),(469,'NATIVE' if en else 'NATIVO','SPANISH' if en else 'ESPAÑOL')]:
        image('X61.png',cx-22,688,44,44)
        text(value,cx,700 if value=='B2' else 706.5,13 if value=='B2' else 6.5,'M-Bold',align='center')
        text(label,cx,736,8.2,'M-SemiBold',align='center')
    mini_heading('Contact' if en else 'Contacto',305,757,257)
    image('X70.png',352,778,201,33)
    text('Portfolio' if en else 'Portafolio',447,780,18.5,'M-Bold',colors.white,'center')
    site='https://sergiocr9991-beep.github.io/CV-Sergio-Coll/'+('en/' if en else '')
    link(site,352,778,201,33)
    # Social links remain selectable and clickable under the portfolio button.
    text('LinkedIn',353,814,7.1,'M-SemiBold',BLUE);link('https://www.linkedin.com/in/sergiocr99/',351,812,59,12)
    text('Behance',430,814,7.1,'M-SemiBold',BLUE);link('https://www.behance.net/Sergio_cr',428,812,58,12)
    text('YouTube',505,814,7.1,'M-SemiBold',BLUE);link('https://www.youtube.com/@sergioramirez6791/videos',503,812,57,12)
    for i in range(6):
        x=6+i*16.5;p=c.beginPath();p.moveTo(x,H-841);p.lineTo(x+12,H-816);p.lineTo(x+21,H-816);p.lineTo(x+9,H-841);p.close();c.setFillColor(LIGHTBLUE if i%2 else BLUE);c.drawPath(p,fill=1,stroke=0)
    rect(112,825,W-112,17,BLUE)
    c.showPage();c.save()

if __name__=='__main__':
    base=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parent.parent
    assets=Path(sys.argv[2]) if len(sys.argv)>2 else base/'assets/cv/design'
    output=base/'assets/cv';output.mkdir(parents=True,exist_ok=True)
    for lang,relative in [('es','index.html'),('en','en/index.html')]:
        source=base/relative
        dest=output/f'Sergio-Coll-Ramirez-CV-{lang.upper()}.pdf'
        create_cv(source,dest,lang,assets);print(dest)
