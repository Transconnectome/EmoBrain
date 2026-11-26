from style import (A, D, H, INK, L, LC, LINE, LOW, MUTE, OBJ, OC, OUT, R, T, TEAL, W, plt)

W,H=1860,770
gold='#996118';sand='#FFF3DC';vio='#705586';pale='#F1ECF5';green='#1E7065';sea='#E6F3EF';navy='#23495A'
figdir=OUT
def begin():
    fig=plt.figure(figsize=(W/100,H/100),dpi=100,facecolor='white')
    a=fig.add_axes([0,0,1,1]);a.set(xlim=(0,W),ylim=(H,0));a.set_axis_off()
    return fig,a
def title(a,n,txt,sub):
    T(a,48,52,n,34,TEAL,True);T(a,182,52,txt,40,INK,True);T(a,182,109,sub,23,MUTE)
    L(a,[(48,147),(1812,147)],LINE,1)
def step(a,x,y,n,txt):
    D(a,x+20,y,21,navy);T(a,x+20,y,n,25,'white',True,'center');T(a,x+57,y,txt,31,INK,True)
def chip(a,x,y,w,txt,fill,col,size=22):
    R(a,x,y,w,45,fill,'none',r=7);T(a,x+w/2,y+23,txt,size,col,True,'center')
def export(fig,stem,svg=False):
    fig.savefig(figdir/(stem+'.png'),dpi=165,facecolor='white')
    fig.savefig(figdir/(stem+'.pdf'),facecolor='white')
    fig.savefig(figdir/(stem+'.svg'),facecolor='white')
    plt.close(fig)
fig,a=begin()
title(a,'그림 1','정서마다 어떤 단서가 기여하고, 같은 특징을 뇌에서도 읽을 수 있을까?',
      '① 영상만 배운 VideoMAE에 VCE 정서 평정을 추가로 학습한다.   ② head를 가려 27개 정서 각각의 예측에 기여한 head 목록을 고정한다.')
step(a,50,213,'3','자극 정보와 정서');step(a,674,213,'4','영역별 뇌 반응');step(a,1291,213,'6','뇌 단독 디코딩')
for x in (628,1245):
    L(a,[(x,250),(x,365)],LINE,.9);L(a,[(x,448),(x,624)],LINE,.9);A(a,x-19,409,x+19,409,TEAL,2)
T(a,50,277,'Cowen 영상과 사람이 쓴 캡션',23,MUTE)
chip(a,50,315,150,'저수준 시각',LC,LOW);chip(a,212,315,143,'물체 이름',OC,OBJ);chip(a,367,315,150,'전체 캡션',pale,vio)
T(a,50,401,'세 입력의 일곱 조합으로 각각 예측',25,INK,True)
R(a,52,447,6,34,sand,gold,r=2);T(a,72,464,'사람들이 매긴 해당 정서 평정',25,gold,True)
R(a,52,495,6,34,sea,green,r=2);T(a,72,512,'그 정서에 고른 head의 영상별 출력',25,green,True)
T(a,50,589,'각 입력이 더하는 몫과 서로 겹치는 몫',22,MUTE)
T(a,674,277,'같은 영상을 본 HK 참가자의 fMRI',23,MUTE)
chip(a,674,315,188,'선택 head만',sea,green);chip(a,875,315,164,'27개 평정만',sand,gold);chip(a,1050,315,143,'둘을 함께',pale,vio)
T(a,674,401,'세 모형 모두 같은 복셀 반응을 예측',25,INK,True)
T(a,674,465,'head 고유분   /   평정 고유분   /   공유분',25,navy,True)
T(a,674,516,'③의 캡션 고유분과 영역 간 차이도 비교',23,MUTE)
T(a,674,589,'⑤ 선택 head를 가려 영역 대응의 변화를 확인',22,MUTE)
T(a,1291,277,'새 영상의 입력은 참가자 fMRI뿐',23,MUTE)
chip(a,1291,315,110,'fMRI',LC,LOW);A(a,1410,337,1442,337,TEAL);chip(a,1453,315,290,'같은 head의 출력 복원',sea,green)
T(a,1291,401,'참가자별 ridge로 특징을 복원',25,INK,True)
T(a,1291,465,'복원 특징 → 고정된 VCE 정서 판독기',25,green,True)
T(a,1291,516,'영상당 27개 평정 예측',25,gold,True)
T(a,1291,589,'특징 복원과 평정 예측을 따로 평가',22,MUTE)
R(a,49,653,1762,79,'#F0F5F5',r=8)
T(a,71,693,'세 분석을 잇는 값',24,TEAL,True)
T(a,300,693,'한 정서에 고른 같은 head 출력이 ③에서는 설명할 대상, ④에서는 뇌를 예측하는 입력, ⑥에서는 뇌로 복원할 목표가 된다.',24,INK)
export(fig,'emobrain_ridge_overview')
fig,a=begin()
title(a,'그림 4a','모델 특징과 사람 평정은 뇌 반응의 어느 부분을 함께 설명할까?',
      '하나의 정서로 선택한 head 묶음에 대한 비교다. 27개 정서 각각에 반복하고, 참가자와 영역별로 새 영상의 예측력을 계산한다.')
T(a,52,212,'같은 훈련 영상에서 세 모형을 각각 적합',28,INK,True)
T(a,998,212,'같은 시험 영상에서 세 예측력을 비교',28,INK,True)
for i,(name,sub,c,fc) in enumerate([('선택 head만','해당 정서에 고른 head의 영상별 출력',green,sea),('27개 평정만','각 영상에서 정서별로 응답한 사람의 비율',gold,sand),('head와 평정 함께','두 입력을 나란히 사용',vio,pale)]):
    y=270+100*i
    chip(a,55,y,203,name,fc,c,22);T(a,279,y+23,sub,22,MUTE)
    A(a,697,y+23,749,y+23,c,1.2)
R(a,757,261,162,263,'#EFF4F5',LINE,1,8)
T(a,838,367,'같은 영역의',23,INK,True,'center');T(a,838,405,'복셀 반응',26,INK,True,'center')
A(a,930,390,978,390,TEAL,1.8)
for i,(label,expr,fc,col) in enumerate([('head 고유분','함께 쓴 R²  -  평정만 쓴 R²',sea,green),('평정 고유분','함께 쓴 R²  -  head만 쓴 R²',sand,gold),('공유분','head만 쓴 R²  +  평정만 쓴 R²  -  함께 쓴 R²',pale,vio)]):
    y=270+100*i
    chip(a,997,y,169,label,fc,col,22);T(a,1189,y+23,expr,24,INK,True)
T(a,55,588,'세 모형에 같은 참가자, 같은 복셀, 같은 시험 fold와 기준을 쓴다.',23,MUTE)
T(a,998,588,'공유분은 선택 head와 27개 평정 전체가 겹쳐 설명한 몫이다.',22,MUTE)
R(a,49,654,1762,77,'#F0F5F5',r=8)
T(a,72,693,'③과의 연결',24,TEAL,True)
T(a,267,693,'캡션이 head 출력을 더 설명하는 정서일수록, 연합 영역군과 시각 영역군의 head 고유분 차이도 커지는지 비교한다.',22,INK)
export(fig,'emobrain_roi_partition',True)
