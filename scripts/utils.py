"""
공통 유틸리티 함수
"""
import os
import json
from pathlib import Path
from google import genai
from google.genai import types

# 프로젝트 루트의 .env 파일 자동 로드
def _load_env_file():
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

_load_env_file()


def get_client() -> genai.Client:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "[ERROR] GEMINI_API_KEY가 설정되지 않았습니다.\n"
            "방법 1 (권장): 프로젝트 루트에 .env 파일 생성 후 아래 내용 입력\n"
            "  GEMINI_API_KEY=your-api-key-here\n"
            "방법 2: export GEMINI_API_KEY='your-api-key-here'"
        )
    # 시스템에 GOOGLE_API_KEY가 있으면 SDK가 그걸 우선 사용하므로
    # 명시적으로 우리 키를 쓰도록 임시 제거 후 복원
    _old = os.environ.pop("GOOGLE_API_KEY", None)
    client = genai.Client(api_key=api_key)
    if _old is not None:
        os.environ["GOOGLE_API_KEY"] = _old
    return client


def load_image_as_part(image_path: str) -> types.Part:
    """이미지 파일을 Gemini API Part 객체로 변환"""
    ext = Path(image_path).suffix.lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
    }
    mime_type = mime_map.get(ext, "image/png")

    with open(image_path, "rb") as f:
        data = f.read()

    return types.Part.from_bytes(data=data, mime_type=mime_type)


def parse_json_response(text: str) -> dict:
    """Gemini 응답에서 JSON 파싱 (마크다운 코드블록 처리 포함)"""
    text = text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return json.loads(text)


def get_reference_pairs(references_dir: str) -> list[dict]:
    """before/after 레퍼런스 이미지 쌍 로드"""
    before_dir = Path(references_dir) / "before"
    after_dir = Path(references_dir) / "after"

    if not before_dir.exists() or not after_dir.exists():
        raise FileNotFoundError(
            f"[ERROR] references/before 또는 references/after 폴더가 없습니다: {references_dir}"
        )

    image_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    before_files = sorted(
        f for f in before_dir.iterdir() if f.suffix.lower() in image_extensions
    )

    pairs = []
    for before_file in before_files:
        # 같은 이름의 after 파일 찾기
        after_file = None
        for ext in image_extensions:
            candidate = after_dir / (before_file.stem + ext)
            if candidate.exists():
                after_file = candidate
                break

        if after_file:
            pairs.append({
                "name": before_file.stem,
                "before": str(before_file),
                "after": str(after_file),
            })
        else:
            print(f"  [WARN] {before_file.name}에 대응하는 after 이미지 없음, 스킵")

    return pairs


def save_json(data: dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  [저장] {path}")


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
