from pathlib import Path
from xml.etree import ElementTree as ET
from math import hypot
from random import Random
from contextlib import contextmanager
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import subprocess
out=Path(os.environ.get('EMOBRAIN_FIGURE_OUT', Path(__file__).resolve().parents[1]))
W,H=1440,650
for key,name in [('reg','Arial.ttf'),('bold','Arial Bold.ttf'),('italic','Arial Italic.ttf')]:
    font = Path(os.environ.get('EMOBRAIN_FIGURE_ARIAL', '/System/Library/Fonts/Supplemental')) / name
    pdfmetrics.registerFont(TTFont(key, str(font)))
ink='#183646'; muted='#415C68'; white='#FFFFFF'; bg='#F6FAFA'; line='#BCD0D2'
blue='#236980'; dark='#19566B'; bluefill='#E1EFF2'; bluehi='#85B9C8'
red='#A7462E'; blush='#FBE9DF'; coral='#DA8365'
green='#226B60'; sea='#91C1AD'; mint='#E7F3EB'
violet='#665783'; lilac='#EDEAF4'; gold='#875B1B'; sand='#FAEBCA'; yellow='#E7BD64'
def el(tag,**kwargs):return ET.SubElement(group,tag,{k.replace('_','-'):str(v) for k,v in kwargs.items() if v is not None})
def grp(name):
    global group
    group=ET.SubElement(svg,'g',id=name)
def style(fill,stroke,w,dash=None):
    c.setFillColor(HexColor(fill or white));c.setStrokeColor(HexColor(stroke or white));c.setLineWidth(w)
    c.setDash(dash or []);c.setLineCap(1);c.setLineJoin(1)
def rect(x,y,w,h,fill=None,stroke=None,sw=1,rx=0):
    style(fill,stroke,sw)
    c.roundRect(x,H-y-h,w,h,rx,fill=int(fill is not None),stroke=int(stroke is not None))
    el('rect',x=x,y=y,width=w,height=h,rx=rx,fill=fill or 'none',stroke=stroke or 'none',stroke_width=sw)
def ell(x,y,r,fill,stroke=None,sw=1):
    style(fill,stroke,sw);c.circle(x,H-y,r,fill=int(fill is not None),stroke=int(stroke is not None))
    el('circle',cx=x,cy=y,r=r,fill=fill or 'none',stroke=stroke or 'none',stroke_width=sw)
def path(pts,color=ink,width=1.35,dash=None,fill=None):
    style(fill,color,width,dash);p=c.beginPath();p.moveTo(pts[0][0],H-pts[0][1])
    for x,y in pts[1:]:p.lineTo(x,H-y)
    if fill:p.close()
    c.drawPath(p,fill=int(bool(fill)),stroke=int(bool(color)))
    el('polygon' if fill else 'polyline',points=' '.join(f'{x:.2f},{y:.2f}' for x,y in pts),fill=fill or 'none',stroke=color or 'none',stroke_width=width,stroke_linecap='round',stroke_linejoin='round',stroke_dasharray=' '.join(map(str,dash)) if dash else None)
def arr(pts,color=ink,width=1.45,dash=None,s=6):
    x,y=pts[-1];a,b=pts[-2];d=hypot(x-a,y-b);u,v=(x-a)/d,(y-b)/d
    bx,by=x-u*s,y-v*s
    path(pts[:-1]+[(bx+.1*u,by+.1*v)],color,width,dash)
    path([(x,y),(bx-v*s*.48,by+u*s*.48),(bx+v*s*.48,by-u*s*.48)],None,0,fill=color)
def txt(x,y,s,sz=16,f='reg',color=ink,ha='left'):
    w=pdfmetrics.stringWidth(s,f,sz)
    dx={'left':0,'mid':w/2,'end':w}[ha]
    if x-dx<-1 or x-dx+w>W+1:raise ValueError((s,x-dx,x-dx+w))
    c.setFillColor(HexColor(color));c.setFont(f,sz);c.drawString(x-dx,H-y,s)
    el('text',x=x,y=y,font_family='Arial, Helvetica, sans-serif',font_size=sz,font_weight='700' if f=='bold' else '400',font_style='italic' if f=='italic' else None,text_anchor={'left':'start','mid':'middle','end':'end'}[ha],fill=color).text=s
def mid(x,y,s,sz=16,f='reg',color=ink):txt(x,y,s,sz,f,color,'mid')
def start(name,title,desc,height=650):
    global c,svg,group,H
    H=height
    wpt=15*72
    c=Canvas(str(out/(name+'.pdf')),pagesize=(wpt,wpt*H/W),initialFontName='reg')
    c.scale(wpt/W,wpt/W);c.setTitle(title);c.setSubject(desc)
    svg=ET.Element('svg',{'xmlns':'http://www.w3.org/2000/svg','width':'15in','height':f'{15*H/W}in','viewBox':f'0 0 {W} {H}','role':'img','aria-labelledby':'title desc'})
    ET.SubElement(svg,'title',id='title').text=title
    ET.SubElement(svg,'desc',id='desc').text=desc
    group=svg;rect(0,0,W,H,white)
def end(name):
    c.showPage();c.save();ET.indent(svg,space='  ');ET.ElementTree(svg).write(out/(name+'.svg'),encoding='utf-8',xml_declaration=True)
    subprocess.run(['pdftoppm', '-singlefile', '-png', '-r', '210', str(out/(name+'.pdf')), str(out/name)], check=True)

@contextmanager
def local(x,y,sc=1):
    global group
    prev=group
    group=el('g',transform=f'translate({x},{y}) scale({sc})')
    c.saveState();c.translate(x,H-y);c.scale(sc,sc);c.translate(0,-H)
    try:yield
    finally:c.restoreState();group=prev
def bez(parts,fill=None,stroke=None,sw=1,dash=None):
    style(fill,stroke,sw,dash);p=c.beginPath()
    for op,*a in parts:
        if op=='M':p.moveTo(a[0],H-a[1])
        elif op=='L':p.lineTo(a[0],H-a[1])
        elif op=='C':p.curveTo(a[0],H-a[1],a[2],H-a[3],a[4],H-a[5])
        elif op=='Z':p.close()
    c.drawPath(p,fill=int(bool(fill)),stroke=int(bool(stroke)))
    el('path',d=' '.join(str(v) for row in parts for v in row),fill=fill or 'none',stroke=stroke or 'none',stroke_width=sw,stroke_linecap='round',stroke_linejoin='round',stroke_dasharray=' '.join(map(str,dash)) if dash else None)
def label(x,y,s,size=22,col=ink): mid(x,y,s,size,'bold',col)
def sub(x,y,s,size=18,col=muted):mid(x,y,s,size,'reg',col)
def title(x,y,s):txt(x,y,s,36,'bold',ink)
def edge(pts,col=ink,dash=None):arr(pts,col,2.3,dash,10)
def straight(x1,x2,y,col=ink):edge([(x1,y),(x2,y)],col)
def plus(x,y):
    ell(x,y,14,white,blue,2);path([(x-6,y),(x+6,y)],blue,2);path([(x,y-6),(x,y+6)],blue,2)
def block(x,y,w,h,lab,lab2='',fill=bluefill,col=blue,sz=22):
    rect(x,y,w,h,fill,col,1.7,7)
    label(x+w/2,y+h/2+(8 if not lab2 else -1),lab,sz,col)
    if lab2:sub(x+w/2,y+h/2+24,lab2,17,col)
def tube(x,y,sc=1):
    with local(x,y,sc):
        path([(0,22),(33,1),(113,1),(80,22)],blue,1.5,fill='#B3D1D6')
        path([(80,22),(113,1),(113,53),(80,74)],blue,1.5,fill='#92B9C5')
        rect(0,22,80,52,bluefill,blue,1.4)
        for i in (1,2,3):
            path([(20*i,22),(20*i+33,1)],blue,1)
            path([(20*i,22),(20*i,74)],blue,.8)
        path([(0,48),(80,48),(113,27)],blue,.8)
        path([(17,11),(96,11),(96,63)],blue,.8)
def video_frame(x,y,step=0,sc=1):
    with local(x,y,sc):
        rect(0,0,174,100,'#E7F0EC',ink,1.6,1)
        ell(130,20,9,'#EDD9A7')
        bez([('M',1,53),('C',24,48,39,32,60,33),('C',83,33,90,48,115,41),('C',136,32,155,37,173,29),('L',173,65),('L',1,65),('Z',)],'#AFCDC2')
        bez([('M',1,61),('C',27,50,51,48,78,54),('C',112,63,130,44,173,49),('L',173,88),('L',1,88),('Z',)],'#7EAA93')
        bez([('M',1,68),('C',48,65,79,81,114,67),('C',137,59,153,63,173,60),('L',173,99),('L',1,99),('Z',)],'#D8C9A9')
        for tx,ty in [(8,53),(16,51),(148,57),(153,55),(166,54)]:
            path([(tx-4,ty),(tx,ty-15),(tx+4,ty)],None,0,fill='#598372');path([(tx,ty),(tx,ty+5)],'#66816F',1)
        # A single illustrated clip; limb positions change between frames.
        dx=12*step
        with local(70+dx,38,.88):
            ell(18,2,4.2,ink);path([(16,9),(11,17),(8,23)],dark,6)
            path([(13,12),(20,18),(29,12+step*2)],ink,3.4);path([(13,13),(6,8),(-2,16)],dark,3.4)
            path([(8,24),(18,29+step),(25-step*4,43)],ink,4)
            path([(8,24),(-1,35-step*2),(-14,32+step*4)],ink,4)
        with local(18+dx*.85,62,1):
            bez([('M',4,7),('C',8,3,16,2,23,4),('L',29,0),('L',29,-5),('L',33,-3),('L',35,0),('L',40,2),('L',39,5),('L',34,6),('L',30,12),('L',18,12),('L',8,13),('Z',)],'#78553C')
            path([(7,8),(0,6),(-4,1)],'#78553C',2.8);path([(28,9),(33+step,15),(38,16+step)],'#78553C',2.7)
            path([(10,11),(7,17),(-1+2*step,19)],'#78553C',2.7)
def film(x,y,sc=1):
    with local(x,y,sc):
        for j in (2,1,0):video_frame(j*15,-j*12,j,.95)
def sheets(x,y,w=176,h=73,count=5):
    for j in range(count-1,0,-1):rect(x+j*5,y-j*5,w,h,'#C6E1E6',blue,1.4,6)
    rect(x,y,w,h,dark,blue,1.6,6)
    label(x+w/2,y+h/2+6,'VideoMAE',26,white)
def vector(x,y,color,light,n=9,dx=10,height=45):
    for j in range(n):
        rect(x+j*dx,y,dx-2,height,light,color,.9,1)
        for k in (1,2):path([(x+j*dx+1,y+k*height/3),(x+j*dx+dx-3,y+k*height/3)],color,.6)
def fragments(x,y,sc=1):
    with local(x,y,sc):
        for xx in (3,46,110):
            vector(xx,0,red,blush,4,8,43)
            path([(xx+1,49),(xx+1,54),(xx+29,54),(xx+29,49)],red,1.1)
        for q in (85,92,99):ell(q,22,1.6,red)
def mat(x,y,w,h,col,fill,nx=9,ny=6):
    rect(x,y,w,h,fill,col,1.3,1)
    for i in range(1,nx):path([(x+i*w/nx,y),(x+i*w/nx,y+h)],col,.75)
    for j in range(1,ny):path([(x,y+j*h/ny),(x+w,y+j*h/ny)],col,.75)
def rdm(x,y,size,col,light):
    n=6;a=size/n
    for i in range(n):
        for j in range(n):
            rect(x+j*a,y+i*a,a,a,white if i==j else light if j>i else '#F5F7F6',col,.42)
    rect(x,y,size,size,None,col,1.2)
def brain_outline(x,y,s=1):
 def P(a):
  return tuple([a[0]]+[x+n*s if i%2==0 else y+n*s for i,n in enumerate(a[1:])])
 outline=[('M',8,49),('C',0,38,5,24,18,18),('C',24,6,42,3,49,5),('C',65,-1,84,5,94,11),('C',110,15,119,32,116,44),('C',114,58,104,62,93,61),('C',87,68,78,69,70,64),('C',63,65,58,73,49,71),('C',41,69,38,62,33,59),('C',24,62,11,59,8,49),('Z',)]
 bez([P(a) for a in outline],lilac,violet,1.7*s)
 grooves=[
 [('M',11,38),('C',17,29,25,41,32,33),('C',38,27,39,21,47,21)],
 [('M',18,49),('C',28,51,34,45,40,46),('C',49,49,55,43,61,37),('C',68,32,73,30,83,30)],
 [('M',49,8),('C',51,17,47,23,45,30),('C',44,34,45,38,40,40)],
 [('M',65,7),('C',70,14,61,21,64,29)], [('M',78,13),('C',82,19,74,20,75,25)],
 [('M',32,17),('C',31,22,26,21,23,26)], [('M',95,17),('C',99,20,92,24,93,30),('C',95,36,104,36,111,32)],
 [('M',45,58),('C',56,62,58,52,67,49),('C',78,44,79,40,91,42),('C',101,45,103,41,110,43)],
 [('M',62,60),('C',72,60,77,51,87,51)], [('M',98,54),('C',101,50,107,51,110,47)]]
 for part in grooves:bez([P(a) for a in part],None,'#A79AB8',1.05*s)
def brain(x,y,sc=1):
    brain_outline(x, y, sc)
    with local(x,y,sc):
        bez([('M',70,40),('C',75,35,83,33,88,35),('L',88,41),('C',81,43,76,47,70,47),('Z',)],'#AB97C4',violet,1)
def lock(x,y):
    rect(x,y+10,18,14,gold,None,0,2)
    bez([('M',x+3,y+10),('L',x+3,y+6),('C',x+3,y-2,x+15,y-2,x+15,y+6),('L',x+15,y+10)],None,gold,2)
def bank(x,y):
    for h in range(12):
        w=12;xx=x+h*19
        rect(xx,y,w,47,blush if h==5 else bluefill,red if h==5 else blue,1.5,2)
        for i in (1,2,3):path([(xx+1,y+47*i/4),(xx+w-1,y+47*i/4)],red if h==5 else blue,.6)
def header(title_,sub_):
    title(38,56,title_);txt(39,90,sub_,21,'reg',muted)
def maskgrid(x,y,size=135):
    s=size/12
    mask=set(Random(117).sample(range(144),72))
    for k in range(144):
        i,j=divmod(k,12);rect(x+j*s,y+i*s,s-1,s-1,'#DCE9EC' if k not in mask else '#758F9B',white,.3)
    rect(x,y,size,size,None,blue,1.4)
def model():
    name='emobrain_videomae_methods'
    start(name,'From a video clip to 27 emotion ratings','A magnified encoder block identifies the exact intervention and extraction site.',645)
    header('From a video clip to 27 emotion ratings','VideoMAE ViT-B/16  |  Masked-video pretraining on VCE, followed by fine-tuning on its 27 continuous ratings.')
    grp('clip-to-prediction')
    film(43,170,.89)
    label(133,292,'Video clip');sub(133,320,'illustrated frames')
    straight(233,282,209)
    tube(302,164,1.09)
    label(364,292,'Tubelet embedding');sub(364,320,'2 frames × 16 × 16 pixels')
    straight(442,504,209)
    sheets(535,169,190,78,6)
    label(637,290,'12 encoder blocks');sub(637,318,'position added to input tokens')
    straight(764,820,209)
    vector(842,177,green,mint,12,11,58)
    label(907,291,'Pooled feature',22,green);sub(907,318,'token mean + LayerNorm')
    sub(907,158,'768 dimensions',18,green)
    straight(990,1037,209)
    path([(1052,169),(1177,188),(1177,230),(1052,249)],gold,1.8,fill=sand)
    label(1108,216,'Linear',22,gold);sub(1112,291,'768 → 27')
    straight(1189,1246,209)
    mat(1264,177,112,58,gold,sand,9,3)
    label(1316,291,'27 ratings',24,gold);sub(1316,318,'sigmoid per emotion')
    # Two leader lines are anchored to the actual encoder, not to a second model.
    path([(538,250),(507,267),(507,333),(392,356)],blue,1.25,[5,5])
    path([(726,250),(762,271),(762,332),(1010,356)],blue,1.25,[5,5])
    grp('expanded-block')
    rect(38,356,1364,253,'#F1F7F8','#91B5C0',1.45,12)
    txt(61,398,'Inside one encoder block',27,'bold',dark)
    txt(1378,396,'12 parallel heads per block  ×  12 blocks  =  144 heads',21,'bold',dark,'end')
    y=492
    edge([(66,y),(66,427),(947,427),(947,476)],'#7B989E')
    edge([(972,y),(972,427),(1302,427),(1302,476)],'#7B989E')
    for xx in (66,972):ell(xx,y,3,blue)
    straight(51,102,y)
    block(109,467,69,53,'LN',sz=22);straight(186,220,y)
    block(227,458,121,70,'Q, K, V',sz=22);straight(355,389,y)
    bank(400,469);label(510,457,'Head outputs',19,blue);sub(406,543,'1',17);sub(501,543,'h',18,red);sub(615,543,'12',17)
    straight(632,677,y);block(685,454,206,76,'Concat + project','768 → 768')
    straight(898,930,y);plus(947,y);straight(964,992,y)
    block(998,467,63,53,'LN',sz=22);straight(1069,1097,y)
    block(1101,454,155,76,'MLP','768 → 3072 → 768',sz=21);straight(1262,1285,y);plus(1302,y);straight(1320,1380,y)
    path([(508,521),(526,543),(526,560),(552,560)],red,1.65)
    txt(560,568,'One head = 64 values per token, before projection.',20,'bold',red)
    txt(63,590,'All heads use scaled dot-product self-attention.',17,'reg',muted)
    end(name)
def alignment():
    name='emobrain_regional_alignment'
    start(name,'Do the same videos elicit similar model and brain responses?','Match videos across modalities, then compare representational distances and predict regional voxels.',646)
    header('Do the same videos elicit similar model and brain responses?','One row per video, in the same order for the model and each participant’s region of interest.')
    grp('shared-stimuli')
    film(45,253,1.05)
    label(147,403,'Cowen videos');sub(147,430,'viewed during fMRI')
    straight(268,293,304);ell(295,304,4,ink)
    edge([(295,304),(295,195),(354,195)],blue)
    edge([(295,304),(295,421),(354,421)],violet)
    grp('paired-matrices')
    sheets(367,164,158,67,4)
    sub(450,264,'intact or head-masked',18,blue)
    brain(370,370,1.35)
    sub(449,498,'HK participant, one ROI',18,violet)
    straight(558,610,195,green);straight(552,610,423,violet)
    mat(630,158,127,75,green,mint)
    mat(630,386,127,75,violet,lilac)
    label(693,265,'Pooled features',21,green);sub(693,291,'videos × 768',17)
    label(693,494,'Voxel responses',21,violet);sub(693,520,'videos × voxels',17)
    # Two transforms of the same matrices. Colour-matched keyed connectors keep the lanes apart.
    grp('comparison')
    path([(763,195),(785,195),(785,305)],green,1.65)
    path([(763,423),(785,423),(785,305)],violet,1.65)
    path([(785,305),(811,305)],ink,1.8);ell(811,305,3.5,ink)
    edge([(811,305),(811,248),(851,248)],ink)
    edge([(811,305),(811,465),(851,465)],ink)
    txt(840,160,'RSA',26,'bold',ink)
    txt(840,192,'Compare distances between the same video pairs.',19,'reg',muted)
    rdm(865,214,67,green,mint);rdm(1199,214,67,violet,lilac)
    edge([(941,247),(981,247)],green);edge([(1189,247),(1149,247)],violet)
    label(1066,244,'Spearman',20);sub(1066,270,'correlation',18)
    sub(898,312,'Model RDM',17,green);sub(1234,312,'ROI RDM',17,violet)
    txt(840,383,'Encoding',26,'bold',ink)
    txt(840,415,'Fit a ridge from pooled features to voxel responses.',19,'reg',muted)
    vector(863,448,green,mint,7,10,34)
    straight(942,966,465,green);block(975,437,147,55,'Voxel ridge',fill=white,col=violet,sz=19)
    straight(1130,1166,465,violet);mat(1177,445,99,40,violet,lilac,8,4)
    sub(1077,521,'Score held-out voxel predictions with R².',18)
    grp('head-comparison')
    rect(38,556,1364,65,'#F3F7F6',None,0,6)
    txt(55,583,'Repeat both comparisons',20,'bold',ink)
    txt(55,607,'Intact model, selected heads masked, and matched random heads masked. Refit encoding for each condition.',18,'reg',muted)
    end(name)
def decoding():
    name='emobrain_brain_decoding'
    start(name,'Can fMRI recover the same features and predict emotion ratings?','The feature ridge and emotion readout are fitted on separate inputs and frozen at test time.',630)
    header('Can fMRI recover the same features and predict emotion ratings?','One participant and one emotion are shown. Repeat the readout for all 27 emotions.')
    grp('training')
    txt(315,153,'Fit the feature ridge',23,'bold',violet)
    txt(315,183,'Pair fMRI with the intact head outputs',18,'reg',muted)
    txt(315,209,'for the same training videos.',18,'reg',muted)
    edge([(420,230),(420,281)],violet,[4,5])
    txt(904,153,'Fit the emotion readout on VCE',23,'bold',gold)
    txt(904,183,'Pair intact head features with the',18,'reg',muted)
    txt(904,209,'corresponding human rating. Freeze this fit.',18,'reg',muted)
    edge([(1015,230),(1015,281)],gold,[4,5])
    grp('test')
    brain(48,275,1.55)
    label(147,426,'Regional fMRI',24,violet);sub(147,454,'one held-out video',18)
    straight(239,316,335,violet)
    block(327,295,192,84,'Feature ridge','one fit per participant',lilac,violet,23)
    straight(530,602,335,red)
    fragments(627,302,1.41)
    label(716,429,'Recovered features',23,red)
    sub(716,457,'K selected heads × 64 values',18)
    straight(825,912,335,red)
    block(922,295,191,84,'Fixed readout','one fit per emotion',sand,gold,23)
    lock(1082,270)
    straight(1126,1201,335,gold)
    # Individual prediction is shown explicitly as a scalar, with no fabricated numerical values.
    ell(1288,334,45,'#FFF7E3',gold,1.8);mid(1288,343,'ŷ',36,'italic',gold)
    label(1290,429,'Predicted rating',23,gold);sub(1290,457,'e.g., fear',18)
    grp('direct-comparison')
    path([(251,335),(251,511)],'#81939B',1.55);ell(251,335,2.7,violet)
    edge([(251,511),(329,511)],'#81939B')
    block(339,484,201,54,'Direct ridge',fill=white,col='#657B83',sz=21)
    edge([(553,511),(1202,511)],'#81939B')
    txt(1214,519,'Direct prediction',18,'reg',ink)
    txt(39,595,'Evaluate both paths on identical videos.',20,'bold',ink)
    txt(499,595,'HK cross-validation, followed by the 72 reserved MC videos.',20,'reg',muted)
    end(name)
if __name__=='__main__':
    model();alignment();decoding()
