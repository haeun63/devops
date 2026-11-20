# Week 12 - GitHub Actions

## 1. CI 파이프라인
- Ruff 코드 검사 및 unittest 테스트
- Docker 이미지 자동 빌드 및 GHCR 업로드
- PR 검사 성공 확인

![CI 성공](images/ci-success.png)

## 2. 오류 검사
- 문법 오류 → CI 실패
- 변수 오타 → 린트 실패
- HTTP 500 응답 → 테스트 실패
- 오류 수정 후 CI 성공

![CI 실패](images/ci-fail.png)

## 3. 브랜치 보호
- main 브랜치 보호 규칙 설정
- CI 실패 시 PR 병합 차단
- 수정 후 병합 성공

![브랜치 보호](images/branch-protection.png)

## 4. 결과
GitHub Actions를 통해 코드 검사, 테스트,
이미지 빌드를 자동화했다.
