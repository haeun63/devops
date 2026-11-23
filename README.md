## 방명록 프로젝트 — GitOps 운영

### 1. 아키텍처

GitHub → GitHub Actions → GHCR
→ Argo CD → Kubernetes(Minikube)
→ guestbook + Redis

- GitHub: 소스 코드와 배포 설정 관리
- GitHub Actions: 테스트 및 Docker 이미지 빌드
- GHCR: Docker 이미지 저장
- Argo CD: GitHub의 배포 설정을 Kubernetes에 자동 반영
- Kubernetes: guestbook과 Redis 실행

### 2. 기술 스택

- Python / Flask
- Docker
- GitHub Actions
- GitHub Container Registry(GHCR)
- Kubernetes / Minikube
- Argo CD
- Redis
- Metrics Server

### 3. 실행 및 상태 확인

```bash
minikube -p week11 start --driver=docker
kubectl get pods
kubectl get deployments
kubectl get applications -n argocd
```

guestbook은 Pod 2개, Redis는 Pod 1개가 정상 실행되는 것을 목표로 한다.

### 4. GitOps 배포 절차

1. 코드를 수정한다.
2. 브랜치를 만들고 Pull Request를 생성한다.
3. PR 병합 후 GitHub Actions에서 이미지를 빌드한다.
4. GHCR에 새 Docker 이미지가 게시됐는지 확인한다.
5. deployment.yaml의 이미지 태그를 변경한다.
6. 이미지 변경 PR을 병합한다.
7. Argo CD가 자동으로 Kubernetes에 배포한다.

### 5. ConfigMap 및 Secret

- ConfigMap: 애플리케이션 환경 설정
- Secret: 비밀번호 등 민감한 설정
- 실제 비밀번호와 인증 토큰은 GitHub에 업로드하지 않는다.

### 6. 오류 및 해결 기록

**문제 1: ImagePullBackOff**
- 증상: Pod에서 이미지 다운로드 실패
- 원인: GHCR에 없는 이미지 태그
- 해결: 실제 게시된 이미지 태그를 확인하고 배포 설정 수정

**문제 2: Argo CD Progressing**
- 증상: Synced이지만 Healthy가 되지 않음
- 확인: kubectl get pods, kubectl describe pod
- 조치: 이미지 오류 및 readiness probe 상태 확인 후 복구

**문제 3: Metrics API not available**
- 증상: kubectl top 명령어 실행 실패
- 확인: Metrics Server와 APIService 상태
- 해결: Metrics Server 준비 상태 확인 및 재시작

### 7. 13주차 실습

- Git 변경으로 replicas 자동 배포
- Self-heal로 직접 변경한 replicas 복구
- Git Revert로 이전 배포 상태 복원
- Prune으로 ConfigMap 자동 삭제
- GitHub Actions와 Argo CD 이미지 배포
- Metrics Server CPU·메모리 모니터링
- 부하 테스트 및 로그 확인
# DevOps

2026년 2학기 DevOps 실습

## 주차별 내용

- [2주차 - 실습 환경 구축과 버전 관리 기초](./week02/)
- [3주차 - 셸 스크립팅](./week03/)
- [4주차 - 자동화와 협업 및 네트워크](./week04/)
- [5주차 - Docker 및 GitHub Issue](./week05/)
- [7주차 - Docker Compose](./week07/)
