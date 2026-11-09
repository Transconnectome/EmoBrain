# GED (Huang 외, 2022, MICCAI) 공식 코드 일부

- 출처: https://github.com/zhongyu1998/GED, commit 3ea8492f0d007cd2776777f0dd2bd1ad54f8d3eb (2022-07-25), MIT 라이선스(LICENSE)
- 가져온 것: models/graphcnn.py, models/mlp.py(바꾸지 않음)
- graphcnn.py에서 바꾼 것: mlp를 가져오는 경로, `torch.sparse.FloatTensor`를 `torch.sparse_coo_tensor`로(지금 PyTorch에 없음). 계산은 같다.
- 자료 준비(영역 칸 평균, 정서-영역 그래프)와 학습 절차는 `src/s5_ged.py`가 원 코드(utils.py, main.py)를 따라 짰다. 원 코드에서 바꾼 점은 그 파일 머리말과 01 O27에 있다.
