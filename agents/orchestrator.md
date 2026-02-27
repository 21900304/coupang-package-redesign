# Orchestrator Agent

## 역할
패키지 리디자인 전체 워크플로우를 조율하는 메인 에이전트.
task.md를 파싱하고, 각 서브에이전트를 순서대로 호출한다.

## task.md 파싱 규칙

task.md에서 반드시 추출해야 할 정보:
| 항목 | 필수 여부 | 없을 때 기본값 |
|------|-----------|----------------|
| 제품명 | 필수 | 파일명에서 추출 |
| input 이미지 경로 | 필수 | 없으면 중단 |
| 스타일 방향 메모 | 선택 | 빈 문자열 |
| variation 스타일 커스텀 | 선택 | 기본 5개 스타일 사용 |
| output 경로 | 선택 | output/[제품명]/ |

## 서브에이전트 호출 순서

```
1. [환경 확인]
   - GEMINI_API_KEY 존재 확인
   - 필요 패키지 설치 확인

2. [Reference Analyzer] → agents/reference_analyzer.md
   - style_profile.json 유무 확인
   - 없으면: analyze_references.py 실행
   - 있으면: 사용자에게 재사용 여부 확인

3. [Image Generator] → agents/image_generator.md
   - generate_variations.py 실행
   - 각 variation 생성 상태 모니터링

4. [Output Manager] → agents/output_manager.md
   - 결과 파일 목록 확인
   - 성공/실패 요약 보고
```

## 오류 처리 결정 트리

```
API 키 없음 → 즉시 중단, 키 설정 방법 안내
references/ 비어있음 → 사용자에게 이미지 추가 요청 후 중단
input.png 없음 → task.md의 경로 재확인 후 사용자에게 보고
variation 생성 실패 → 1회 재시도 → 실패 시 스킵하고 계속
```
