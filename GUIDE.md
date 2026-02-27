# 패키지 리디자인 Agent 사용 가이드

## 목차
1. [시스템 개요](#1-시스템-개요)
2. [최초 설정](#2-최초-설정)
3. [새 제품 리디자인 실행하기](#3-새-제품-리디자인-실행하기)
4. [워크플로우 상세 설명](#4-워크플로우-상세-설명)
5. [task.md 작성 방법](#5-taskmd-작성-방법)
6. [Variation 스타일 커스터마이징](#6-variation-스타일-커스터마이징)
7. [style_profile.json 재사용 전략](#7-style_profilejson-재사용-전략)
8. [결과물 확인](#8-결과물-확인)
9. [자주 발생하는 오류 및 해결법](#9-자주-발생하는-오류-및-해결법)

---

## 1. 시스템 개요

이 시스템은 Claude Code (AI Agent)가 Google Gemini API를 활용하여 쿠팡 판매용 제품의 패키지 디자인을 자동으로 리디자인한다.

### 동작 원리

```
[사용자]  task.md 작성 + input.png 준비
    ↓
[Claude Code]  CLAUDE.md 읽고 워크플로우 자동 실행
    ↓
[Gemini Vision]  references/before + after 7쌍 분석
    ↓
[Gemini Image]  분석 결과 기반으로 5개 variation 생성
    ↓
[결과]  output/[제품명]/ 에 이미지 5개 저장
```

### 사용 모델

| 용도 | 모델 |
|------|------|
| 레퍼런스 분석 (Vision) | `gemini-2.5-flash` |
| 이미지 생성 | `gemini-2.0-flash-exp-image-generation` |

### 디렉토리 구조

```
package-redesign/
├── references/
│   ├── before/     ← 원본 패키지 7개 (변경 X)
│   └── after/      ← 리디자인 완성본 7개 (변경 X)
├── tasks/
│   └── [제품명]/
│       ├── task.md     ← 내가 작성하는 작업 지시서
│       └── input.jpg   ← 리디자인할 제품 이미지
└── output/
    ├── style_profile.json    ← 자동 생성 (재사용 가능)
    └── [제품명]/
        ├── variation_1_minimal_white.png
        ├── variation_2_premium_dark.png
        ├── variation_3_natural_craft.png
        ├── variation_4_modern_flat.png
        ├── variation_5_luxury_gradient.png
        └── generation_meta.json
```

---

## 2. 최초 설정

### 2-1. API 키 설정

프로젝트 루트에 `.env` 파일을 생성하고 Gemini API 키를 입력한다.

```
# C:/Users/82102/Desktop/package-redesign/.env
GEMINI_API_KEY=your-api-key-here
```

> Google AI Studio (https://aistudio.google.com) 에서 무료로 발급 가능.

### 2-2. 의존성 설치

```bash
pip install google-genai pillow
```

### 2-3. 레퍼런스 이미지 확인

`references/before/` 와 `references/after/` 에 동일한 파일명으로 before/after 쌍이 있어야 한다.

```
references/before/item 1.jpg  ←→  references/after/item 1.jpg
references/before/item 2.jpg  ←→  references/after/item 2.jpg
...
```

현재 7쌍이 준비되어 있으며, **레퍼런스가 바뀌지 않는 한 추가 작업 불필요**.

---

## 3. 새 제품 리디자인 실행하기

### Step 1. 제품 디렉토리 생성 및 파일 준비

```
tasks/
└── 내제품이름/
    ├── task.md     ← 아래 양식 참고하여 작성
    └── input.jpg   ← 리디자인할 제품 이미지 (jpg/png 모두 가능)
```

**파일명 규칙:**
- 디렉토리명(`내제품이름`)이 output 폴더명으로 그대로 사용됨
- 공백 없이 영문/한글 가능 (예: `vita_c`, `홍삼정`, `green_tea_powder`)
- 입력 이미지는 `input.jpg` 또는 `input.png` 권장

### Step 2. task.md 작성

```markdown
# 패키지 리디자인 작업 지시서

## 제품 정보
- 제품명: 내제품이름
- 카테고리: 건강식품
- 쿠팡 타겟 고객: 30-50대 건강 관심층
- input 이미지: tasks/내제품이름/input.jpg

## 스타일 방향
- 기존보다 더 프리미엄하고 신뢰감 있는 느낌으로
- 초록색 계열 유지하되 더 세련되게

## 출력 설정
- output 경로: output/내제품이름/
- 개수: 5개
```

> 자세한 작성법은 [5. task.md 작성 방법](#5-taskmd-작성-방법) 참고.

### Step 3. Claude Code에서 실행 명령

Claude Code CLI 또는 채팅창에 아래 형식으로 입력한다:

```
tasks/내제품이름/task.md 읽고 패키지 리디자인 시작해줘
```

Claude가 자동으로:
1. task.md 파싱
2. 레퍼런스 분석 (또는 캐시 재사용)
3. 5개 variation 이미지 생성
4. 결과 보고

까지 전부 처리한다.

### Step 4. 결과 확인

```
output/내제품이름/
├── variation_1_minimal_white.png
├── variation_2_premium_dark.png
├── variation_3_natural_craft.png
├── variation_4_modern_flat.png
└── variation_5_luxury_gradient.png
```

---

## 4. 워크플로우 상세 설명

Claude Code가 실행 명령을 받으면 다음 순서로 자동 처리된다.

### STEP 1: 환경 확인

- `.env` 파일에서 `GEMINI_API_KEY` 로드
- `google-genai`, `pillow` 패키지 설치 여부 확인
- API 키가 없으면 즉시 중단하고 설정 방법 안내

### STEP 2: task.md 파싱

`agents/orchestrator.md` 지침에 따라 task.md에서 아래 정보를 추출:

| 항목 | 필수 여부 | 없을 때 기본값 |
|------|-----------|----------------|
| 제품명 | 필수 | 디렉토리명에서 자동 추출 |
| input 이미지 경로 | 필수 | 없으면 중단 |
| 스타일 방향 메모 | 선택 | 빈 문자열 |
| 커스텀 variation | 선택 | 기본 5개 스타일 |
| output 경로 | 선택 | `output/[제품명]/` |

### STEP 3: 레퍼런스 분석

**`output/style_profile.json`이 이미 있으면 재사용 여부를 물어본다.**
없으면 자동으로 레퍼런스 분석을 실행한다.

```bash
# 내부적으로 실행되는 명령
cd scripts
python analyze_references.py ../references ../output/style_profile.json
```

**분석 과정:**
1. `references/before/` + `references/after/` 에서 7쌍 로드
2. 각 쌍을 Gemini Vision으로 분석 → 색상 변화, 타이포그래피, 레이아웃, 프리미엄 점수 등 추출
3. 7개 분석 결과를 종합 → 공통 스타일 패턴 도출
4. `output/style_profile.json`으로 저장

**소요 시간:** 약 1~2분 (7쌍 × API 호출)

### STEP 4: 이미지 변형 생성

```bash
# 내부적으로 실행되는 명령
cd scripts
python generate_variations.py \
  "tasks/[제품명]/input.jpg" \
  "output/style_profile.json" \
  "output/[제품명]" \
  "tasks/[제품명]/task.md"
```

**생성 과정:**
1. 입력 이미지를 Gemini Vision으로 분석 (제품명, 카테고리, 현재 디자인 파악)
2. `style_profile.json` + variation 스타일 + task.md 메모를 조합하여 프롬프트 구성
3. Gemini 이미지 생성 모델로 각 variation 생성
4. 실패 시 1회 자동 재시도, 재실패 시 해당 variation 스킵 후 계속 진행

**소요 시간:** 약 3~8분 (5개 × 이미지 생성 API 호출)

### STEP 5: 결과 보고

- 생성된 파일 목록과 각 스타일 설명 출력
- 실패한 항목이 있으면 원인 및 재시도 방법 안내
- `generation_meta.json`에 전체 결과 메타데이터 저장

---

## 5. task.md 작성 방법

### 기본 양식

```markdown
# 패키지 리디자인 작업 지시서

## 제품 정보
- 제품명: [디렉토리명과 동일하게]
- 카테고리: [예: 식품, 화장품, 건강식품, 생활용품]
- 쿠팡 타겟 고객: [예: 20-40대 여성, 건강 관심층]
- input 이미지: tasks/[제품명]/input.jpg

## 스타일 방향
- [자유롭게 원하는 스타일 요청]

## 출력 설정
- output 경로: output/[제품명]/
- 개수: 5개
```

### 스타일 방향 작성 예시

**색상 유지 요청:**
```
- 파란색 계열 유지하되 더 고급스럽게
- 브랜드 컬러인 빨간색은 포인트로만 사용
```

**전체 방향 제시:**
```
- 기존보다 훨씬 프리미엄하고 신뢰감 있는 느낌으로
- 한국 소비자가 선호하는 깔끔하고 현대적인 스타일
- 제품명과 효능이 잘 보이는 레이아웃
```

**타겟 이미지 설명:**
```
- 올리브영 매대에 놓여도 어색하지 않을 정도의 디자인
- 백화점 식품관 느낌의 프리미엄 포장
```

### 스타일 방향을 적게 쓸수록 좋은 경우
레퍼런스 스타일을 최대한 따르고 싶을 때는 스타일 방향을 비워두거나 간단하게만 작성해도 된다. 레퍼런스 분석에서 추출된 `style_profile.json`이 자동으로 디자인 방향을 결정한다.

---

## 6. Variation 스타일 커스터마이징

### 기본 5개 스타일 (커스텀 없을 때)

| # | 파일명 | 스타일 방향 |
|---|--------|------------|
| 1 | `variation_1_minimal_white` | 흰 배경, 극도로 깔끔, 넓은 여백, 단색 포인트 |
| 2 | `variation_2_premium_dark` | 딥 다크 배경, 골드/실버 포인트, 럭셔리 |
| 3 | `variation_3_natural_craft` | 크래프트 텍스처, 어스톤, 친환경·자연 느낌 |
| 4 | `variation_4_modern_flat` | 볼드한 단색 블록, 기하학적, 그라디언트 없음 |
| 5 | `variation_5_luxury_gradient` | 부드러운 그라디언트, 메탈릭 효과, 고급스러움 |

### 커스텀 스타일 지정 방법

task.md에 `## Variation 커스텀` 섹션을 추가하면 기본 5개 대신 사용된다.

```markdown
## Variation 커스텀
1. 한방 전통 스타일 - 한지 느낌 배경, 전통 문양, 붓글씨 느낌 폰트
2. K-뷰티 트렌드 - 파스텔 핑크, 미니멀, 인스타그래머블
3. 스포츠/액티브 - 네온 컬러, 역동적인 레이아웃, 에너지 넘치는 느낌
4. 오가닉 프리미엄 - 딥그린 + 골드, 식물성 원료 강조, 유럽풍
5. 레트로 빈티지 - 복고풍 색상, 클래식 폰트, 빈티지 일러스트
```

---

## 7. style_profile.json 재사용 전략

레퍼런스 분석은 API 호출 비용과 시간이 소요된다. 아래 기준으로 재사용 여부를 결정한다.

### 재사용 (분석 스킵) 해도 되는 경우

- **같은 날 여러 제품을 연속으로 처리할 때** → 무조건 재사용
- 레퍼런스 이미지를 변경하지 않았을 때
- 스타일 방향을 크게 바꿀 계획이 없을 때

### 재생성해야 하는 경우

- `references/before/` 또는 `references/after/` 이미지를 추가/교체/삭제했을 때
- 레퍼런스 기반 스타일이 원하는 방향과 맞지 않을 때
- `style_profile.json`이 오래되어 최신 레퍼런스를 반영하지 않을 때

### 재생성 방법

Claude Code에 직접 지시:
```
style_profile.json 무시하고 레퍼런스 새로 분석해줘
```

또는 파일을 직접 삭제한 뒤 실행하면 자동으로 재생성된다:
```bash
del output\style_profile.json
```

---

## 8. 결과물 확인

### 생성 파일 구조

```
output/내제품이름/
├── variation_1_minimal_white.png     ← 미니멀 화이트
├── variation_2_premium_dark.png      ← 프리미엄 다크
├── variation_3_natural_craft.png     ← 내추럴 크래프트
├── variation_4_modern_flat.png       ← 모던 플랫
├── variation_5_luxury_gradient.png   ← 럭셔리 그라디언트
└── generation_meta.json              ← 생성 메타데이터
```

### generation_meta.json 구조

```json
{
  "input_image": "tasks/내제품이름/input.jpg",
  "product_analysis": "Gemini가 분석한 제품 설명",
  "style_profile_used": "output/style_profile.json",
  "task_md": "tasks/내제품이름/task.md",
  "variations": [
    {
      "variation_id": 1,
      "style_label": "미니멀 화이트",
      "status": "success",
      "path": "output/내제품이름/variation_1_minimal_white.png",
      "attempts": 1
    }
  ]
}
```

### 결과 활용 팁

- 5개 중 마음에 드는 스타일을 선택하여 디자이너에게 레퍼런스로 전달
- 특정 variation을 기반으로 추가 수정을 요청하려면 해당 이미지를 새 input으로 사용 가능
- 같은 task.md로 재실행하면 다른 variation이 생성됨 (AI 생성 특성상 매번 다름)

---

## 9. 자주 발생하는 오류 및 해결법

### API 키 오류

```
[ERROR] GEMINI_API_KEY가 설정되지 않았습니다.
```

**해결:** 프로젝트 루트에 `.env` 파일 생성 후 키 입력
```
GEMINI_API_KEY=AIza...
```

---

### 모델 미사용 오류

```
404 NOT_FOUND. This model is no longer available to new users.
```

**해결:** `scripts/` 내 모델명 확인. 현재 사용 중인 모델:
- 분석: `gemini-2.5-flash`
- 생성: `gemini-2.0-flash-exp-image-generation`

---

### 레퍼런스 쌍 매칭 실패

```
[WARN] item 3.jpg에 대응하는 after 이미지 없음, 스킵
```

**해결:** `references/before/`와 `references/after/`의 파일명이 정확히 일치해야 한다.

---

### 이미지 생성 후 이미지가 없음 (텍스트만 반환)

```
[WARN] 이미지 미반환 (attempt 1/2), 재시도...
```

스크립트가 자동으로 1회 재시도한다. 재시도 후에도 실패하면 해당 variation을 스킵하고 다음으로 진행한다. 완료 후 실패한 variation만 개별 재실행하려면 Claude에게 요청:

```
variation_2만 다시 생성해줘
```

---

### Windows 인코딩 오류

```
UnicodeEncodeError: 'cp949' codec can't encode character
```

**해결:** 이미 수정 완료. 이모지 대신 `[OK]`/`[FAIL]` 텍스트 사용.

---

### 실행 경로 오류

```
FileNotFoundError: ../references/before
```

**해결:** 반드시 `scripts/` 디렉토리 안에서 실행해야 한다. Claude가 자동으로 처리하지만, 수동으로 실행할 때는:
```bash
cd C:/Users/82102/Desktop/package-redesign/scripts
python analyze_references.py ...
```

---

## 빠른 참조

### 새 제품 실행 체크리스트

```
[ ] tasks/[제품명]/ 디렉토리 생성
[ ] input.jpg 또는 input.png 추가
[ ] task.md 작성 (제품명, 카테고리, 스타일 방향)
[ ] Claude Code에 명령: "tasks/[제품명]/task.md 읽고 패키지 리디자인 시작해줘"
[ ] output/[제품명]/ 에서 결과 확인
```

### 수동 실행 명령 (Claude 없이 직접)

```bash
# 레퍼런스 분석
cd C:/Users/82102/Desktop/package-redesign/scripts
python analyze_references.py ../references ../output/style_profile.json

# 이미지 생성
python generate_variations.py \
  "../tasks/[제품명]/input.jpg" \
  "../output/style_profile.json" \
  "../output/[제품명]" \
  "../tasks/[제품명]/task.md"
```
