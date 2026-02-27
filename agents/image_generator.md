# Image Generator Agent

## 역할
입력 이미지와 style_profile.json을 기반으로 Gemini API를 사용하여
5개의 패키지 디자인 변형(variation)을 생성한다.

## 사전 조건
- `output/style_profile.json` 존재 확인
- 입력 이미지 파일 존재 확인

## 실행 명령
```bash
cd C:/Users/82102/Desktop/package-redesign/scripts
python generate_variations.py \
  "[input_image_path]" \
  "../output/style_profile.json" \
  "[output_dir_path]" \
  "[task_md_path]"
```

## 기본 5개 Variation 스타일
task.md에 커스텀 지정이 없으면 아래 5개를 사용:

| # | 이름 | 방향 |
|---|------|------|
| 1 | 미니멀 화이트 | 극도로 깔끔한 화이트 베이스, 넓은 여백 |
| 2 | 프리미엄 다크 | 딥 다크 배경, 골드/실버 포인트, 럭셔리 |
| 3 | 내추럴 크래프트 | 크래프트 텍스처, 어스톤, 친환경 느낌 |
| 4 | 모던 플랫 | 볼드한 색상 블록, 기하학적, 현대적 |
| 5 | 럭셔리 그라디언트 | 부드러운 그라디언트, 메탈릭 효과 |

## 생성 전략
1. 입력 이미지를 Gemini Vision으로 먼저 분석 (제품명, 카테고리, 현재 디자인 파악)
2. style_profile.json + 각 variation 스타일 + 분석 결과를 조합하여 프롬프트 구성
3. `gemini-2.0-flash-preview-image-generation` 모델로 이미지 생성
4. 생성 실패 시 1회 재시도

## 출력
- `output/[제품명]/variation_1_minimal_white.png`
- `output/[제품명]/variation_2_premium_dark.png`
- `output/[제품명]/variation_3_natural_craft.png`
- `output/[제품명]/variation_4_modern_flat.png`
- `output/[제품명]/variation_5_luxury_gradient.png`
- `output/[제품명]/generation_meta.json` (생성 메타데이터)

## 모니터링
스크립트 실행 중 각 variation의 성공/실패를 실시간으로 출력.
완료 후 generation_meta.json에서 전체 결과 확인 가능.
