# django-graphql-google-accounts  


ㅈ같은 django-allauth 패키지는 쓰잘데기 없이 7개의 테이블이나 만듭니다.  
그래서 구글 인증과 graphql만을 사용하는 입장으로 너무 별로라 직접 작성하였습니다.
  
```diff
@@ 경고 @@
+ 오직 구글 계정만을 사용하는 기본 사용자 테이블을 생성합니다.
+ 프로젝트 초기 설정에만 사용할 것을 권장합니다.
```  

#### 테이블 컬럼
| column     |
|------------|
| uid        |
| email      |
| nickname   |
| pitcure    |
| locale     |
| is_active  |
| is_admin   |
| updated_at |
| created_at |


### Installation
```bash
pip install django-graphql-google-accounts
```  

### Setup

##### configure base settings  
앱 추가와 설정 값을 할당하고 사용자 모델을 설정합니다.

```python3
# settings.py
INSTALLED_APPS = [
    # ...
    'django.contrib.auth',
    'django.contrib.sites',
    'accounts',
]

AUTHENTICATION_BACKENDS = [
    'accounts.auth.backend.GoogleAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# ...

# Required!
ACCOUNTS_SETTINGS = {
    # change secret example: https://djecrety.ir/
    'token_secret': '^yb9tjg_hif0jym(d42j=vc#kyy=e_t#bjs)xy9y9)=tf&)!-2',
    'claim': {
        'iss': '',  # 발급자
        'sub': '',  # 제목
        'aud': '',  # 대상
        'exp': 1800,  # accessToken expire time seconds
    },
    'refresh_token_expire': 30,  # days / only verify check day
    'google': {
        'client_id': '<GOOGLE-CLIENT-ID>',
        'secret': '<GOOGLE-SECRET>',
        'redirect_uri': '/auth/google/callback',
        'front_redirect_uri': 'http://localhost:8081/auth/google/callback',
    }
}

GRAPHENE = {
    "SCHEMA": "core.schema.schema",
    'MIDDLEWARE': [
        'accounts.middleware.TokenMiddleware'
    ]
}

AUTH_USER_MODEL = 'accounts.User'
```

#### configure urls
```python3
# urls.py
from django.urls import path, include
from accounts.views import GoogleLoginView, GoogleCallbackView


urlpatterns = [
    # ...
    path('login', GoogleLoginView.as_view()),
    path('auth/google/callback', GoogleCallbackView.as_view()),
]
```

### Refresh Token

#### Mutate

###### Schema 등록

```python3
# schema.py
import graphene
from accounts.resolver import UserQuery, RefreshTokenMutation


class Mutation(graphene.ObjectType):
    refresh_token = RefreshTokenMutation.Field()


schema = graphene.Schema(mutation=Mutation)
```

###### HTTP Headers

```json
{
  "Authorization": "Bearer <accessToken>"
}
```

###### Mutation

```graphql
mutation {
  refreshToken(token: "=0ujbayhl43l6m=vleqpa#&k(jaqlv0-p&qn7jl1#*nv@%v&=+") {
    ok
    accessToken
    refreshToken
  }
}
```

### Login Required
accessToken 만료와 `uid`를 소유하고 있는지 검사합니다.

```python3
import graphene
# from example.types import ExampleType
from accounts.decorators.define import login_required


class ExampleQuery:
    example = graphene.List(ExampleType)

    @staticmethod
    @login_required
    def resolve_example():
        return example.objects.all()
```

### Admin(관리자)

비밀번호는 이메일과 같습니다. 구글 로그인 진행 할 때 비밀번호가 비어있을 경우 이메일을 django pbk2 암호화를 통해 자동으로 설정하여 저장합니다.
