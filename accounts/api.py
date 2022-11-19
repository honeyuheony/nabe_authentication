import requests
from django.conf import settings
from ninja_extra import (
    api_controller,
    http_get, http_post
)

from accounts.models import User
from ninja.constants import NOT_SET


BASE_URL = 'http://15.164.210.47:8000'
KAKAO_CALLBACK_URI = BASE_URL + '/kakao/callback'

@api_controller('kakao', tags=['kakao'], auth=NOT_SET, permissions=[])
class KakaoAuthorizeCallback:
    @http_get('/login/callback')
    def kakao_login(self, code: str):
        rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
        kakao_token_api = 'https://kauth.kakao.com/oauth/token'
        data = {
            'grant_type': 'authorization_code',
            'client_id': rest_api_key,
            'redirection_uri': KAKAO_CALLBACK_URI,
            'code': code
        }
        token_response = requests.post(kakao_token_api, data=data)
        kakao_access_token = token_response.json().get('access_token')
        kakao_refresh_token = token_response.json().get('refresh_token')

        user_info_response = requests.get('https://kapi.kakao.com/v1/oidc/userinfo',
                                          headers={"Authorization": f'Bearer ${kakao_access_token}'}).json()
        data = {'code': code, 'access_token': kakao_access_token}
        accept = requests.post(
            f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code
        if accept_status == 200:
            email = user_info_response.get('email')
            user = User.objects.get(email=email)
            user.kakao_access_token = kakao_access_token
            user.kakao_refresh_token = kakao_refresh_token
            jwt = accept.json().get('access_token')
            refresh_token = accept.json().get('refresh_token')
            return JsonResponse({"email": email, 'drf_access_token': jwt, 'drf_refresh_token': refresh_token})
        else:
            return JsonResponse({"error": "error"})