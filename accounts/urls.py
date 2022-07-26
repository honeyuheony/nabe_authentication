from django.urls import path, include
from accounts import views

urlpatterns = [
    path('kakao/login/', views.KakaoAuthorize.as_view(), name='kakao_login'),
    path('kakao/callback/', views.KaKaoSignInCallBack.as_view(), name='kakao_callback'),
    path('kakao/login/finish/', views.KakaoLogin.as_view(),
         name='kakao_login_todjango'),
    path('kakao/userinfo/', views.KakaoUserinfo.as_view(),
         name='kakao_get_userinfo'),
]