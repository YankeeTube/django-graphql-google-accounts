# django-graphql-google-accounts  


fk django allauth creates 7 tables.  
but we need only google accounts and we will only use graphql token authentication.

<span style="color:red">WARNING</span>  
Create a user table that uses only Google accounts.  
Use is not recommended unless it is the initial setting.

### Table Columns
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
add this app and settings

```python3
# settings.py
INSTALLED_APPS = [
    # ...
    'django.contrib.auth',
    'django.contrib.sites',
    'accounts',
]

# ...

ACCOUNTS_SETTINGS = {
    # change secret example: https://djecrety.ir/
    'token_secret': '^yb9tjg_hif0jym(d42j=vc#kyy=e_t#bjs)xy9y9)=tf&)!-2',
    'claim': {
        'iss': '',  # issuer
        'sub': '',  # subject
        'aud': '',  # audience
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

###### Register Schema

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
verify accessToken timeout and `uid`

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