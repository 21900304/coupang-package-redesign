# 패키지 리디자인 AI Agent 시스템

## 시스템 개요
쿠팡 판매 제품의 패키지 디자인을 Google Gemini API로 자동 리디자인하는 시스템.
before/after 레퍼런스 7쌍을 학습하여 신제품에 5개의 리디자인 변형을 생성한다.

## 디렉토리 구조
```
package-redesign/
├── CLAUDE.md                  ← 현재 파일 (전역 지침)
├── agents/                    ← 서브에이전트 역할 정의
│   ├── orchestrator.md
│   ├── reference_analyzer.md
│   ├── image_generator.md
│   └── output_manager.md
├── references/
│   ├── before/                ← 원본 패키지 이미지 (item1.png ~ item7.png)
│   └── after/                 ← 리디자인 완성본 (item1.png ~ item7.png)
├── scripts/
│   ├── utils.py
│   ├── analyze_references.py  ← 레퍼런스 분석 스크립트
│   └── generate_variations.py ← 이미지 생성 스크립트
├── tasks/
│   └── [제품명]/
│       ├── task.md            ← 작업 지시서
│       └── input.png          ← 재디자인할 신제품 이미지
└── output/
    ├── style_profile.json     ← 캐시된 스타일 프로파일 (재사용)
    └── [제품명]/              ← 생성된 variation 이미지들
```

## 필수 환경 변수
- `GEMINI_API_KEY`: Google Gemini API 키
- 확인: `echo $GEMINI_API_KEY`
- 설정: `export GEMINI_API_KEY="your-key-here"` 또는 `.env` 파일 사용

## 실행 트리거
사용자가 아래 형식으로 요청한다:
> "tasks/[제품명]/task.md 읽고 패키지 리디자인 시작해줘"
> 또는 task.md 경로와 함께 작업 지시

---

## 워크플로우 (반드시 이 순서로 실행)

### STEP 1: 환경 확인
```bash
echo $GEMINI_API_KEY
```
- API 키가 없으면 즉시 중단하고 사용자에게 안내
- 필요시: `pip install google-genai pillow` 실행

### STEP 2: task.md 파싱
agents/orchestrator.md 참고하여 task.md를 읽고 파악:
- 제품명 (output 디렉토리명으로 사용)
- input 이미지 경로
- 추가 스타일 요구사항
- 원하는 variation 스타일 (없으면 기본값 5개 사용)

### STEP 3: 레퍼런스 분석 (style_profile.json 생성)
agents/reference_analyzer.md 참고

**output/style_profile.json이 이미 존재하면 사용자에게 재사용 여부 확인**
재사용 시 이 단계 스킵.

```bash
cd C:/Users/82102/Desktop/package-redesign/scripts
python analyze_references.py ../references ../output/style_profile.json
```

### STEP 4: 이미지 변형 생성
agents/image_generator.md 참고

```bash
cd C:/Users/82102/Desktop/package-redesign/scripts
python generate_variations.py \
  "../tasks/[제품명]/input.png" \
  "../output/style_profile.json" \
  "../output/[제품명]" \
  "../tasks/[제품명]/task.md"
```

### STEP 5: 결과 보고
agents/output_manager.md 참고
- 생성된 파일 목록과 각 variation 스타일 설명 출력
- 실패한 항목이 있으면 원인과 재시도 방법 안내

---

## 중요 규칙
- scripts/ 실행은 반드시 `cd scripts` 후 실행 (상대 경로 기준)
- 오류 발생 시 즉시 원인 파악 후 사용자에게 보고, 무한 재시도 금지
- style_profile.json은 레퍼런스가 변경되지 않으면 재사용 권장 (분석 비용 절감)
- variation 생성 실패 시 1회 재시도 후 스킵하고 나머지 계속 진행
