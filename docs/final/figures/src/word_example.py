from style import (A, D, H, INK, L, LINE, MUTE, ORANGE, OUT, R, T, TEAL, W, film, plt)

from functools import partial
W,H=1600,700
fig=plt.figure(figsize=(W/100,H/100),dpi=100,facecolor='white')
a=fig.add_axes([0,0,1,1]);a.set(xlim=(0,W),ylim=(H,0));a.set_axis_off()
t=partial(T,a);r=partial(R,a);line=partial(L,a);arrow=partial(A,a);dot=partial(D,a)
gold='#926315';pur='#735987';blue='#246D82';green='#247867';gr='#D5DFE0'
t(48,46,"3c",34,TEAL,True);t(125,46,"‘쫓다’로 묘사된 영상에서, 사람과 모델과 뇌는 무엇을 공유할까?",38,INK,True)
t(126,94,"같은 영상에 붙은 캡션과 정서 평정, 그 영상을 본 모델과 참가자의 반응을 연결한다.",23,MUTE)
line([(48,125),(1552,125)],LINE,1.1)
for x,n,col,label in [(52,'1',pur,'사람의 캡션과 공포 평정'),(565,'2',ORANGE,'공포 예측에 기여한 head'),(1093,'3',blue,'같은 head와 실제 뇌 반응')]:
    dot(x+14,170,15,col);t(x+14,170,n,20,'white',True,'center');t(x+41,170,label,27,INK,True)
for x in [537,1065]:
    line([(x,200),(x,345)],gr,.8);line([(x,413),(x,563)],gr,.8);arrow(x-19,380,x+10,380,'#71949B',1.4)
film(a,55,247,140,80)
t(224,241,'“A dog chases a person.”',24,pur,True)
t(224,282,'이 영상의 캡션 20개 중',23,INK)
t(224,313,'‘쫓다’를 쓴 캡션 8개',23,INK)
for k in range(20):
    row,col=divmod(k,10);dot(72+18*col,375+row*20,6.1,pur if k<8 else '#E7E1EB')
t(268,383,'8 / 20 = 0.40',26,pur,True)
t(55,456,'같은 영상에서 공포를 고른 사람의 비율',23,INK,True)
t(55,510,'여러 영상에서 두 비율이',22,MUTE)
t(55,543,'함께 높고 낮아지는지 본다.',22,MUTE)
# visualise a set selected for fear and a member carried into the ROI model
t(567,233,'VCE 영상만 보고 27개 정서를 예측',23,INK,True)
t(567,274,'일부 head를 가려 공포 예측이 특히',22,MUTE)
t(567,304,'나빠지는 head 묶음을 고른다.',22,MUTE)
for i in range(10):
    xx=583+i*44
    col=ORANGE if i in [1,4,7] else '#D7E0E2'
    r(xx,358,26,37,col,'none',r=5)
    if i==4:r(xx-5,353,36,47,'none',pur,2.2,7,6)
line([(772,402),(772,424),(582,424)],pur,1.3)
t(567,456,'그중 ‘쫓다’ 묘사와 대응하는 head',23,pur,True)
t(567,510,'Cowen 영상에서 움직임과 물체를 고려해도',22,MUTE)
t(567,543,'단어 빈도가 새 영상의 출력을 설명하나?',22,MUTE)
t(1094,233,'head의 영상별 출력 64개',24,INK,True)
for i in range(9):r(1096+i*19,269,14,30,'#E7DDEE' if i%3 else '#A785B7','none',r=2)
t(1278,284,'…',25,pur,True);arrow(1309,284,1354,284,blue);r(1366,260,152,48,'#E8F2F5',blue,1,7);t(1442,284,'참가자별 ridge',20,blue,True,'center')
# Fork into two region examples, both drawn in identical neutral colours
line([(1442,310),(1442,331),(1218,331)],blue,1.2)
arrow(1218,331,1218,351,blue);arrow(1442,330,1442,351,blue)
for x,name in [(1100,'후두 시각 영역'),(1324,'측두두정 연합 영역')]:
    r(x,362,215,53,'#F3F8F9',gr,1,5);t(x+107.5,389,name,21,blue,True,'center')
t(1094,456,'새 영상의 실제 복셀 반응과 비교',23,INK,True)
t(1094,510,'영역마다 예측력을 구하고, 두 영역의',22,MUTE)
t(1094,543,'차이를 같은 참가자 안에서 비교한다.',22,MUTE)
r(49,601,1502,70,'#F0F5F5','none',r=8)
t(73,635,'읽는 법',21,TEAL,True)
t(183,635,'보라색 테두리는 두 기준을 통과한 head의 예다. 8/20과 영역 이름은 설명용이며, 실제 대응은 측정할 값이다.',22,INK)
figdir=OUT;stem='emobrain_chase_head_roi'
fig.savefig(figdir/(stem+'.png'),dpi=190,facecolor='white')
fig.savefig(figdir/(stem+'.pdf'),facecolor='white',metadata={'Title':"‘쫓다’와 공포 예측 head, 뇌 영역의 대응"})
fig.savefig(figdir/(stem+'.svg'),facecolor='white')
plt.close(fig)
