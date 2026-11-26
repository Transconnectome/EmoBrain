from itertools import combinations
from style import (A, CAP, D, INK, L, LIGHT, LINE, LOW, MUTE, OBJ, OCHRE, ORANGE, OUT, PAPER, PEACH, R, SHARED, T, TEAL, W, YELLOW, film, plt, selected, subset)

def title(a,number,subject,sub):
    T(a,45,50,number,33,TEAL,True)
    T(a,124,50,subject,38,INK,True)
    T(a,125,96,sub,23,MUTE)
    L(a,[(45,125),(1655,125)],LINE,1)
def model(a):
    title(a,'3a','영상 모델 안에서 공포 예측에 기여하는 head를 찾는다',
          '여기서 한 층은 VideoMAE의 Transformer 블록 하나다. 영상 토큰은 1번부터 12번 블록을 차례로 지난다.')
    film(a,50,211,137,79);T(a,117,319,'영상 클립',21,INK,True,'center')
    A(a,201,251,231,251)
    for i in range(4):R(a,244+i*16,234,12,32,'#AFCDD4',TEAL,.8,2)
    T(a,277,306,'영상 토큰',20,INK,True,'center')
    A(a,314,251,370,251)
    T(a,390,159,'VideoMAE 인코더',24,TEAL,True)
    T(a,604,158,'작은 칸 하나가 head 하나다.    12개 블록 × 12개 head = 144개',21,MUTE)
    x0,step,bw=390,78,63
    for block in range(1,13):
        x=x0+(block-1)*step;hsel=selected.get(block,set())
        R(a,x,190,bw,105,PEACH if block==9 else LIGHT,ORANGE if block==9 else '#96B7BB',1.8 if block==9 else .9,7)
        T(a,x+bw/2,210,f'{block}층',18,ORANGE if block==9 else INK,True,'center')
        for j in range(12):
            row,col=divmod(j,4)
            R(a,x+8.5+12*col,231+14*row,9,10,ORANGE if j+1 in hsel else '#B3C9CD','none',r=1,z=4)
        if block<12:A(a,x+bw+1,251,x+step-2,251,'#708E97',.82)
        L(a,[(x+bw/2,296),(x+bw/2,329)],'#AFBEC1',.75,':')
        if hsel:
            for j in range(len(hsel)):D(a,x+bw/2+(j-(len(hsel)-1)/2)*14,343,5.6,ORANGE)
        else:T(a,x+bw/2,343,'0',15,'#7D8E95',False,'center')
    T(a,364,343,'선택한 head 수',19,ORANGE,True,'right')
    L(a,[(390,364),(1312,364)],LINE,.8)
    T(a,392,389,'가상 위치 예시',17,ORANGE,True)
    T(a,538,389,'3층에서 1개, 8층에서 1개, 9층에서 2개가 선택된 경우',20,MUTE)
    A(a,1319,251,1344,251)
    R(a,1352,216,117,73,'#E6F0EB','#94B4A5',.9,7)
    T(a,1411,239,'토큰 평균',19,INK,True,'center');T(a,1411,266,'+ 정규화',18,MUTE,False,'center')
    A(a,1475,251,1495,251)
    R(a,1503,208,149,88,YELLOW,'#D3B368',1,7)
    T(a,1578,236,'정서 출력층',22,OCHRE,True,'center')
    T(a,1578,268,'27개 평정 예측',19,INK,False,'center')
    # Zoom leader runs in the gap between blocks 9 and 10, outside the count dots.
    xx=x0+8*step+bw+5
    L(a,[(x0+8*step+bw,290),(xx,290),(xx,423),(1051,423),(1051,443)],ORANGE,1.1,(0,(3,3)))
    R(a,48,434,557,273,'#F3F7F7','none',r=12)
    T(a,72,466,'어떤 head를 주황색으로 표시하나?',25,TEAL,True)
    T(a,72,513,'학습 전에 따로 둔 VCE 검증 영상에서',22)
    T(a,72,545,'매번 다른 72개 head의 출력을 0으로 가린다.',22)
    T(a,72,586,'각 head를 남겼을 때와 가렸을 때의 공포 예측력을',22)
    T(a,72,618,'여러 영상에 걸쳐 비교해 기여 순위를 정한다.',22)
    L(a,[(72,645),(576,645)],LINE,.7)
    T(a,72,675,'새 영상에서 같은 층·같은 수의 무작위 제거와 비교한다.'.replace('층·같은','층에서 같은'),19,MUTE)
    R(a,650,439,1005,268,'#FFFBF8','#D8B1A0',1.1,12)
    T(a,680,471,'9층을 펼치면',25,ORANGE,True)
    T(a,880,471,'같은 토큰을 12개 head가 병렬로 처리한다.',22,INK)
    R(a,676,532,132,58,LIGHT,'#A3BFC3',.85,6)
    T(a,742,560,'8층의 토큰',21,INK,True,'center')
    A(a,815,560,861,560)
    for j in range(12):
        x=873+j*30; sel=j+1 in selected[9]
        R(a,x,522,24,75,ORANGE if sel else '#C7D9D9','none',r=2)
        T(a,x+12,559,str(j+1),14,PAPER if sel else TEAL,True,'center')
    A(a,1238,560,1264,560)
    R(a,1271,530,170,61,'#EDF2F2','#A6BDC1',.85,6)
    T(a,1356,548,'head 출력을 합쳐',18,INK,False,'center');T(a,1356,574,'투영한 뒤 MLP',19,INK,True,'center')
    A(a,1448,560,1482,560)
    R(a,1490,532,132,58,LIGHT,'#A3BFC3',.85,6);T(a,1556,560,'10층으로',21,INK,True,'center')
    L(a,[(975,602),(975,618),(1125,618),(1125,602)],ORANGE,1.05)
    T(a,1050,644,'주황색 4번과 9번의 출력',20,ORANGE,True,'center')
    T(a,1050,675,'토큰당 64개 값씩. 이 위치에서 읽거나 가린다.',20,MUTE,False,'center')
    T(a,48,736,'실제 분석은 정서마다 반복한다. 층 번호와 head 번호는 모델 내부의 위치를 뜻한다.',18,MUTE)

# Illustrative unique and shared components, in hundredths above the nuisance-only model.
sets=('L','O','S','LO','LS','OS','LOS')
parts={'fear':dict(zip(sets,[4,2,10,2,3,4,5])), 'head':dict(zip(sets,[10,2,5,3,3,2,3]))}
def gain(which,subset):
    return sum(amount for names,amount in parts[which].items() if set(subset)&set(names))
def fnum(i):return f'{i/100:.2f}'
def feat(a,x,y,letter,label,col,small):
    R(a,x,y-15,33,32,col,'none',r=5)
    T(a,x+16.5,y+1,letter,20,PAPER,True,'center')
    T(a,x+46,y+1,label,23,INK,True)
    T(a,x+46,y+35,small,20,MUTE)
def attribution(a):
    title(a,'3b','같은 일곱 조합으로 사람의 공포 평정과 head 반응을 각각 설명한다',
          '두 예측 대상은 따로 학습하고 같은 시험 영상에서 평가한다. 아래 수치는 방법을 설명하기 위한 가상 예시다.')
    T(a,48,162,'한 영상에서 얻는 세 묶음',24,TEAL,True)
    film(a,51,204,115,66)
    T(a,190,218,'Cowen 영상 예시',20,INK,True)
    T(a,190,252,'개가 사람을 쫓는다.',20,MUTE)
    feat(a,50,325,'L','저수준 시각',LOW,'영상에서 잰 밝기, 색, 움직임')
    feat(a,50,424,'O','물체 이름',OBJ,'사람 캡션의 구체 명사 “개, 사람”')
    feat(a,50,523,'S','전체 캡션',CAP,'“개가 사람을 쫓는다.”')
    T(a,96,593,'O와 S는 영상당 캡션 20개에서',18,MUTE)
    T(a,96,620,'고정 DeBERTa-large로 추출한다.',18,MUTE)
    L(a,[(402,148),(402,652)],LINE,1)
    T(a,431,163,'일곱 조합',24,TEAL,True)
    T(a,431,200,'색칠한 칸이 포함된 특징',18,MUTE)
    T(a,785,161,'사람의 공포 평정',23,OCHRE,True,'center')
    T(a,950,161,'3a의 선택 head',23,ORANGE,True,'center')
    T(a,785,195,'공포를 고른 비율',18,MUTE,False,'center')
    T(a,950,195,'Cowen 영상의 실제 출력',18,MUTE,False,'center')
    T(a,527,243,'L',21,LOW,True,'center');T(a,584,243,'O',21,OBJ,True,'center');T(a,641,243,'S',21,CAP,True,'center')
    T(a,785,243,'시험 R²',18,MUTE,False,'center');T(a,950,243,'시험 R²',18,MUTE,False,'center')
    L(a,[(431,262),(1027,262)],LINE,1)
    for i,s in enumerate(sets):
        y=291+48*i
        if i==6:R(a,429,y-21,599,43,'#EEF4F3','none',r=5)
        label={0:'단독',3:'둘씩',6:'모두'}.get(i)
        if label:T(a,435,y,label,19,TEAL,True)
        for cx,letter,co in [(527,'L',LOW),(584,'O',OBJ),(641,'S',CAP)]:
            R(a,cx-11,y-9.5,22,19,co if letter in s else PAPER,co if letter in s else '#D9E0E1',.85,3)
        T(a,785,y,fnum(gain('fear',s)),24,OCHRE,i==6,'center');T(a,950,y,fnum(gain('head',s)),24,ORANGE,i==6,'center')
        if i in [2,5]:L(a,[(431,y+24),(1027,y+24)],LINE,.75)
    T(a,433,631,'가상 R² 예시. 공통 변수만 쓴 기준 모형은 0.00으로 가정.',17,MUTE)
    L(a,[(1052,149),(1052,652)],LINE,1)
    T(a,1083,162,'각자 더한 몫과 함께 설명한 몫',24,TEAL,True)
    T(a,1083,206,'한 묶음의 고유분 = 전체 R² - 그 묶음을 뺀 R²',20,INK)
    T(a,1083,240,'색 막대는 왼쪽 표와 같은 가상 수치다.',18,MUTE)
    scale=1780;start=1086
    for key,y,label,cc in [('fear',304,'사람의 공포 평정',OCHRE),('head',428,'공포 예측에 기여한 head',ORANGE)]:
        T(a,start,y,label,21,cc,True)
        values=[parts[key][k] for k in ['L','O','S']]+[sum(parts[key][k] for k in sets if len(k)>1)]
        x=start
        for v,col in zip(values,[LOW,OBJ,CAP,SHARED]):
            w=v/100*scale;R(a,x,y+21,w,42,col,PAPER,1)
            T(a,x+w/2,y+42,fnum(v),17 if w<43 else 19,PAPER,True,'center');x+=w
        T(a,1624,y,'합계 '+fnum(sum(values)),20,INK,True,'right')
    for xx,c,t in [(1086,LOW,'L 고유'),(1204,OBJ,'O 고유'),(1326,CAP,'S 고유'),(1446,SHARED,'둘 이상 공유')]:
        R(a,xx,531,18,18,c,'none',r=2)
        T(a,xx+25,540,t,19,INK)
    T(a,1086,590,'공포 평정에서 S 고유분은 0.30 - 0.20 = 0.10.',20,CAP,True)
    T(a,1086,625,'나머지 두 고유분까지 빼면 공유분 0.14가 남는다.',19,MUTE)
    L(a,[(48,669),(1653,669)],LINE,.85)
    T(a,49,707,'공유분을 더 나누면',25,TEAL,True)
    T(a,49,751,'어떤 두 묶음이 겹쳤는지, 셋 모두 겹쳤는지 본다.',20,MUTE)
    T(a,49,780,'표에서 ‘둘만’은 세 묶음 공통분을 제외한 값이다.',18,MUTE)
    xs=[847,1022,1188,1355,1564]
    for x,hdr in zip(xs,['L과 O만','L과 S만','O와 S만','셋 모두','공유분 합계']):
        T(a,x,700,hdr,18,SHARED,True,'center')
    L(a,[(621,719),(1643,719)],LINE,.8)
    for key,y,label,cc in [('fear',740,'사람의 공포 평정',OCHRE),('head',774,'선택한 head 반응',ORANGE)]:
        T(a,624,y,label,18,cc,True)
        v=[parts[key][k] for k in ['LO','LS','OS','LOS']]
        for xi,val in enumerate(v+[sum(v)]):T(a,xs[xi],y,fnum(val),20,SHARED,xi==4,'center')
    T(a,49,818,'가상 예에서는 모든 몫이 양수다. 실제 분석은 음수 추정값도 보존한다. 공유분은 이 영상들에서 두 가지 이상의 측정치가 함께 설명한 몫이다.',17,MUTE)
def make(fs):
    hs=[758 if fun==model else 844 for fun in fs]
    full=sum(hs);fig=plt.figure(figsize=(17,full/100),facecolor=PAPER);top=0
    for h,fun in zip(hs,fs):
        top+=h;a=fig.add_axes([0,1-top/full,1,h/full]);a.set(xlim=(0,W),ylim=(h,0));a.set_axis_off();fun(a)
    return fig
for stem, draw in [('emobrain_head_layers', model), ('emobrain_head_captions', attribution)]:
    fig = make([draw])
    fig.savefig(OUT / (stem + '.svg'), facecolor=PAPER)
    fig.savefig(OUT / (stem + '.png'), dpi=200, facecolor=PAPER)
    fig.savefig(OUT / (stem + '.pdf'), facecolor=PAPER)
    plt.close(fig)
