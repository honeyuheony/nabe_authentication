from django.urls import path, include
from accounts import views

urlpatterns = [
    path('kakao/login/', views.kakao_login, name='kakao_login'),
    path('kakao/callback/', views.kakao_callback, name='kakao_callback'),
    path('kakao/login/finish/', views.KakaoLogin.as_view(),
         name='kakao_login_todjango'),
    path('kakao/userinfo/', views.kakao_get_userinfo,
         name='kakao_get_userinfo'),
]