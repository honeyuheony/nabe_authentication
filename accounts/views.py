from django.conf import settings
from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from accounts.models import User
from allauth.socialaccount.models import SocialAccount

from dj_rest_auth.registration.views import SocialLoginView
from rest_framework_simplejwt.tokens import RefreshToken
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

import requests
from rest_framework import status
from json.decoder import JSONDecodeError 

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

'''
django JWT 와 kakao access token 만료기간 동일하게 설정
사용자가 API 호출 (Django 토큰 검사)
1. 로그인풀려있으면 => 403 messages.massage : 'Token is invalid or expired'
⇒ 메시지 확인 후 jwt refresh token 통해 재발급 후 API 재호출
⇒ 없으면 카카오 로그인 다시 진행 (로그아웃)
2. 로그인 유효하면 
'''
class KakaoTokenRefresh(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        refresh_token = request.query_params.get('kakao_refresh_token')
        code = request.GET.get("code")
        rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
        kakao_token_api = 'https://kauth.kakao.com/oauth/token'
        data = {
            'grant_type': 'refresh_token',
            'client_id': rest_api_key,
            'refresh_token': refresh_token
        }
        token_response = requests.post(kakao_token_api, data=data)

        return JsonResponse(token_response.json())

BASE_URL = 'http://15.164.210.47:8000/'
KAKAO_CALLBACK_URI = BASE_URL + 'accounts/kakao/callback/'

# kakao 로그인 요청
# GET /oauth/authorize -> 카카오 계정 로그인 및 동의 진행 -> callback redirect
class KakaoAuthorize(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        rest_api_key = getattr(settings, 'KAKAO_REST_API_KEY')
        redirect_uri = f'{BASE_URL}/accounts/signin/kakao/callback'
        kakao_auth_api = 'https://kauth.kakao.com/oauth/authorize?response_type=code'

        return redirect(
            f'{kakao_auth_api}&client_id={rest_api_key}&redirect_uri={redirect_uri}'
        )
# Token으로 사용자 정보 확인 => 로그인 or 회원가입 처리
class KaKaoSignInCallBack(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        code = request.GET.get("code")
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
        
        user_info_response = requests.get('https://kapi.kakao.com/v1/oidc/userinfo', headers={"Authorization": f'Bearer ${kakao_access_token}'}).json()
        data = {'code': code, 'access_token': kakao_access_token}
        accept = requests.post(
            f"{BASE_URL}accounts/kakao/login/finish/", data=data)
        accept_status = accept.status_code  
        if accept_status == 200:
            email = user_info_response.get('email')
            user = User.objects.get(email=email)
            user.kakao_access_token = kakao_access_token
            user.kakao_refresh_token = kakao_refresh_token
            user.save()
            jwt = accept.json().get('access_token')
            refresh_token = accept.json().get('refresh_token')
            return JsonResponse({"email": email, 'drf_access_token': jwt, 'drf_refresh_token': refresh_token})
        else:
            return JsonResponse({"error": "error"})

class KakaoLogin(SocialLoginView):
    permission_classes = [permissions.AllowAny]
    adapter_class = kakao_view.KakaoOAuth2Adapter
    client_class = OAuth2Client
    callback_url = KAKAO_CALLBACK_URI

class KakaoUserinfo(APIView):
    def get(self, request):
        access_token = request.user.kakao_access_token
        profile_request = requests.get(
            "https://kapi.kakao.com/v2/user/me", headers={"Authorization": f"Bearer {access_token}"})
        profile_json = profile_request.json()
        kakao_account = profile_json.get('kakao_account')
        if kakao_account == None:
            #Token is invaild
            return HttpResponse({request.user}, status=401)
        userinfo = {}
        userinfo['email'] = kakao_account.get('email', None)
        userinfo['nickname'] = kakao_account.get('profile', None).get('nickname', None)
        userinfo['age_range'] = kakao_account.get('age_range', None)
        userinfo['birthday'] = kakao_account.get('birthday', None)
        userinfo['gender'] = kakao_account.get('gender', None)
        return JsonResponse(userinfo)




    
