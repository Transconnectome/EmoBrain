from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,FancyBboxPatch,Circle,Ellipse,FancyArrowPatch,Polygon
from matplotlib.font_manager import FontProperties
from matplotlib.backends.backend_pdf import PdfPages
from fontTools.ttLib import TTCollection
from fontTools import subset
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.cu2quPen import Cu2QuPen

import os
from tempfile import TemporaryDirectory
font_cache = TemporaryDirectory()
OUT = Path(os.environ.get('EMOBRAIN_FIGURE_OUT', Path(__file__).resolve().parents[1]))
W,H=1700,758
INK='#173746';MUTE='#506671';SOFT='#71818A';LINE='#CCD9DB';TEAL='#186F79'
LIGHT='#F0F6F6';PAPER='#FFFFFF';ORANGE='#AA4928';PEACH='#FCF0E9';OCHRE='#895B0C';YELLOW='#FFF4D7'
LOW='#376E96';OBJ='#287A68';CAP='#79598E';SHARED='#435967'
LC='#EAF2F7';OC='#E8F3EE';SC='#F2ECF6'
def fonts():
    chars=set(''.join(p.read_text() for p in Path(__file__).parent.glob('*.py')))|set('0123456789.+×−')
    faces={}
    for w,i,k in [('normal',0,400),('bold',6,700)]:
        font_file = os.environ.get('EMOBRAIN_FIGURE_FONT_' + w.upper())
        if font_file:
            faces[w] = FontProperties(fname=font_file, weight=w)
            continue
        collection = Path('/System/Library/Fonts/AppleSDGothicNeo.ttc')
        if not collection.is_file():
            raise FileNotFoundError('Set EMOBRAIN_FIGURE_FONT_NORMAL and EMOBRAIN_FIGURE_FONT_BOLD to Hangul TrueType fonts.')
        f=TTCollection(collection,lazy=True).fonts[i]
        s=subset.Subsetter();s.populate(text=''.join(chars));s.subset(f)
        fb=FontBuilder(f['head'].unitsPerEm,isTTF=True); order=f.getGlyphOrder();fb.setupGlyphOrder(order);fb.setupCharacterMap(f.getBestCmap())
        glyphs={};gs=f.getGlyphSet()
        for name in order:
            pen=TTGlyphPen(None);gs[name].draw(Cu2QuPen(pen,1,reverse_direction=True));glyphs[name]=pen.glyph()
        fb.setupGlyf(glyphs);fb.setupHorizontalMetrics(f['hmtx'].metrics)
        h=f['hhea'];o=f['OS/2'];fb.setupHorizontalHeader(ascent=h.ascent,descent=h.descent)
        style='Bold' if w=='bold' else 'Regular'
        fb.setupNameTable({'familyName':'Apple SD Gothic Neo','styleName':style,'psName':'AppleSDGothicNeo-'+style,'fullName':'Apple SD Gothic Neo '+style})
        fb.setupOS2(sTypoAscender=o.sTypoAscender,sTypoDescender=o.sTypoDescender,usWinAscent=o.usWinAscent,usWinDescent=o.usWinDescent,usWeightClass=k)
        fb.setupPost();face=Path(font_cache.name)/(w+'.ttf');fb.save(face)
        faces[w]=FontProperties(fname=str(face),family=['Apple SD Gothic Neo','Noto Sans KR','Malgun Gothic','sans-serif'],weight=w)
    return faces
FACE=fonts()
plt.rcParams.update({'svg.fonttype':'none','pdf.fonttype':42,'svg.hashsalt':'emobrain-f3-blocks-subsets'})
def T(a,x,y,s,sz=22,c=INK,b=False,ha='left',va='center'):
    return a.text(x,y,s,fontsize=.72*sz,fontproperties=FACE['bold' if b else 'normal'],color=c,ha=ha,va=va,zorder=8)
def R(a,x,y,w,h,fc='none',ec='none',lw=1,r=0,z=1):
    p=FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0,rounding_size='+str(r),facecolor=fc,edgecolor=ec,linewidth=lw,zorder=z)
    a.add_patch(p);return p
def L(a,points,c=LINE,lw=1.2,ls='-',z=3):
    a.plot(*zip(*points),color=c,lw=lw,ls=ls,solid_capstyle='round',solid_joinstyle='round',zorder=z)
def A(a,x,y,xx,yy,c=MUTE,lw=1.4):
    a.add_patch(FancyArrowPatch((x,y),(xx,yy),arrowstyle='-|>',mutation_scale=11,shrinkA=0,shrinkB=0,lw=lw,color=c,zorder=4))
def D(a,x,y,rad,fc,ec='none',lw=1,z=5):
    a.add_patch(Circle((x,y),rad,fc=fc,ec=ec,lw=lw,zorder=z))
def E(a,x,y,w,h,c,angle=0):
    a.add_patch(Ellipse((x,y),w,h,angle=angle,facecolor=c,edgecolor='none',zorder=5))

def film(a,x,y,w=141,h=84):
    R(a,x+7,y-8,w,h,'#E8F0F0','#C5D6D9',.8,4)
    R(a,x+3.5,y-4,w,h,'#F1F6F6','#C5D6D9',.8,4)
    R(a,x,y,w,h,'#E9F2F3','#AAC0C6',.9,4)
    def pos(xx,yy):return x+w*xx/140,y+h*yy/80
    def ln(pts,col,weight):L(a,[pos(*p) for p in pts],col,weight)
    s=w/140
    ln([(4,65),(135,65)],'#9BB9A9',1)
    xx,yy=pos(38,54);E(a,xx,yy,29*s,12*s,'#946446')
    xx,yy=pos(52,46);D(a,xx,yy,6*s,'#946446')
    ln([(52,46),(59,48)],'#946446',2.8*s);ln([(25,52),(17,45),(13,46)],'#946446',2*s)
    ln([(30,58),(23,65),(18,63)],'#946446',2.1*s);ln([(46,58),(55,65),(60,64)],'#946446',2.1*s)
    xx,yy=pos(100,24);D(a,xx,yy,5.7*s,'#AA7659')
    ln([(98,33),(91,47)],LOW,4.4*s);ln([(97,34),(104,40),(113,33)],LOW,2.4*s)
    ln([(91,48),(103,56),(110,64)],INK,2.9*s);ln([(91,48),(81,57),(73,50)],INK,2.9*s)

selected={3:{6},8:{2},9:{4,9}}
