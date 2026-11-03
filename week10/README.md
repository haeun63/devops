# Week 10 - 쿠버네티스 배포와 서비스

실습일: 2026-11-03 (KST)

기존 Deployment의 중복 컨테이너 오류를 수정하고, Service 로드밸런싱, 복제본 확장, Pod 자가 치유, v2 롤링 업데이트와 v1 롤백을 확인했다. 최초 업데이트에서 연결 오류를 관찰한 뒤 readiness와 종료 대기 설정을 추가했다. 재검증에서는 v1 → v2 → v1 전환 동안 HTTP 요청 314건이 모두 성공했다.

## 1. 시작 상태와 오류 수정

`minikube`의 `default` 네임스페이스에 `guestbook` Deployment와 NodePort Service가 존재했다. Deployment에는 `web`과 이전 실습의 `guestbook` 컨테이너가 함께 들어 있었다. 두 컨테이너가 같은 Pod 안에서 포트 5000을 사용하면서 `Address already in use` 오류가 발생했고, Pod는 `1/2` 상태였다.

이전 `guestbook` 컨테이너를 제거하고 `web` 하나만 남겼다. 이미지 `ghcr.io/haeun63/guestbook:v1`로 복제본 2개가 모두 준비된 것을 확인했다.

- [수정 전 Deployment](evidence/01-before-fix.yaml)
- [수정 후 Deployment·Service·Pod 상태](evidence/02-baseline.txt)

## 2. 복제본 확장과 Service 로드밸런싱

```bash
kubectl scale deployment guestbook --replicas=4
kubectl get pods -l app=guestbook -o wide
```

4개 Pod가 모두 `1/1 Running` 상태가 되었다. 클러스터 내부에서 `http://guestbook/healthz`로 20회 요청한 결과, 아래 4개 hostname이 응답했다.

```text
guestbook-76546cfc9-dd4mg
guestbook-76546cfc9-m8tk7
guestbook-76546cfc9-mzds6
guestbook-76546cfc9-pb59m
```

Service의 `app=guestbook` selector가 여러 Pod로 요청을 전달하는 것을 확인했다. 브라우저의 `port-forward`는 한 Pod에 연결되므로, 로드밸런싱 검증에는 클러스터 내부 Service 주소를 사용했다.

- [4개 Pod 상태](evidence/03-scale4-pods.txt)
- [20회 요청의 실제 응답](evidence/03-load-balancing.txt)

## 3. 복제본 5개와 자가 치유

복제본을 5개로 확장한 뒤 Pod 하나를 삭제했다. Deployment를 삭제하지 않았으므로 ReplicaSet이 부족해진 Pod를 자동 생성했고, 다시 5개가 준비된 상태로 복구되었다.

| 구분 | Pod 이름 | UID |
| --- | --- | --- |
| 삭제한 Pod | `guestbook-76546cfc9-chtsr` | `49eccfa7-28a8-4165-ba1c-dbfb7d09e37f` |
| 자동 생성된 Pod | `guestbook-76546cfc9-pb5qm` | `8205e8ad-6725-40a1-ba50-8894ad7881ea` |

이름과 UID가 모두 달라졌으므로 기존 Pod가 재시작한 것이 아니라 새 Pod가 생성된 것을 확인할 수 있다.

- [5개 Pod 상태](evidence/06-scale5-pods.txt)
- [5개 Pod 명령 출력 이미지](evidence/06-scale5-pods.png)
- [삭제 및 복구 과정](evidence/06-self-healing.txt)
- [삭제 전 JSON](evidence/06-before-self-healing.json), [삭제 후 JSON](evidence/06-after-self-healing.json)

## 4. v2 이미지와 롤링 업데이트

`guestbook/templates/index.html`의 제목에 `v2`를 추가했다. v2는 현재 소스의 Dockerfile 설정을 사용하므로 개인화된 제목이 반영되었다.

| 상태 | 이미지 | 실제 HTML 제목 |
| --- | --- | --- |
| 기존 v1 | `ghcr.io/haeun63/guestbook:v1` | `InhaTC DevOps 방명록` |
| 새 v2 | `ghcr.io/haeun63/guestbook:v2` | `정하은 DevOps 방명록 v2` |
| v1 롤백 | `ghcr.io/haeun63/guestbook:v1` | `InhaTC DevOps 방명록` |

이번 실습에서는 GHCR에 이미지를 push하지 않았다. 빌드 컨텍스트를 minikube 노드의 `/tmp/guestbook-week10-v2`에 복사한 뒤, 기존 containerd와 nerdctl로 이미지를 로컬 빌드했다.

```bash
# minikube 노드 내부에서 실행한 빌드
sudo systemctl start buildkit
cd /tmp/guestbook-week10-v2
sudo nerdctl --namespace k8s.io build --progress plain \
  -t ghcr.io/haeun63/guestbook:v2 .
```

이후 Deployment의 `web` 이미지를 v2로 바꾸고 rollout 완료와 ReplicaSet 교체를 확인했다.

```bash
kubectl set image deployment/guestbook web=ghcr.io/haeun63/guestbook:v2
kubectl rollout status deployment/guestbook
kubectl rollout history deployment/guestbook
kubectl rollout undo deployment/guestbook
kubectl rollout status deployment/guestbook
```

처음 기록한 history에서는 revision 4가 중복 컨테이너를 제거한 v1, revision 5가 v2였다. 롤백 후 v1이 revision 6으로 기록되었다. 이후 readiness 설정 추가와 재검증, YAML의 이미지 변경 실습으로 revision이 더 생성되었다. 최종 history의 revision 10은 YAML을 수정하고 apply한 v2이며, revision 11은 YAML을 v1으로 복원하고 apply한 상태다. v2 ReplicaSet과 롤백한 Deployment에는 변경 이유 annotation을 남겼다.

- [v2 빌드 로그](evidence/04-v2-build.txt)
- [v2 rollout 과정](evidence/04-v2-rollout.txt), [v2 리소스 상태](evidence/04-v2-resources.txt)
- [v1 제목](evidence/04-title-v1.txt), [v2 제목](evidence/04-title-v2.txt), [롤백 후 제목](evidence/05-title-after-rollback.txt)
- [롤백 전 history](evidence/05-history-before-rollback.txt), [롤백 후 history](evidence/05-history-after-rollback.txt)
- [롤백 과정](evidence/05-rollback.txt), [최종 history](evidence/08-history-final.txt)

## 5. 연결 오류 관찰과 재검증

첫 번째 v1 → v2 → v1 전환을 Service 경유 `/healthz` 요청으로 관찰했다. 473회 중 연결 오류가 12회 발생했다. 따라서 첫 실행 결과만으로 무중단 업데이트가 되었다고 판단하지 않았다.

새 Pod가 요청을 받을 준비가 되었는지 확인하고, 종료 중인 Pod로 이미 전달된 요청이 처리될 시간을 주도록 배포 설정을 보완했다.

| 설정 | 최종 값 | 목적 |
| --- | --- | --- |
| `readinessProbe` | `/readyz`, 포트 5000, 주기 1초 | 준비된 Pod로 서비스 요청 전달 |
| `minReadySeconds` | `2` | 준비 상태를 유지한 뒤 가용 Pod로 계산 |
| `maxUnavailable` | `0` | 교체 중 기존 가용 복제본 유지 |
| `maxSurge` | `1` | 새 Pod를 하나씩 추가 |
| `preStop` | 종료 전 3초 대기 | 종료 시 연결 오류 완화 |

같은 설정을 유지한 채 v1 → v2 → v1을 다시 수행했다. **재검증 결과는 314회 요청, 연결 오류 0회이며, 전환 과정에서 서로 다른 hostname 6개가 관찰되었다.** 이는 이번 실습의 관찰 구간에서 확인한 결과다.

`/healthz` 응답은 HTTP 접근 가능 여부와 응답 Pod를 확인하는 용도이며, `/readyz`는 요청을 받을 준비 상태를 확인하는 용도로 사용했다. 원시 로그의 시각은 UTC(`+00:00`)이며 KST는 9시간을 더하면 된다.

- [최초 관찰 로그: 473회·오류 12회](evidence/04-availability.jsonl)
- [설정 보완 후 v2 rollout](evidence/08-readiness-v2-rollout.txt)
- [재검증 로그: 314회·오류 0회](evidence/08-availability-after-readiness.jsonl)

## 6. 최종 상태와 다시 접속하기

실습 후 이미지와 복제본 수는 안내 실습의 상태로 복구했다.

| 항목 | 최종 상태 |
| --- | --- |
| 클러스터 / 네임스페이스 | `minikube` / `default` |
| Deployment | `guestbook`, `web` 컨테이너 1개 |
| 배포 이미지 | `ghcr.io/haeun63/guestbook:v1` |
| 복제본 | `2/2 Ready` |
| Pod | [최종 리소스 기록 참고](evidence/09-final-resources.txt) |
| Service | `NodePort`, `80 → 5000`, `nodePort: 30080` |
| 브라우저 접속 | `http://localhost:8080` (`port-forward` 사용) |
| 화면 제목 | `InhaTC DevOps 방명록` |

최종 매니페스트도 v1·복제본 2개로 맞췄다. 소스 템플릿에는 다음 빌드에 사용할 v2 수정이 남아 있다. 현재 v1 화면은 배포 이미지에서 제공되므로 로컬 템플릿 수정과 별도로 동작한다. 임시 확인용 Pod는 정리했다.

- [최종 Deployment](evidence/09-final-deployment.yaml)
- [최종 Service](evidence/09-final-service.yaml)

PowerShell이 닫혀 브라우저 접속이 끊기면 다음 명령으로 포트 전달을 다시 연다.

```powershell
wsl -d Ubuntu-24.04 -u haeun -- sh -lc 'kubectl port-forward service/guestbook 8080:80'
```

이 명령을 실행한 창을 열어 둔 상태에서 [방명록](http://localhost:8080)에 접속한다. PowerShell을 닫으면 포트 전달은 종료되지만 Deployment와 Service는 클러스터에 남아 있다.

v2를 다시 빌드하려면 WSL의 `~/devops/guestbook`에서 다음 명령을 사용할 수 있다.

```bash
minikube image build -t ghcr.io/haeun63/guestbook:v2 .
kubectl set image deployment/guestbook web=ghcr.io/haeun63/guestbook:v2
kubectl rollout status deployment/guestbook
```

v2 이미지는 현재 minikube에 로컬로 저장되어 있으며 `imagePullPolicy: IfNotPresent`로 사용한다. 다른 클러스터에서는 해당 이미지 빌드 또는 레지스트리 배포가 먼저 필요하다.

## 7. 교안 전체 실습 확인

| 교안 항목 | 수행 내용 | 근거 |
| --- | --- | --- |
| 클러스터와 매니페스트 확인 | minikube context와 노드 상태, 서버 dry-run, Pod 레이블 확인 | [환경·검증 기록](evidence/11-context-and-validation.txt) |
| Deployment 배포 | 중복 컨테이너 수정 후 v1 복제본 2개 준비 확인 | [배포 상태](evidence/02-baseline.txt) |
| p28 선언형 적용과 멱등성 | YAML의 replicas를 `2 → 3 → 2`로 바꾸고 각각 apply, 변경 없이 재적용했을 때 `unchanged` 확인 | [YAML 확장·복원 기록](evidence/12-declarative-scaling.txt) |
| Pod 자가 치유 | 5개 중 하나를 삭제하고 새 이름·UID를 가진 대체 Pod 생성 확인 | [자가 치유 기록](evidence/06-self-healing.txt) |
| Service 설정 | selector `app=guestbook`, `80 → 5000`, NodePort 30080, Endpoints 확인 | [Service describe](evidence/11-service-description.txt) |
| p35 Memory 저장소 관찰 | 임시 글을 저장한 뒤 Service 경유 GET 20회에서 서로 다른 두 Pod의 글 표시 여부 비교 | [Memory 저장소 기록](evidence/13-memory-storage.txt) |
| 명령형 확장과 로드밸런싱 | 복제본 4개, Service 응답의 hostname 4개 확인 | [확장](evidence/03-scale4-pods.txt), [응답](evidence/03-load-balancing.txt) |
| v2 빌드·롤링 업데이트 | v2 로컬 이미지 빌드, set image, rollout 상태와 화면 제목 확인 | [빌드](evidence/04-v2-build.txt), [rollout](evidence/04-v2-rollout.txt) |
| 버전 이력·롤백·변경 이유 | history와 annotation 기록, v1 화면 복구 확인 | [최초 롤백](evidence/05-rollback.txt), [최종 history](evidence/08-history-final.txt) |
| 업데이트 중 요청 확인 | 최초 연결 오류를 기록하고 설정 보완 후 314회 요청에서 오류 0회 확인 | [재검증 로그](evidence/08-availability-after-readiness.jsonl) |
| p56 YAML로 이미지 변경 | YAML의 image를 v2로 바꾸어 apply 후 v2 확인, 다시 v1으로 바꾸어 apply 후 복원 확인 | [YAML 이미지 변경 기록](evidence/14-yaml-image-update.txt), [v2 적용 YAML](evidence/14-v2-applied-deployment.yaml) |
| 과제와 정리 | 복제본 5개 캡처, 자가 치유, 업데이트·롤백 기록 후 최종 v1·2개 복원 및 임시 Pod 정리 | [5개 Pod 이미지](evidence/06-scale5-pods.png), [최종 리소스](evidence/09-final-resources.txt) |

p28 실습에서는 YAML의 replicas 값이 실제 Deployment의 원하는 수를 결정하는 것을 확인했다. `kubectl scale`로 바꾼 값과 파일 내용이 다를 때 apply하면 파일의 값으로 맞춰진다. 같은 파일을 다시 적용했을 때 `unchanged`가 표시되는 것도 함께 기록했다.

p35 실습에서는 Memory 방식의 글이 Pod별 프로세스 메모리에 저장되는 것을 확인했다. 임시 글이 저장된 Pod에서는 표시되고 다른 Pod에서는 표시되지 않아, 같은 Service 주소를 요청해도 응답한 Pod에 따라 글이 나타나거나 사라지는 현상이 관찰되었다. Service가 글을 공유하거나 동기화하는 것은 아니다. 이 임시 샘플은 최종 이미지 전환 과정에서 Pod가 교체되면서 함께 사라졌다.

p56 실습에서는 `kubectl set image`와 YAML 수정 후 apply가 모두 Pod 템플릿을 바꾸어 롤링 업데이트를 유발하는 것을 확인했다. 최종 파일은 v1으로 복원했으므로 다시 apply해도 현재 v1 배포와 일치한다.

## 8. GitHub 제출

제출 저장소는 [haeun63/devops](https://github.com/haeun63/devops), 브랜치는 `main`, 과제 태그는 [week10](https://github.com/haeun63/devops/tree/week10/week10)이다. 커밋 메시지는 `week10: Deployment and Service`이며, 이번 실습의 매니페스트·템플릿 수정과 `week10` 기록을 제출 대상으로 정리했다.

```bash
cd ~/devops
git add guestbook/k8s/deployment.yaml guestbook/k8s/service.yaml guestbook/templates/index.html week10
git commit -m "week10: Deployment and Service"
git tag week10
git push origin main
git push origin week10
```

브랜치와 태그가 같은 커밋을 가리키는지 다음 명령으로 확인할 수 있다.

```bash
git ls-remote origin refs/heads/main refs/tags/week10
```

## 참고 문서

- [Kubernetes Deployment 공식 문서](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [준비 상태 검사 공식 문서](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)
