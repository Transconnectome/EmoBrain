# EmoBrain 구현 명세서 (Claude Code 용)

## 이 문서를 읽는 에이전트에게

이 문서는 EmoBrain framework를 구현하기 위한 설계 명세다. 이 문서를 바탕으로 코드베이스를 설계하고 구현하라. 아래 원칙을 지켜라.

* DECIDED로 표시된 것은 그대로 구현한다.
* OPEN으로 표시된 것은 하드코딩하지 말고 config로 노출하고, 기본값만 두되 바꿀 수 있게 한다.
* CAUTION으로 표시된 것은 흔한 오류다. 반드시 피한다.
* 각 모듈에는 완료 기준(Acceptance)이 있다. 그 기준을 만족해야 그 모듈이 끝난 것이다.
* 텐서 shape와 입출력 계약을 지킨다. 모듈 간 경계에서 shape를 assert로 검증하라.

용어와 shape 규약은 다음과 같다. B는 batch, N_b는 brain token 수, N_v는 video token 수, D_enc는 encoder 출력 차원, D_llm은 LLM hidden 차원, C=34는 감정 카테고리 수, S_b는 피험자 수(Horikawa 5, MindCaptioning 6)다.

---

## 1. 프로젝트 개요와 목표

EmoBrain은 fMRI에서 34차원 감정 프로파일을 디코딩하는 통합 framework다. 학습 때는 brain, video, caption, question을 모두 활용하는 teacher를 두고, 추론 때는 brain과 question만 쓰는 student가 teacher의 출력을 distillation으로 이어받는다. novelty는 특정 encoder가 아니라 이 통합 구조 자체, 즉 멀티모달 학습과 brain-only 추론의 비대칭, modality별 역할 분리, 고차원 readout이다.

핵심 목표는 세 가지다. 첫째, brain만으로 34차원 감정의 고차원 구조를 복원한다. 둘째, valence, arousal 저차원이 놓치는 공존 감정(mixed emotion)을 잡는다. 셋째, video와 caption의 맥락이 brain-only 디코딩을 실제로 끌어올리는지를 distillation으로 검증한다.

---

## 2. 범위

### 구현할 것

* 데이터 로딩과 34차원 라벨 정규화 파이프라인
* brain encoder 후보 네 개(E1 simple projection, E2 ridge encoder, E3 BFM frozen, E4 ViT fine-tune)
* modality별, encoder별 전용 projector
* video foundation model 경로(teacher 전용)
* caption과 question의 텍스트 토큰 경로와 prompt 조립
* LLM backbone과 34차원 출력 head
* teacher 학습, student 학습, distillation
* caption dropout 학습 전략
* baseline(LLM 없는 ridge, modality 단독)
* 평가 지표와 진단 ablation
* 실험을 스위치로 조합하는 config 시스템과 로깅, 체크포인트

### 구현하지 않을 것

* 새로운 BFM이나 video model의 사전학습. 기존 체크포인트를 로드해 쓴다.
* CCN 페이퍼의 subspace 분석. 이 레포는 model framework 전용이다.
* 실시간 추론이나 배포용 서빙.

---

## 3. 확정된 사실과 제약 (DECIDED)

* 학습 데이터는 Horikawa 2020이다. 5명 피험자, 약 2,180에서 2,196개 Cowen 계열 정서 영상(데이터 버전에 따라 클립 수 확인), 각 영상에 34차원 감정 점수(1점에서 9점 원점수).
* cross-subject 확인용 test는 MindCaptioning(Horikawa, Science Advances 2025)이다. 6명 피험자, 약 2,108개 영상, 중립 caption, 문헌 기준 2,036 train과 72 test 분할. 우리는 이 데이터의 영상이 Cowen 계열과 겹치는 부분에 34차원 라벨을 매핑해 external test로 쓴다.
* 이 test는 cross-subject 일반화 확인이다. 영상이 겹치므로 cross-stimulus가 아니다. 평가 리포트에 이 구분을 반드시 출력한다.
* 출력은 34차원 감정 값이다. 34개는 서로 배타적이지 않다(공존 가능). 따라서 34개에 softmax를 적용하지 않는다. 감정별 독립 회귀로 다룬다.
* 라벨은 감정별 z-score로 정규화한다. 통계는 train split에서만 구하고 val과 test에 그대로 적용한다.
* 모델 내부는 z-score 공간에서 동작한다. 사용자 표시용 0에서 1 값은 별도 reporting 변환으로 만든다.
* encoder 후보는 네 개이며 모두 같은 자리(fMRI에서 projector 거쳐 LLM token)의 후보다.
* projector는 modality별이고 encoder별이다. 하나의 공용 projector가 아니다.
* caption과 question은 텍스트라 projector 없이 tokenizer만 거친다. brain과 video는 벡터라 projector를 거친다.
* prompt는 Caption field와 Question field로 나뉜다. caption을 question에 녹이지 않는다(ablation 가능하도록).
* teacher는 brain, video, caption, question을 받는다. student는 brain과 question만 받는다.
* distillation 기본은 offline이다. teacher를 먼저 수렴시켜 얼리고, student를 hard loss와 distillation loss로 학습한다.
* LLM 없는 순수 ridge는 encoder 후보가 아니라 바깥 baseline이다. 성능표에만 등장하고 framework 그래프에는 없다.

---

## 4. 열린 결정 (OPEN, config로 노출)

* LLM backbone. Qwen-VL 계열(예: Qwen3-VL)을 teacher와 student가 공유하는 방향이나 미확정. config의 llm.backbone으로 교체 가능하게.
* BFM 선택. SwiFT, Brain-JEPA, NeuroSTORM 중 E3 대표. config의 encoder.pretrained_ckpt로.
* distillation target. teacher의 34차원 출력(soft label)만 맞출지, hidden state까지 맞출지. 기본 soft label. config의 loss.distill.target으로.
* projector token 수 N_b, N_v. 고차원 보존과 직결되는 병목. sweep 대상. config의 projector.n_tokens로.
* projector 종류. MLP 기본, Q-Former 옵션. config의 projector.type으로.
* teacher의 LLM을 full로 학습할지 LoRA로 할지. 기본 LoRA. config의 llm.teacher.mode로.
* distillation loss 종류. MSE 기본, KL 대안. config의 loss.distill.type으로.
* structure loss 사용 여부. 기본 off. config의 loss.structure.enabled로.

---

## 5. 데이터 명세

### 5-1. 입력과 라벨

* fMRI 입력: 영상 단위 반응. 각 (subject, clip) 쌍에 대해 하나의 fMRI 표현. encoder 종류에 따라 형식이 다르므로(아래 6절), 원 데이터는 encoder 이전의 표준 형태로 보관하고 encoder 어댑터에서 변환한다.
* 라벨: 각 clip에 34차원 벡터. 원점수 1에서 9. shape (C,) with C=34.
* caption: 각 clip에 중립 caption 문자열(teacher 전용). MindCaptioning 소스에서 매핑.
* question: 고정 지시문 문자열(아래 8-3).

### 5-2. 정규화 (DECIDED)

1. train split의 각 감정 열에서 평균 mu[c]와 표준편차 std[c]를 구한다. shape (C,).
2. 모든 split의 라벨을 z = (raw - mu) / std로 변환한다.
3. mu, std를 파일로 저장한다.
4. reporting 시 raw = z * std + mu로 되돌리고, 표시용 0에서 1은 별도 min-max나 clip 규칙으로 만든다(표시 전용, 학습에 미사용).

CAUTION: test 자체 통계로 정규화하면 정보 누출이다. 반드시 train 통계만 쓴다.

### 5-3. 분할

* Horikawa: train, val을 clip 기준으로 나눈다. 재현을 위해 seed 고정.
* 옵션: cross-stimulus 평가를 위해 Horikawa 내부에 held-out stimuli split도 지원한다(config의 data.holdout_stimuli).
* MindCaptioning: external test. 학습에 절대 사용하지 않는다.

### 5-4. MindCaptioning 라벨 매핑 (DECIDED)

1. MindCaptioning clip과 Cowen 계열 clip의 대응표를 만든다.
2. 겹치는 clip에만 Cowen 규준 34차원 점수를 붙인다.
3. 겹치지 않는 clip은 test에서 제외하고, 제외 수와 최종 test clip 수를 로그로 남긴다.
4. test 라벨도 train 통계로 z-score 정규화한다.

Acceptance: 정규화 후 train 라벨의 감정별 평균이 0, 표준편차가 1에 근접. MindCaptioning test clip에 34차원 라벨이 결측 없이 매핑됨.

---

## 6. 아키텍처 명세

### 6-1. 전체 데이터 흐름

Teacher (학습 전용):
```
fMRI  -> brain encoder(E) -> brain projector(E)   -> N_b brain tokens
video -> video FM          -> video projector      -> N_v video tokens
caption(text) --------------> LLM tokenizer         -> caption text tokens
question(text) -------------> LLM tokenizer         -> question text tokens
[all tokens in one sequence] -> LLM -> output head -> 34-dim (z-space)
```

Student (학습 + 추론):
```
fMRI  -> brain encoder(E) -> brain projector(E) -> N_b brain tokens
question(text) -----------> LLM tokenizer         -> question text tokens
[brain + question tokens] -> LLM(frozen) + LoRA -> output head -> 34-dim (z-space)
```

### 6-2. Brain encoder slot (E1 to E4)

공통 계약: 입력은 fMRI 표현, 출력은 (B, T_e, D_enc) 형태의 embedding. frozen 여부는 config 플래그.

* E1 simple projection (DECIDED: no pretrain, control). fMRI feature를 작은 MLP로 D_enc에 사상. 사전학습 없음. 항상 학습됨.
* E2 ridge encoder (DECIDED: LLM 경유). ridge로 얻은 표현을 embedding으로 본다. 이 표현을 projector로 올린다. 주의: 이는 8절의 LLM 없는 ridge baseline과 다르다. 이름을 ridge_encoder로 명확히.
* E3 BFM frozen (DECIDED default frozen). SwiFT 또는 Brain-JEPA 체크포인트를 로드해 embedding 추출. 기본 frozen. config로 fine-tune 전환 가능.
* E4 ViT fine-tune (DECIDED default finetune). Qwen vision encoder를 로드하고 fMRI를 이미지 유사 입력으로 넣는다. 기본은 LoRA 또는 부분 fine-tune. full fine-tune은 소량 데이터에서 무너지므로 기본값 아님.

frozen과 fine-tune은 어떤 encoder에도 적용 가능한 독립 축이다. config의 encoder.frozen과 encoder.lora로 제어. CAUTION: E4 full fine-tune은 overfit 위험. 기본 LoRA.

Acceptance: 각 encoder가 동일한 fMRI 배치를 받아 (B, T_e, D_enc)를 반환. frozen 플래그가 실제로 backward를 차단하는지 grad 확인.

### 6-3. Projector (DECIDED: per-modality, per-encoder)

계약: 입력 (B, T_e, D_enc), 출력 (B, N, D_llm). N은 config의 projector.n_tokens.

* MLP 방식(기본): D_enc를 D_llm으로 사상하고 토큰 수를 N으로 맞춘다(pooling 또는 learned query).
* Q-Former 방식(옵션): N개의 learned query로 cross-attention 요약.
* brain projector와 video projector는 별개 파라미터. 또한 각 encoder마다 자기 projector 인스턴스를 가진다.

CAUTION: N이 너무 작으면 34차원 감정 구조가 압축 병목에서 손실된다. N을 sweep 대상으로 둔다.

Acceptance: projector 출력의 마지막 차원이 D_llm과 일치. brain과 video의 projector가 파라미터를 공유하지 않음을 확인.

### 6-4. Video 경로 (teacher 전용)

* video foundation model은 V-JEPA2 기본, CLIP과 VideoMAE 옵션. config의 video.model.
* 임베딩은 마지막 hidden state를 사용한다(고차 layer). V-JEPA2의 경우 예시 차원 1408. CAUTION: 초기 layer를 쓰지 마라. 감정 관련 시각 정보는 고차 layer에 있다(우리 CCN 결과 근거).
* video projector로 N_v tokens 생성.

### 6-5. 텍스트 경로와 prompt 조립 (DECIDED)

* caption과 question은 LLM tokenizer만 거친다. projector 없음.
* prompt는 Caption field와 Question field로 구성. 8-3의 템플릿을 사용.
* 최종 시퀀스는 벡터 token(brain, video)과 텍스트 token(caption, question)을 한 줄로 결합. 벡터 token은 placeholder 위치에 삽입한다. tokenizer는 텍스트 전체를 한 번 처리한다(두 번 태우지 않는다).
* teacher 시퀀스 순서 기본값: video tokens, Caption field, brain tokens, Question field. student 시퀀스: brain tokens, Question field. 순서는 config로 조정 가능.

CAUTION: caption을 question 안에 문자열로 합치지 마라. 별도 field로 두어야 ablation이 가능하다.

### 6-6. LLM backbone과 출력 head

* backbone은 config의 llm.backbone. teacher와 student가 공유(기본).
* teacher LLM은 기본 LoRA 학습(OPEN, full 가능). student LLM은 frozen에 LoRA 학습(DECIDED).
* 출력 head는 LLM의 마지막 표현에서 34차원 실수를 내는 선형 head. z-space 출력이므로 activation 없음(sigmoid 없음). CAUTION: 34차원에 softmax 금지.

Acceptance: teacher와 student가 같은 backbone 인스턴스 규약을 따르되 student는 LLM 파라미터가 frozen이고 LoRA만 학습됨.

---

## 7. Baseline 명세

### 7-1. B1 ridge (LLM 없음, DECIDED)

* fMRI 입력에서 34차원 z-score 라벨로 바로 가는 감정별 ridge 회귀.
* 정규화, split, 평가 지표를 본 실험과 동일하게.
* 예전 VA binary 0.72가 아니라 34차원에서 새로 측정.

### 7-2. B2 modality 단독 (DECIDED)

* brain 단독, video 단독, (옵션 caption 단독)으로 각각 34차원 예측.
* VA binary의 video 지배가 34차원에서도 성립하는지 확인.

Acceptance: B1과 B2가 본 실험과 같은 지표로 리포트됨. B1(LLM 없음)과 E2 ridge encoder(LLM 경유)의 결과가 라벨상 구분됨.

---

## 8. 학습 명세

### 8-1. Loss (DECIDED)

기호: y_true는 34차원 z-score 라벨, y_stu와 y_tea는 student와 teacher의 34차원 출력. 모두 shape (B, C).

* supervised(hard) loss: 감정별 제곱오차의 합 또는 평균. L_sup = mean_c (y_pred[:,c] - y_true[:,c])^2. Huber 대안 가능(config). CAUTION: 감정 간 softmax 금지.
* 옵션 per-emotion weight: 분산이 작거나 드문 감정을 덜 눌리게 가중(config의 loss.per_emotion_weight). scale 불변 상관 기반 항도 옵션.
* distillation loss(student): 기본은 teacher 출력에 대한 감정별 MSE. L_dist = mean_c (y_stu[:,c] - y_tea[:,c])^2. 근거: distillation에서 값(logit) 매칭이 성능과 양의 상관을 보이며 MSE가 KL보다 나은 경우가 보고됨. 대안: 낮은 온도의 감정별 KL(라벨 잡음에 강함). KL은 합이 1인 분포용이므로 감정별 이진 형태로 reshaping 필요. config의 loss.distill.type.
* 옵션 structure loss: 배치 내 예측 34x34 상관 행렬과 라벨 상관 행렬의 유사도 항. 기본 off.
* 총 student loss: L = lambda_hard * L_sup + lambda_dist * L_dist (+ lambda_struct * L_struct). lambda는 config.

### 8-2. 절차 (DECIDED)

1. teacher를 34차원 라벨에 hard loss로 수렴시킨다. 수렴 후 얼려 저장.
2. student를 hard loss와 distillation loss로 학습한다.
3. distillation ablation을 위해 teacher 없는 student(hard only)도 학습 지원.
4. caption dropout: teacher 또는 student가 caption을 받는 경우, 학습 시 Bernoulli(p_drop)로 caption field를 제거한다. 이는 추론의 caption 부재 형태를 미리 겪게 하고 caption 의존을 끊는다. p_drop은 config.

CAUTION: student 추론 형태는 brain과 question만이다. student의 최종 평가는 반드시 이 형태로 한다.

### 8-3. Prompt 템플릿 (DECIDED)

Question field 고정 지시문(영상별 불변):
```
Question 1: You are an affective neuroscientist. You are analyzing a subject's
fMRI response evoked while watching a video. Analyze the response and identify
which emotions it reflects.
Question 2: Based on the above, give a score from 0 to 1 for each of the 34
emotion categories (admiration, adoration, ... , sympathy, triumph).
```

Caption field(teacher 전용, 영상별 가변):
```
Caption: <neutral scene description mapped from MindCaptioning>
```

주의: Question은 고정 상수라 그 자체로 학습 shortcut이 되지 않는다. 가변이며 정답과 상관 높은 것은 caption이므로, shortcut 방지 대상은 caption이다.

### 8-4. 하이퍼파라미터 (기본값, OPEN)

* optimizer AdamW, lr 기본 1e-4(LLM LoRA는 별도 lr 가능), weight decay 0.01.
* batch size는 자원에 맞춰. gradient accumulation 지원.
* epoch은 early stopping으로. val 프로파일 상관 기준.
* projector.n_tokens 기본 후보 {8, 16, 32}로 sweep.
* caption dropout p_drop 기본 0.5, sweep {0.0, 0.3, 0.5, 0.7}.
* lambda_hard 1.0, lambda_dist 기본 1.0 sweep, lambda_struct 0.0.
* distillation temperature(KL 사용 시) 기본 작은 값.
* seed 고정, 결정론적 설정.

---

## 9. 평가 명세 (DECIDED)

### 9-1. 헤드라인 지표

* per-clip profile correlation: 각 clip에서 예측 34차원 벡터와 정답 34차원 벡터의 상관(Pearson과 Spearman 둘 다). clip 평균으로 집계. 이것이 헤드라인.

### 9-2. 보조 지표

* per-emotion correlation: 각 감정에서 clip을 가로지른 예측과 정답의 상관. 드문 감정 부분집합 별도 리포트.
* mean R2, mean squared error(z-space).

### 9-3. 구조 지표

* RSA: 예측 프로파일들의 34x34 상관 행렬과 정답 상관 행렬의 상삼각 유사도.
* dimension-compression curve: readout을 k차원으로 줄이며 프로파일 재현이 어디서 포화 또는 붕괴하는지. k를 1부터 34까지.

### 9-4. cross-subject 평가

* Horikawa로 학습한 student를 MindCaptioning test에 적용. 프로파일과 구조 지표 측정.
* 리포트에 cross-subject이며 cross-stimulus가 아님을 명시 출력.
* 옵션: held-out stimuli 결과를 함께 출력.

### 9-5. 진단 ablation

* shortcut 점검: student에 brain만 줬을 때와 caption을 함께 줬을 때 성능 비교. brain 제거 시 성능이 안 떨어지면 shortcut 의존 경고 출력.
* teacher modality ablation: teacher에서 caption 또는 video 제거 시 성능 변화. brain 제거 시 크게 안 떨어지면 teacher가 brain 무시 경고.

### 9-6. mixed emotion 분석

* 두 감정이 동시에 높은 clip을 선별해, 1차원 valence 예측과 34차원 예측이 공존을 어떻게 다루는지 사례 비교.

Acceptance: 모든 지표 함수가 Phase 0 단계에서 고정되어 실험 간 동일하게 적용됨.

---

## 10. Config 스키마

YAML 예시. 실제 키 이름은 이 구조를 따른다.
```yaml
run:
  name: e3_frozen_student_distill
  seed: 42
  output_dir: runs/${run.name}

data:
  train_dataset: horikawa2020
  test_dataset: mindcaptioning
  fmri_root: /path/to/fmri
  label_root: /path/to/labels
  caption_root: /path/to/captions
  holdout_stimuli: false
  norm_stats_path: artifacts/label_norm_stats.pt   # mu, std (C,)

encoder:
  type: e3_bfm            # e1_proj | e2_ridge | e3_bfm | e4_vit
  pretrained_ckpt: /path/to/bfm.ckpt   # e3, e4
  frozen: true            # OPEN axis
  lora:
    enabled: false
    r: 8
    alpha: 16

projector:
  type: mlp               # mlp | qformer
  n_tokens: 16            # OPEN, sweep
  hidden_dim: 1024

video:                    # teacher only
  model: vjepa2           # vjepa2 | clip | videomae
  layer: last_hidden
  projector:
    type: mlp
    n_tokens: 16

text:
  tokenizer: ${llm.backbone}
  use_caption_field: true     # teacher true, student false at inference
  caption_dropout_p: 0.5      # OPEN, sweep

llm:
  backbone: qwen-vl           # OPEN
  teacher:
    mode: lora                # lora | full  (OPEN)
  student:
    frozen: true
    lora:
      enabled: true
      r: 16
      alpha: 32
  output_head_dim: 34

loss:
  hard:
    type: mse               # mse | huber
    per_emotion_weight: none
  distill:
    enabled: true
    type: mse               # mse | kl   (OPEN)
    target: soft_label      # soft_label | hidden_state (OPEN)
    temperature: 1.0
  structure:
    enabled: false
  lambda_hard: 1.0
  lambda_dist: 1.0
  lambda_struct: 0.0

train:
  optimizer: adamw
  lr: 1.0e-4
  weight_decay: 0.01
  batch_size: 16
  grad_accum: 1
  max_epochs: 100
  early_stop_metric: val_profile_corr
  early_stop_patience: 10

eval:
  metrics: [profile_corr, per_emotion_corr, rsa, dim_compression, cross_subject]
  report_cross_stimulus_caveat: true
```

---

## 11. 레포 구조 (제안)

```
emobrain/
  configs/                 # yaml 실험 설정
  data/
    datasets.py            # Horikawa, MindCaptioning 로더
    labels.py              # 34차원 로드, z-score, mu/std 저장
    caption_map.py         # MindCaptioning caption 및 라벨 매핑
    fmri_adapter.py        # encoder별 입력 형식 변환
  models/
    encoders/
      e1_projection.py
      e2_ridge_encoder.py
      e3_bfm.py            # SwiFT/Brain-JEPA 로드
      e4_vit.py           # Qwen vision encoder + lora
    projector.py           # mlp, qformer (per-modality/per-encoder)
    video_encoder.py       # vjepa2/clip/videomae
    prompt.py              # caption/question field, 시퀀스 조립
    llm_backbone.py        # backbone 로드, lora, 34-dim head
    teacher.py             # 네 입력 결합
    student.py             # brain+question, distillation 연결
  losses/
    supervised.py          # per-emotion mse/huber, weight
    distillation.py        # per-emotion mse, kl(reshaped)
    structure.py           # 34x34 corr matching
  train/
    train_teacher.py
    train_student.py
    train_baseline_ridge.py
    train_modality_solo.py
  eval/
    metrics.py             # profile_corr, per_emotion, rsa, dim_compression
    cross_subject.py
    ablation.py            # shortcut, teacher modality
    mixed_emotion.py
  utils/
    seed.py, logging.py, checkpoint.py, shapes.py
  scripts/
    run_experiment.py      # config 받아 파이프라인 실행
```

---

## 12. 빌드 순서 (에이전트용)

1. data 모듈. datasets, labels(z-score와 mu/std 저장), caption_map, fmri_adapter. 여기서 정보 누출 방지 로직 확립.
2. losses와 eval/metrics. 이후 모든 실험이 공유하므로 먼저 고정.
3. baseline. train_baseline_ridge, train_modality_solo. 기준선 확보.
4. models. encoders 넷, projector, prompt, llm_backbone, 34-dim head.
5. train_student(teacher 없이 hard only). encoder 후보 단독 성능표.
6. video_encoder와 teacher. train_teacher.
7. distillation. student가 teacher를 잇도록. caption dropout.
8. eval 확장. cross_subject, ablation, mixed_emotion, dim_compression.

각 단계 끝에 해당 모듈의 Acceptance를 통과시킨다.

---

## 13. 실험 매트릭스 (산출 목표)

* B1 ridge(LLM 없음), B2 modality 단독(brain, video, caption).
* E1 to E4 각각 brain-only student(distillation 없음). frozen과 fine-tune 축 포함.
* teacher(네 입력) 학습과 modality ablation.
* E1 to E4 각각 student + distillation. distillation 유무 비교.
* caption dropout p_drop sweep, projector n_tokens sweep, lambda_dist sweep.
* cross-subject: 각 주요 모델을 MindCaptioning test에 적용.

각 run은 config 하나로 재현 가능해야 한다.

---

## 14. 전역 CAUTION 요약

* 34차원에 softmax를 쓰지 마라. 감정 공존이 사라진다.
* test나 val 통계로 정규화하지 마라. train 통계만.
* 텍스트(caption, question)에 projector를 붙이지 마라. tokenizer만.
* video는 고차 layer를 써라. 초기 layer 금지.
* caption을 question에 문자열로 합치지 마라. 별도 field.
* frozen과 fine-tune은 encoder 종류와 무관한 독립 축이다. config로.
* E4 full fine-tune 기본값 금지. 소량 데이터에서 overfit. LoRA 또는 부분.
* student 최종 평가는 brain과 question만인 추론 형태로.
* cross-subject 결과를 cross-stimulus로 서술하지 마라.
* E2 ridge encoder(LLM 경유)와 B1 ridge(LLM 없음)를 혼동하지 마라.

---

## 15. 관련 연구 (구현 시 참고, 차별화용)

* privileged knowledge distillation과 learning using privileged information. 멀티모달 teacher에서 축소 modality student로 지식을 옮기는 계보. 우리 teacher-student 비대칭의 이론적 배경.
* knowledge distillation의 MSE 대 KL. 값(logit) 매칭이 성능과 양의 상관을 보이며 MSE가 KL보다 나은 경우가 보고됨. KL은 라벨 잡음에 강함. distillation loss 기본값 근거.
* EmoBrain 인접 연구인 EmoMind은 fMRI에서 정서적 caption을 생성한다. 우리는 텍스트 생성이 아니라 34차원 프로파일을 brain-only로 distillation한다는 점에서 다르다.
* 데이터와 모델 근거: Horikawa 2020(정서 영상 fMRI와 34차원 규준), Cowen과 Keltner 2017(34개 감정 카테고리), MindCaptioning(Horikawa, Science Advances 2025), V-JEPA2(Assran 등 2025), Brain-JEPA(Dong 등 2024), SwiFT.

---

## 부록 A. 34개 감정 카테고리 (고정 순서)

admiration, adoration, aesthetic appreciation, amusement, anger, anxiety, awe, awkwardness, boredom, calmness, confusion, contempt, craving, disappointment, disgust, empathic pain, entrancement, envy, excitement, fear, guilt, horror, interest, joy, nostalgia, pride, relief, romance, sadness, satisfaction, sexual desire, surprise, sympathy, triumph.

이 34개가 출력 벡터의 인덱스 순서다. 라벨, 예측, 정규화 통계가 모두 이 순서를 따르도록 강제하라. 흔히 인용되는 27개는 신뢰도나 공적재로 제외된 일곱 개(contempt, disappointment, envy, guilt, pride, triumph, sympathy)를 뺀 축소 집합이며, 본 프로젝트는 34개 전체를 사용한다.

## 부록 B. 텐서 shape 계약 요약

* fMRI 입력: encoder별 상이. fmri_adapter가 표준화.
* encoder 출력: (B, T_e, D_enc).
* projector 출력: (B, N, D_llm).
* brain tokens: (B, N_b, D_llm). video tokens: (B, N_v, D_llm).
* 텍스트 tokens: LLM tokenizer 규약.
* LLM 최종 표현에서 head: (B, C) with C=34, z-space.
* 라벨: (B, C). mu, std: (C,).
