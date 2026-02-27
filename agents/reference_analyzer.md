# Reference Analyzer Agent

## 역할
references/before/ 와 references/after/ 의 이미지 쌍을 분석하여
공통 스타일 변환 패턴을 추출하고 style_profile.json을 생성한다.

## 실행 조건
- `output/style_profile.json`이 없을 때만 실행
- 레퍼런스 이미지가 추가/교체된 경우 강제 재실행

## 실행 명령
```bash
cd C:/Users/82102/Desktop/package-redesign/scripts
python analyze_references.py ../references ../output/style_profile.json
```

## 이미지 매칭 규칙
- `references/before/item1.png` ↔ `references/after/item1.png`
- 파일명이 같은 것끼리 쌍으로 처리
- 한쪽만 있는 파일은 무시

## 출력 형식 (style_profile.json)
```json
{
  "common_color_palette": ["색상 목록"],
  "typography_style": "타이포그래피 설명",
  "layout_principles": ["레이아웃 원칙들"],
  "design_philosophy": "전반적인 디자인 철학",
  "premium_direction": "프리미엄화 방향성",
  "transformation_rules": ["변환 규칙들"],
  "style_keywords": ["키워드들 (영문 포함)"],
  "individual_analyses": [
    {
      "pair": "item1",
      "analysis": { ... }
    }
  ]
}
```

## 성공 기준
- style_profile.json 파일 생성 완료
- 최소 1개 이상의 레퍼런스 쌍 분석 성공
