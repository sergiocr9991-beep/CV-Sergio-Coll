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
        round_gradient(x,t,w,20,8)
        text(label,x+w/2,t+4.8,8.2,'M-Medium',colors.white,'center')
    # The blue edge bands and diagonal strokes follow the supplied originals.
    rect(0,14,484,17,BLUE)
    for i in range(6):
        x=487+i*16.5;p=c.beginPath();p.moveTo(x,H-39);p.lineTo(x+8,H-14);p.lineTo(x+17,H-14);p.lineTo(x+9,H-39);p.close();c.setFillColor(LIGHTBLUE if i%2==0 else BLUE);c.drawPath(p,fill=1,stroke=0)
    text('Sergio Coll Ramírez',32,15.2,11.7,'M-Bold',colors.white)
    text('CV / EN' if en else 'CV / ES',446,18,6.6,'M-Medium',colors.white)
    c.setFillColor(MUTED);c.circle(28,H-51,2.8,fill=1,stroke=0);line(35,51,57,51,color=MUTED)
    tagline='Graphic Designer | Digital Design & Motion Graphics' if en else 'Diseñador Gráfico | Diseño Digital & Motion Graphics'
    text(tagline,64,44,10.1,'M-Medium',BLUE,tracking=.5)
    # Profile frame, with the original portrait and asymmetric clipping.
    c.setStrokeColor(BLUE);c.setLineWidth(.7);c.roundRect(122,H-195,440,130,10,fill=0,stroke=1)
    c.saveState();p=c.beginPath();x,t,w,h=33,65,98,123;y=H-t-h
    p.moveTo(x,y+h);p.lineTo(x+w-42,y+h);p.curveTo(x+w-15,y+h,x+w,y+h-15,x+w,y+h-42);p.lineTo(x+w,y);p.lineTo(x+42,y);p.curveTo(x+15,y,x,y+15,x,y+42);p.close();c.clipPath(p,stroke=0,fill=0)
    image('X33.jpg',x,t,w,h);c.restoreState()
    text('Professional Profile' if en else 'Perfil Profesional',167,76,14,'M-SemiBold')
    profile=root.one(id='perfil').one(cls='profile-text')
    content=' '.join(escape(p.text()) for p in profile.find(tag='p'))
    # Keep every current profile statement, including ShowHeroes and AI workflows.
    content=content.replace('Designer en ShowHeroes Group','<b>Designer en ShowHeroes Group</b>').replace('Designer at ShowHeroes Group','<b>Designer at ShowHeroes Group</b>')
    para(content,167,101,382,8.8,11.8,maxh=86)
    # Contact strip: the original asset includes the phone/mail/location icons.
    round_gradient(33,207,529,26,10)
    text('+57 305 761 6657',48,214,8.1,'M-Medium',colors.white)
    text('sergiocr9991@gmail.com',213,214,8.1,'M-Medium',colors.white)
    text('Bogotá, Colombia',441,214,8.1,'M-Medium',colors.white)
    link('tel:+573057616657',43,208,138,24);link('mailto:sergiocr9991@gmail.com',207,208,192,24)
    # Four current roles, in chronological reading order.
    section('Professional Experience' if en else 'Experiencia laboral',249,x=33,width=529,size=14)
    jobs=root.one(id='experiencia').find(cls='job-card')
    dates_en=['Nov 2026 - Present','Jan 2025 - Oct 2026','May 2024 - Jan 2025','Aug 2023 - Jan 2024']
    dates_es=['Nov 2026 - Actualidad','Ene 2025 - Oct 2026','May 2024 - Ene 2025','Ago 2023 - Ene 2024']
    # Concise wording retains each role's current responsibilities and avoids
    # repeating generic phrases so the body can use larger type and leading.
    briefs_en=[
        'CTV, OLV and interactive ads: visual and audiovisual concepts, production and adaptation, motion graphics and multi-platform animation in collaboration with creative teams.',
        'Graphics, motion graphics and audiovisual content for digital and internal channels. Promotional videos and animations with consistent branding and multi-format adaptation.',
        'Graphic, animated and audiovisual assets for social media, commercial campaigns and email marketing, aligned with brand and communication objectives.',
        'Graphic and audiovisual production and adaptation for digital formats, social media and internal communications; institutional campaigns, photography and animation.'
    ]
    briefs_es=[
        'Creatividades para CTV, OLV y anuncios interactivos. Conceptualización, producción y adaptación visual y audiovisual; motion graphics y animación multiformato en colaboración con equipos creativos.',
        'Gráficos, motion graphics y contenido audiovisual para canales digitales y comunicación interna. Animaciones y videos promocionales con coherencia de marca y adaptación multiformato.',
        'Piezas gráficas, animadas y audiovisuales para redes, campañas comerciales y email marketing, alineadas con los objetivos de comunicación y la marca.',
        'Adaptación y producción gráfica y audiovisual para formatos digitales, redes y comunicación interna; campañas institucionales, fotografía y animación.'
    ]
    for i,job in enumerate(jobs):
        x=[33,313][i%2];t=277 if i<2 else 408
        badge((dates_en if en else dates_es)[i],x,t,166)
        para(escape(job.one(tag='h3').text()),x,t+29,249,9.5,12,maxh=13,bold=True)
        para(escape(job.one(tag='h4').text()),x,t+47,249,8.3,10.8,maxh=12,color=MUTED)
        para(escape((briefs_en if en else briefs_es)[i]),x,t+66,249,8.7,12,maxh=61 if i<2 else 49)
    # Education uses the same two-column structure and date capsules.
    section('Education' if en else 'Educación',530,x=33,width=529,size=14)
    for edu,x in zip(root.one(id='educacion').find(cls='edu'),[33,313]):
        label=edu.one(cls='pill').text()
        badge(label,x,556,126 if '2026' in label else 104)
        title=edu.one(tag='h3').text();school=edu.one(tag='h4').text()
        para(escape(title),x,586,249,9.1,11.8,maxh=25,bold=True)
        para(escape(school),x,617,249,8.4,10.8,maxh=12,color=MUTED)
        summary=(('AI applied to creative processes, digital experiences and design innovation.' if en else 'IA aplicada a procesos creativos, experiencias digitales e innovación en diseño.') if '2026' in label else ('Visual communication, digital design, multimedia and editorial design.' if en else 'Comunicación visual, diseño digital, multimedia y editorial.'))
        para(summary,x,638,249,8.7,11.6,maxh=24)
    # Original software icon artwork with live text labels.
    section('Software' if en else 'Herramientas',683,x=33,width=194,size=12.8)
    icons=Image.open(assets/'X80.png').convert('RGBA')
    crops=[(8,61,137,191),(155,61,285,191),(304,61,434,191),(8,202,137,332),(155,202,285,332),(304,202,434,332)]
    labels=['Photoshop','Illustrator','After Effects','Premiere Pro','Figma','InDesign']
    for i,(crop,label) in enumerate(zip(crops,labels)):
        ix=40+(i%3)*65;it=710+(i//3)*55
        c.drawImage(ImageReader(icons.crop(crop)),ix,H-it-32,32,32,mask='auto')
        text(label,ix+16,it+38,7.2,'M-Medium',align='center')
    # Language rings and portfolio/contact retain the supplied visual hierarchy.
    text('Languages' if en else 'Idiomas',246,683,12.8,'M-Bold')
    for top,value,label in [(715,'B2','English' if en else 'Inglés'),(772,'Native' if en else 'Nativo','Spanish' if en else 'Español')]:
        text(label,246,top,8.7,'M-Medium')
        badge(value,246,top+17,75)
    section('Contact' if en else 'Contacto',683,x=358,width=204,size=12.8)
    round_gradient(358,714,204,32,12)
    text('Portfolio' if en else 'Portafolio',460,720,16,'M-SemiBold',colors.white,'center')
    site='https://sergiocr9991-beep.github.io/CV-Sergio-Coll/'+('en/' if en else '')
    link(site,358,714,204,32)
    # Stacked icon-and-address rows follow the original contact reference.
    rows=[('linkedin','linkedin.com/in/sergiocr99','https://www.linkedin.com/in/sergiocr99/',colors.HexColor('#0077b5')),
          ('behance','behance.net/Sergio_cr','https://www.behance.net/Sergio_cr',colors.HexColor('#191919')),
          ('youtube','youtube.com/@sergioramirez6791','https://www.youtube.com/@sergioramirez6791/videos',colors.HexColor('#e52424'))]
    for i,(platform,address,url,fill) in enumerate(rows):
        x,t,size=358,755+i*23,16
        c.setFillColor(fill);c.roundRect(x,H-t-size,size,size,2,fill=1,stroke=0)
        if platform=='linkedin':text('in',x+8,t+.5,12,'M-Bold',colors.white,'center')
        elif platform=='behance':text('Bē',x+8,t+1.5,10,'M-Bold',colors.white,'center')
        else:
            c.setFillColor(colors.white);p=c.beginPath();p.moveTo(x+6,H-t-4);p.lineTo(x+6,H-t-12);p.lineTo(x+12,H-t-8);p.close();c.drawPath(p,fill=1,stroke=0)
        text(address,x+24,t+3.0,7.6,'M-Medium',INK)
        link(url,x-2,t-2,208,20)
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
