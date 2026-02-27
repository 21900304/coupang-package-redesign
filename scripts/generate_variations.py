#!/usr/bin/env python3
"""
입력 이미지 + style_profile.json + task.md를 기반으로
Gemini API를 사용하여 5개의 패키지 디자인 변형을 생성한다.

사용법:
  python generate_variations.py <input_image> <style_profile.json> <output_dir> [task.md]
"""

import sys
import json
from pathlib import Path
from google.genai import types
from utils import get_client, load_image_as_part, load_json, save_json

# ─────────────────────────────────────────────────────────────
# 기본 5개 Variation 스타일 정의
# task.md에서 커스텀 지정 시 덮어씌워짐
# ─────────────────────────────────────────────────────────────
DEFAULT_VARIATIONS = [
    {
        "id": 1,
        "name": "minimal_white",
        "label": "미니멀 화이트",
        "emphasis": (
            "pure white background, minimalist design, maximum whitespace, "
            "single accent color, clean sans-serif typography, simple geometric shapes, "
            "modern and airy feel"
        ),
    },
    {
        "id": 2,
        "name": "premium_dark",
        "label": "프리미엄 다크",
        "emphasis": (
            "deep dark background (near black or very dark navy), gold or silver accents, "
            "luxury feel, elegant serif or refined sans-serif font, "
            "subtle metallic texture, high contrast elements"
        ),
    },
    {
        "id": 3,
        "name": "natural_craft",
        "label": "내추럴 크래프트",
        "emphasis": (
            "kraft paper texture background, earth tones (beige, brown, sage green), "
            "organic shapes and botanical illustrations, handwritten or organic font style, "
            "eco-friendly and natural aesthetic, warm and inviting"
        ),
    },
    {
        "id": 4,
        "name": "modern_flat",
        "label": "모던 플랫",
        "emphasis": (
            "bold flat color blocks, vibrant primary or pastel colors, "
            "geometric shapes, no gradients or shadows, "
            "strong bold typography, contemporary graphic design style"
        ),
    },
    {
        "id": 5,
        "name": "luxury_gradient",
        "label": "럭셔리 그라디언트",
        "emphasis": (
            "smooth elegant gradient background (e.g. deep purple to rose gold, "
            "navy to gold, or emerald to teal), metallic shimmer effect, "
            "refined typography, sophisticated color transitions, "
            "premium positioning, soft glow highlights"
        ),
    },
]


def analyze_input_image(client, input_path: str) -> str:
    """입력 이미지의 제품 특성 분석"""
    print("  입력 이미지 분석 중...")
    input_part = load_image_as_part(input_path)

    prompt = """
이 제품 패키지 이미지를 분석하여 아래 항목을 간결하게 설명해주세요:
1. 제품명/브랜드명 (이미지에 보이는 텍스트)
2. 제품 카테고리 (식품, 화장품, 생활용품 등)
3. 주요 색상 구성
4. 현재 패키지 형태 (박스, 파우치, 병, 튜브 등)
5. 현재 디자인의 특징 및 분위기
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[input_part, types.Part.from_text(text=prompt)],
    )
    return response.text.strip()


def build_prompt(product_analysis: str, style_profile: dict, variation: dict, task_notes: str) -> str:
    """이미지 생성용 프롬프트 구성"""
    layout_principles = "\n".join(
        f"- {p}" for p in style_profile.get("layout_principles", [])
    )
    transformation_rules = "\n".join(
        f"- {r}" for r in style_profile.get("transformation_rules", [])
    )
    style_keywords = ", ".join(style_profile.get("style_keywords", []))

    task_section = f"\n[추가 요청사항]\n{task_notes}\n" if task_notes.strip() else ""

    return f"""
Create a redesigned product packaging image for an e-commerce listing (Coupang, Korean market).

[Original Product Analysis]
{product_analysis}

[Design Style for This Variation: {variation['label']}]
{variation['emphasis']}

[Brand Style Guidelines (learned from reference redesigns)]
- Design philosophy: {style_profile.get('design_philosophy', 'modern and premium')}
- Premium direction: {style_profile.get('premium_direction', 'elevate to premium tier')}
- Style keywords: {style_keywords}
- Typography style: {style_profile.get('typography_style', 'clean, modern')}

[Layout Principles]
{layout_principles}

[Transformation Rules]
{transformation_rules}
{task_section}
[Output Requirements]
- Keep the product identity (product name, category) clearly visible
- Apply the {variation['label']} design style completely
- Clean background appropriate for product listing
- High quality, photorealistic packaging visualization
- Square or portrait orientation
- The redesign should look significantly more sophisticated than the original
"""


def save_image_from_response(response, output_path: str) -> bool:
    """Gemini 응답에서 이미지 추출 및 저장"""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    for candidate in response.candidates:
        for part in candidate.content.parts:
            if part.inline_data is not None:
                with open(output_path, "wb") as f:
                    f.write(part.inline_data.data)
                return True
    return False


def generate_variation(client, input_path: str, style_profile: dict, variation: dict,
                        product_analysis: str, output_path: str, task_notes: str) -> dict:
    """단일 variation 생성 (실패 시 1회 재시도)"""
    prompt = build_prompt(product_analysis, style_profile, variation, task_notes)

    for attempt in range(1, 3):  # 최대 2회 시도
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-exp-image-generation",
                contents=[
                    types.Part.from_text(text="원본 패키지 참고 이미지:"),
                    load_image_as_part(input_path),
                    types.Part.from_text(text=prompt),
                ],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE", "TEXT"],
                    temperature=0.8,
                ),
            )

            if save_image_from_response(response, output_path):
                return {"status": "success", "path": output_path, "attempts": attempt}
            else:
                print(f"    [WARN] 이미지 미반환 (attempt {attempt}/2), 재시도...")

        except Exception as e:
            print(f"    [ERROR] attempt {attempt}/2 실패: {e}")
            if attempt == 2:
                return {"status": f"error: {e}", "path": output_path, "attempts": attempt}

    return {"status": "no_image_returned", "path": output_path, "attempts": 2}


def load_task_notes(task_md_path: str | None) -> str:
    """task.md에서 스타일 메모 섹션 추출"""
    if not task_md_path or not Path(task_md_path).exists():
        return ""
    with open(task_md_path, "r", encoding="utf-8") as f:
        return f.read()


def main(input_path: str, style_profile_path: str, output_dir: str,
         task_md_path: str = None, custom_variations: list = None):

    print("\n=== Image Generator 시작 ===\n")

    # 입력 파일 확인
    if not Path(input_path).exists():
        print(f"[ERROR] 입력 이미지 없음: {input_path}")
        sys.exit(1)
    if not Path(style_profile_path).exists():
        print(f"[ERROR] style_profile.json 없음: {style_profile_path}")
        print("  → 먼저 analyze_references.py를 실행하세요.")
        sys.exit(1)

    client = get_client()
    style_profile = load_json(style_profile_path)
    task_notes = load_task_notes(task_md_path)
    variations = custom_variations if custom_variations else DEFAULT_VARIATIONS

    # 입력 이미지 분석
    product_analysis = analyze_input_image(client, input_path)
    print(f"\n[제품 분석 결과]\n{product_analysis}\n")

    # 5개 variation 생성
    results = []
    for variation in variations:
        filename = f"variation_{variation['id']}_{variation['name']}.png"
        output_path = str(Path(output_dir) / filename)
        print(f"[{variation['id']}/5] 생성 중: {variation['label']} → {filename}")

        result = generate_variation(
            client, input_path, style_profile, variation,
            product_analysis, output_path, task_notes
        )
        result["style_label"] = variation["label"]
        result["variation_id"] = variation["id"]
        results.append(result)

        status_icon = "[OK]" if result["status"] == "success" else "[FAIL]"
        print(f"    {status_icon} {result['status']}")

    # 메타데이터 저장
    meta = {
        "input_image": input_path,
        "product_analysis": product_analysis,
        "style_profile_used": style_profile_path,
        "task_md": task_md_path,
        "variations": results,
    }
    save_json(meta, str(Path(output_dir) / "generation_meta.json"))

    # 결과 요약
    success_count = sum(1 for r in results if r["status"] == "success")
    print(f"\n=== 완료: {success_count}/{len(results)}개 생성 성공 ===")
    print(f"저장 위치: {output_dir}\n")

    return results


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("사용법: python generate_variations.py <input_image> <style_profile.json> <output_dir> [task.md]")
        sys.exit(1)

    main(
        input_path=sys.argv[1],
        style_profile_path=sys.argv[2],
        output_dir=sys.argv[3],
        task_md_path=sys.argv[4] if len(sys.argv) > 4 else None,
    )
