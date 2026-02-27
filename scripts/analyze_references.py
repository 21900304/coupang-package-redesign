#!/usr/bin/env python3
"""
references/before + after 이미지 쌍을 Gemini Vision으로 분석하여
공통 스타일 변환 패턴을 추출하고 style_profile.json을 생성한다.

사용법:
  python analyze_references.py [references_dir] [output_json_path]
  python analyze_references.py ../references ../output/style_profile.json
"""

import sys
import json
from pathlib import Path
from google.genai import types
from utils import get_client, load_image_as_part, get_reference_pairs, parse_json_response, save_json


ANALYZE_PAIR_PROMPT = """
아래는 패키지 디자인 리디자인의 before/after 예시입니다.
첫 번째 이미지(Before)와 두 번째 이미지(After)를 비교하여 디자인 변화를 분석해주세요.

아래 JSON 형식으로만 응답하세요 (설명 텍스트 없이 JSON만):
{
  "color_changes": "색상 변화 설명 (구체적으로)",
  "typography": "텍스트/폰트 스타일 변화",
  "layout": "레이아웃 구조 변화",
  "visual_style": "전반적인 시각적 스타일 변화",
  "material_texture": "재질감/텍스처 변화",
  "premium_score_before": 3,
  "premium_score_after": 8,
  "key_improvements": ["주요 개선점 1", "주요 개선점 2", "주요 개선점 3"]
}
"""

EXTRACT_COMMON_STYLE_PROMPT_TEMPLATE = """
아래는 {count}개의 패키지 리디자인 분석 결과입니다:

{analyses_json}

이 분석들을 종합하여 공통적인 스타일 변환 패턴을 추출해주세요.
아래 JSON 형식으로만 응답하세요 (설명 텍스트 없이 JSON만):
{{
  "common_color_palette": ["공통적으로 사용된 색상들"],
  "typography_style": "공통 타이포그래피/폰트 스타일",
  "layout_principles": ["공통 레이아웃 원칙 1", "원칙 2", "원칙 3"],
  "design_philosophy": "전반적인 디자인 철학 한 문장 요약",
  "premium_direction": "프리미엄화 방향성 설명",
  "transformation_rules": [
    "변환 규칙 1 (예: 복잡한 배경 → 단색/그라디언트 배경)",
    "변환 규칙 2",
    "변환 규칙 3"
  ],
  "style_keywords": ["keyword1", "keyword2", "modern", "premium", "clean"]
}}
"""


def analyze_pair(client, pair: dict) -> dict | None:
    """단일 before/after 쌍 분석"""
    try:
        before_part = load_image_as_part(pair["before"])
        after_part = load_image_as_part(pair["after"])

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_text(text="Before 이미지:"),
                before_part,
                types.Part.from_text(text="After 이미지:"),
                after_part,
                types.Part.from_text(text=ANALYZE_PAIR_PROMPT),
            ],
        )
        return parse_json_response(response.text)

    except Exception as e:
        print(f"    [FAIL] 분석 실패: {e}")
        return None


def extract_common_style(client, analyses: list[dict]) -> dict:
    """개별 분석 결과들에서 공통 스타일 패턴 추출"""
    analyses_json = json.dumps(
        [a for a in analyses if a["analysis"] is not None],
        ensure_ascii=False,
        indent=2,
    )
    prompt = EXTRACT_COMMON_STYLE_PROMPT_TEMPLATE.format(
        count=len(analyses),
        analyses_json=analyses_json,
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[types.Part.from_text(text=prompt)],
    )
    return parse_json_response(response.text)


def main(references_dir: str, output_path: str):
    print("\n=== Reference Analyzer 시작 ===\n")

    client = get_client()

    # 레퍼런스 쌍 로드
    pairs = get_reference_pairs(references_dir)
    if not pairs:
        print("[ERROR] 레퍼런스 이미지 쌍을 찾을 수 없습니다.")
        print(f"  → {references_dir}/before/ 와 {references_dir}/after/ 에 이미지를 추가하세요.")
        sys.exit(1)

    print(f"[INFO] {len(pairs)}개의 before/after 쌍 발견\n")

    # 각 쌍 분석
    analyses = []
    for i, pair in enumerate(pairs, 1):
        print(f"[{i}/{len(pairs)}] 분석 중: {pair['name']}")
        result = analyze_pair(client, pair)
        analyses.append({"pair": pair["name"], "analysis": result})
        if result:
            print(f"    [OK] 완료")

    successful = sum(1 for a in analyses if a["analysis"] is not None)
    print(f"\n[INFO] {successful}/{len(pairs)}개 분석 성공")

    if successful == 0:
        print("[ERROR] 분석 성공한 쌍이 없어 style_profile.json을 생성할 수 없습니다.")
        sys.exit(1)

    # 공통 스타일 추출
    print("\n[INFO] 공통 스타일 패턴 추출 중...")
    style_profile = extract_common_style(client, analyses)
    style_profile["individual_analyses"] = analyses
    style_profile["reference_count"] = len(pairs)
    style_profile["successful_analyses"] = successful

    # 저장
    save_json(style_profile, output_path)
    print(f"\n=== 완료: {output_path} 생성됨 ===\n")

    return style_profile


if __name__ == "__main__":
    refs_dir = sys.argv[1] if len(sys.argv) > 1 else "../references"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "../output/style_profile.json"
    main(refs_dir, out_path)
