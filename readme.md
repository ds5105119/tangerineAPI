## 🍊 감귤마켓

<p align="center">
  <img src="https://github.com/user-attachments/assets/5d15e62e-179b-4faf-8921-b10f732514a7" />
</p>
</br>

## **👨‍⚕️ Team Introduction & Members**

### **💬 팀 소개**

조화와 지속 가능한 성장을 추구하는 $\bf{\color{orange}감귤조직}$입니다.

팀 개개인 모두 주어진 위치에 상관없이 모든 일에 오너십을 가지고 적극적으로 참여하는 것을 최우선으로 생각하고 있습니다.

지금도 좋은 동료가 되기 위해 **치열하게 고민하고, 학습하고, 성장하고 있습니다**.

| **공미희** | **권용인** | **김동현** |
| --- | --- | --- |
| 백앤드 Products 앱 및 테스트 코드 담당 및 문서화 | 백앤드 Likes 앱 담당 |  |
| [https://github.com/heeeee-github](https://github.com/heeeee-github) | [https://github.com/vanhalenpanama](https://github.com/vanhalenpanama) | [https://github.com/ds5105119](https://github.com/ds5105119) |
|  | 데이터 분야에 관심이 많습니다. | CS/CE의 전반적인 분야에 흥미를 갖고 있습니다. |
</br>

## 프로젝트 개요

### 우리가 이번 프로젝트에서 도전했던 것

- **Backend, Frontend, ML**의 긴밀한 통합

### 목적

- **감귤마켓**은 자신의 스토어에서 판매하고 있는 상품(감귤)을 등록하여 홍보할 수 있는 SNS입니다.

### 대상

- **주 타겟**은 감귤 판매 및 구매에 관심있는 사람들입니다.
- **부 타겟** SNS를 통해 일상을 공유하고 소통하고자 하는 모든 사람들입니다.

### 프로젝트 일정

**워밍업 기간**

- **날짜**: September 13, 2024 (Friday) – September 20, 2024 (Friday)
- **기간**: 8일

**Main Development Phase**

- **날짜**: September 23, 2024 (Monday) – October 14, 2024 (Monday)
- **기간**: 22일
</br>

## WBS

초기에 핵심 기능을 구현한 뒤, 애자일한 프로세스를 적용시켰습니다.

<p align="center">
  <img src="https://github.com/user-attachments/assets/d0043fee-f138-401e-83f2-cce38112adbb" />
</p>

(이미지 변경 예정)
</br>

## ERD 및 전체 다이어그램

<p align="center">
  <img src="https://github.com/user-attachments/assets/b27b06f7-d0d4-4271-8a7b-e6e9a9fc9f60" />
</p>

(이미지 변경 예정)
</br>

## API 주소

스웨거
</br>

## 시작 가이드

### 환경(Requirements)

### 설치(Install)

### 백엔드(Backend)

### 프론트엔드(Frontend)
</br>

## 📚 기술스택

### Environment

1. **IDE: Pycharm, VSCode**
    1. VCS 및 Jira와의 원활한 통합 지원
2. **Language: Python, TypeScript**
    1. Poetry를 활용한 파이썬 패키지 관리
3. **Project Management System: Jira**
    1. 개발에 집중할 수 있는 체계적인 환경 제공
    2. 🖇️ GitHub Actions와 Jira 자동화를 통해 다양한 상용 프로그램과 통합된 환경을 구축하였습니다. GitHub issue 생성 시 자동으로 브랜치가 생성되며, Jira는 해당 이슈를 자동으로 추적합니다. 브랜치가 병합되면 Jira 이슈와 GitHub 이슈도 자동으로 종료됩니다.
        1. Github issue
        2. Github branch
        3. Discord via webhooks
        4. Notion
        5. Pycharm
        6. Automation
4. **VCS: Github**
    1. 🛠️ 깃허브 액션 등 다양한 기능 사용
        1. Github issue는 Github Projects에서 자동으로 추적됩니다.
        2. Jira와의 완벽한 통합
        3. 세심한 이슈 템플릿
    2. 🏗️ Github flow branch 전략 채택
        1. ✨ Lightspeed Development
5. **지속적 통합 및 지속적 배포**
    1. Python: pre-commit을 사용하였습니다.
        1. 📝 pre-commit hooks을 통한 사전 검사
        2. ⚡️ Ruff를 사용한 매우 빠른 파이썬 코드 linting 및 formatting
        3. 🧪 Pytest를 통한 테스트 자동화
    2. Frontend: Prettier를 사용하여 코드 일관성 유지
    3. ☁️ AWS
        1. ECR, ECS등의 AWS 서비스를 사용하여 CI Pipeline을 구축하였습니다.
6. **비용 최적화**
    1. AWS에서 Spot Instance를 사용하여 비용 또한 약 65% 절감할 수 있습니다. (현재는 AWS에서 2024년 12월 31일까지 무료로 제공하는 t4g.small Instance를 사용 중입니다.)
    2. CloudFlare R2 객체 스토리지를 도입하여 CDN을 기본으로 지원하며(R2 URL필요), S3 대비 예상 소모 비용을 약 80% 절감하였습니다. (1TB 저장 공간 사용, 월 100만 번의 쓰기, 1000만 번의 읽기 작업 시 예상 요금 $14.35, S3와 동일한 내구성 보장)
</br>

### Development

**Backend: Django**

- **Django Rest Framework (DRF)**
    - DRF는 강력한 시리얼라이저와 뷰셋을 제공하여 API 개발을 효율적으로 지원합니다. 다양한 인증 방식과 권한 관리 기능을 갖추고 있어 신뢰성 있는 API 구현이 가능합니다. 이를 통해 클라이언트와 서버 간의 원활한 데이터 교환이 실현됩니다.
    - 본 프로젝트의 목표는 Django Rest Framework를 활용하여 RESTful API 서버를 구축하는 것입니다.
- **Django Allauth**
    - Django Allauth는 다양한 소셜 인증 제공업체를 지원하여 유연한 인증 시스템을 구현할 수 있도록 돕습니다. 사용자는 소셜 계정을 통해 편리하게 로그인할 수 있으며, 개발자는 복잡한 인증 로직을 단순화할 수 있습니다. Adapter와 Serializer 등 다양한 커스텀된 로직을 통해 프로젝트에 긴밀하게 융합될 수 있도록 하였습니다.
    - **최신 버전의 Allauth를 사용합니다.**
- **DJ-Rest-Auth**
    - DJ-Rest-Auth는 Django Rest Framework와 Django Allauth를 통합하여 RESTful API에 대한 인증 기능을 제공합니다.
    - 최신 버전의 Allauth와의 호환성 문제를 해결하기 위해, `dj_rest_auth.registration.serializers.SocialLoginSerializer`를 상속받아 `validate` 함수를 수정하였습니다. 이로 인해 DJ-Rest-Auth의 업데이트에도 Robust하게 동작합니다 (파일 경로: `accounts/serializers.py`, AllAuth 64.2.1 버전에서 65.0.1 버전으로 업그레이드 하여 정상적으로 동작함을 확인)
- **DjangoRestFramework-SimpleJWT**
    - DjangoRestFramework-SimpleJWT는 JSON Web Token (JWT) 인증을 Django REST Framework에 통합하는 라이브러리입니다. 이는 안전하고 stateless한 인증 메커니즘을 제공하여 서버 부하를 감소시키고 확장성을 향상시킵니다. 서비스 확장을 지원하는 데 유용합니다.
    - JWT 토큰에 대한 상세한 설정은 [Settings.py](http://settings.py/)를 참조하시기 바랍니다.
- **Boto3**
    - Boto3는 S3 호환 스토리지에 대한 접근을 제공하여 정적 파일 저장소의 전환을 간편하게 만듭니다.
    - Presigned POST URL을 생성하여 일반적인 Presigned URL보다 안전하게 파일 업로드를 처리할 수 있습니다. 이는 악의적인 사용자가 정적 파일 저장소에서 비정상적인 행동을 취하는 것을 사전에 방지하는 데 도움이 됩니다.
- **Confluent-Kafka**
    - 상용 Kafka의 Python Client, librdkafka C/C++의 Python Wrapper로 librdkafka는 초당 100만개의 Producer Message, 300만개의 Consume Message에 대응할 수 있어 매우 안정적인 서비스를 제공할 수 있습니다
- **Channels**
    - 비동기 WebSocket API 구현
    - 직접 구현한 Kafka용 Channel Layer는 비동기 처리 및 다중 프로세스로 실행되는 배포 환경을 고려하여 세심하게 설계되었습니다.
</br>

**프론트엔드 기술 스택: Next.js/14**

- **TypeScript**
    - TypeScript를 사용하여 신뢰성 있는 어플리케이션을 구축하고, 코드 품질 및 DX를 향상시켰습니다.
- **CVA (Class Variance Authority)**
    - CVA를 활용하여 컴포넌트의 재사용성을 높였습니다. 이를 통해 UI 일관성을 유지하면서 개발 효율성을 크게 개선하였습니다.
- **Axios**
    - Axios Instance를 사용하여 백엔드와의 매끄러운 통합을 이룰 수 있었습니다.
- **React Query**
    - React Query 라이브러리를 활용하여 현대적인 애플리케이션의 상태 관리를 구현하였습니다. 서버 상태를 효율적으로 관리하고, 비동기 요청의 데이터 캐싱 및 동기화를 통해 사용자 경험을 향상시켰습니다.
- **Next/Image**
    - Next/Image 컴포넌트를 사용하여 이미지 최적화를 구현하였습니다.
- **FingerprintJS**
    - FingerprintJS를 사용하여 사용자 식별 기능을 강화하였습니다. Pro 버전으로의 업그레이드를 통해 상용 애플리케이션 수준의 안정성을 제공할 수 있습니다.
</br>

**Design: Figma**
</br>

### Communication
</br>

## 화면

| **페인페이지** |  |  |  |
| --- | --- | --- | --- |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |
|  |  |  |  |

### 시연 영상
</br>

## 주요기능

**🍊 사용자 관리**

- **회원가입**
    - 소셜계정으로 가입 가능
        - google, 실제 프로덕션 시 apple도 추가
- **로그인**
- **프로필 관리**
    - 사용자 정보 조회 및 수정
    - 작성 글 목록
    - 작성 댓글 목록
    - 팔로우 리스트
    -

**🍊 상품**

- **(C)** 상품 명, 가격, 설명, 이미지 및 판매 링크(외부 쇼핑몰 URL)
- **(R)** 등록된 감귤 상품 목록 및 상세 정보 조회
- **(U)** 등록된 감귤 상품 정보 수정
- **(D)** 등록된 감귤 상품 삭제

**🍊 게시글**

- **(C)** 텍스트, 이미지, 위치 및 해시태그
- **(R)** 홈피드에서 팔로우한 사용자의 게시글 조회
- **(U)** 작성자 본인에 한해 게시글 내용 및 이미지 수정
- **(D)** 등록된 게시글 삭제

**🍊 소셜기능**

- **팔로우/언팔로우**
    - 다른 사용자 팔로우 및 언팔로우
    - 팔로워 및 팔로잉 목록 조회
- **좋아요**
    - 게시글에 좋아요 표시, 선택 사용자 및 취소
    - 좋아요 수 표시
- **댓글**
    - 게시글에 댓글 작성, 조회, 수정 및 삭제
    - 댓글의 답글
- **채팅**
    - 1:1 실시간 채팅 기능
    - 채팅방 생성, 메시지 전송 및 수신
    - 채팅방 목록 조회
    - 채팅방 나가기

**🍊 검색**

- 사용자, 상품, 해시태그로 검색

**🍊 알림**

- **활동**
    - 새로운 팔로워, 좋아요, 댓글, 이웃 게시글 알림
- **채팅**
    - 채팅 초대, 메세시 수신 알림
- **설정**
    - 알림 켬/끔(App용)

**🍊 보안**

- 사용자 개인정보 및 채팅 내용 암호화 / O
- 사용자 권한(관리자/스태프/일반 사용자) / O

**🍊 성능**

- 자주 접근하는 데이터를 캐싱으로 응답속도 개선
- ~~~ 제한
- 이미지 프리뷰
</br>

## 배포주소

> **개발 버전**
**프론트 서버**
**백엔드 서버**
>
</br>

## 트러블슈팅
</br>

## 회고

**김동현**

- **팀장 및 PM**: Jira와 GitHub를 통해 프로젝트 협업 및 관리 프로세스 개발, VCS 환경에서 pre-commit 및 GitHub Actions을 설정하여 자동화된 코드 검증과 빌드 파이프라인을 구축
- **백엔드**: Accounts 및 Chats 앱을 포함한 주요 기능을 구현, R2와 Boto3를 활용한 데이터 교환 로직을 구축. Kafka를 도입하여 Channels Layer를 지원하는 메시지 시스템을 설계 및 구현. 전체 백엔드의 Docker화, Poetry 도입
- **ML**: Milvus DB 도입
- **프론트엔드**: 전체 프론트엔드 개발, UI/UX 설계
- **디자인**: 예시 WBS를 기반으로 컴포넌트 디자인 및 문서화

**권용인**

- **백엔드**: 사용자가 게시글, 댓글, 대댓글에 좋아요를 추가하거나 취소할 수 있고 좋아요 수를 조회할 수 있는 기능 구현, Likes 앱에 대한 테스트 코드 작성

**공미희**
