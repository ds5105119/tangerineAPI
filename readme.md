## 프로젝트 개요

DRF로 만든 블로그의 API 서버입니다. 다양한 장고의 third-party 앱을 사용하였습니다.

## WBS

![Frame 48](https://github.com/user-attachments/assets/925f4acd-8198-45ae-a4ac-61a47b10596b)

## ERD

<img width="1422" alt="스크린샷 2024-09-02 오전 8 41 12" src="https://github.com/user-attachments/assets/b9c94bbe-abcb-47a5-85e1-6a69bbbb0f52">

## 사용 기술 및 선택 이유

<div align=center> 
  <img src="https://img.shields.io/badge/typescript-3178C6?style=for-the-badge&logo=typescript&logoColor=white"> 
  <img src="https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=white"> 
  <br>
  
  <img src="https://img.shields.io/badge/html5-E34F26?style=for-the-badge&logo=html5&logoColor=white"> 
  <img src="https://img.shields.io/badge/css-1572B6?style=for-the-badge&logo=css3&logoColor=white"> 
  <img src="https://img.shields.io/badge/mysql-4479A1?style=for-the-badge&logo=mysql&logoColor=white"> 
  <br>
  
  <img src="https://img.shields.io/badge/react-61DAFB?style=for-the-badge&logo=react&logoColor=black"> 
  <img src="https://img.shields.io/badge/reactquery-FF4154?style=for-the-badge&logo=reactquery&logoColor=white">
  <img src="https://img.shields.io/badge/nextdotjs-000000?style=for-the-badge&logo=nextdotjs&logoColor=white">
  <img src="https://img.shields.io/badge/node.js-339933?style=for-the-badge&logo=Node.js&logoColor=white">
  <br>

  <img src="https://img.shields.io/badge/django-092E20?style=for-the-badge&logo=django&logoColor=white">
  <img src="https://img.shields.io/badge/amazonaws-232F3E?style=for-the-badge&logo=amazonaws&logoColor=white"> 
  <br>
</div>

### Django

- Django-Rest-Framework
    - DRF는 강력한 시리얼라이저와 뷰셋을 제공하여 API 개발 과정을 간소화합니다. 또한, 다양한 인증 방식과 권한 관리 기능을 지원하여 보안성 높은 API를 구현할 수 있습니다. 이를 통해 클라이언트와 서버 간의 효율적인 데이터 교환이 가능해집니다.
    - Django Rest Framework를 활용하여 RESTful API 서버를 구축하는 것이 목표입니다.
- Django Allauth
    - Django Allauth는 다양한 소셜 인증 제공업체를 지원하며, 유연한 인증 시스템을 구현할 수 있게 해줍니다. 이를 통해 사용자는 편리하게 소셜 계정으로 로그인할 수 있으며, 개발자는 복잡한 인증 로직을 간소화할 수 있습니다. Adapter를 통한 커스터마이징이 용이합니다.
    - 최신 Allauth를 사용합니다.
- DJ-Rest-Auth
    - DJ-Rest-Auth는 Django Rest Framework와 Django Allauth를 통합하여 RESTful API에 대한 인증 기능을 제공합니다.
    - 최신 Allauth와 호환성 문제가 있어, 최신 Allauth와 호환되도록, `*dj_rest_auth.registration.serializers.SocialLoginSerializer`를 상속받아 `validate` 함수를 수정하였습니다.* 수정된 코드는 DJ-Rest-Auth가 업데이트 되어도 Robust함을 보장합니다. (accounts/serializers.py)
- DjangoRestFramework-SimpleJWT
    - DjangoRestFramework-SimpleJWT는 (JWT) 인증을 Django REST Framework에 통합하는 라이브러리입니다. 이는 안전하고 stateless한 인증 메커니즘을 제공하여, 서버의 부하를 줄이고 확장성을 향상시킵니다.
    - JWT 토큰의 상세 Config는 [Settings.py](http://Settings.py) 참조
- Django-Taggit
    - Tag 기능
- Boto3, django-storages
    - AWS S3 버킷에 대한 Presigned POST URL 생성 및 보안

### NEXT.js

- 프론트 엔드를 구현하기 위해 사용하였습니다.
- Axios
    - Axios Instance를 사용한 API 패키징
    - Axios interceptors를 사용한 API 패키징
- React-Query
    - 전역 상태 관리를 위해 사용
- MDX Editor
    - /src/components/editor/ 내 파일들
    - MDX WYSIWYG 에디터를 구현하기 위해 사용하였습니다.
    - Code Editor, MD 형식 Keyboard Shortcut(```, `, # 등)을 지원합니다.
    - 커스텀 이미지 최적화 기능을 통해 S3버킷으로 업로드됩니다.

## 기능

**1. 사용자 인증 및 프로필** 

- 커스텀 유저
    - AbstractBaseUser 상속을 통한 커스텀 유저 기능 구현
- 프로필 상세 보기 기능
- Allauth, Dj-rest-auth, simpleJWT를 통한 JWT기반 소셜 로그인 구현

**2. 게시물 관리**

- 게시물 CRUD
- 게시물 LIST

**3. 댓글 시스템** 

- 댓글 작성, 수정, 삭제

**4. 카테고리 및 태그**

- 태그 목록 및 태그별 게시물 보기
- 태그 상세 정보 페이지

## 후기
본 프로젝트는 Django Rest Framework(DRF)와 Next.js 프레임워크를 동시에 활용하여 개발된 풀스택 어플리케이션입니다. 
백엔드 개발자로서의 커리어를 목표로 하고 있지만, 프론트엔드와 백엔드 사이의 데이터 흐름에 대한 이해를 위해 풀스택 개발을 선택하였습니다.

이 과정에서 약 100개에 달하는 다양한 라이브러리를 적용하며, 현대적인 웹 개발 생태계의 복잡성과 다양성을 직접 경험할 수 있었습니다.
DRF의 시리얼라이저를 사용해보면서 이는 백엔드와 프론트엔드 간 데이터가 직렬화-역직렬화 되는 과정을 심도 높게 이해할 수 있었습니다.

또한 DRF의 페이지네이션 클래스를 커스터마이징하여 클라이언트의 요구사항에 맞는 유연한 데이터 제공 방식을 구현했습니다. 이 과정에서 백엔드의 성능 최적화와 프론트엔드의 사용자 경험 향상이 어떻게 맞물리는지 깊이 있게 고민할 수 있었습니다.
Dj-rest-auth, allauth, simpleJWT를 사용한 소셜 로그인 연동, JWT 기반 로그인 설계를 하면서 프론트엔드에서 AXIOS 인스턴스까지 유기적으로 연결되는 구조를 매우 상세히 배울 수 있었습니다. 
덕분에 프론트엔드와 백엔드 간의 효과적인 협업 방식도 이번 프로젝트를 통해 체득할 수 있었습니다.
트러블슈팅 과정에서는 다양한 도구와 기술을 활용했습니다. Django에서는 로깅을 사용하였으며, 프론트에서는 React-Query의 Devtools를 사용하였고, console또한 사용하였습니다.

이 프로젝트를 통해 백엔드 개발자의 핵심 역할이 단순히 데이터를 제공하는 것을 넘어, 프론트엔드의 요구사항을 정확히 이해하고 최적화된 솔루션을 설계하는 것임을 깊이 인식하게 되었습니다.
결론적으로, 프론트엔드의 관점에서 백엔드를 바라보며, 더 나은 서비스를 제공하기 위한 통찰력을 얻을 수 있었고, 이는 향후 개발자로서의 커리어에 invaluable한 자산이 될 것입니다.
