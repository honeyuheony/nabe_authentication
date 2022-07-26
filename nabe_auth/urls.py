"""nabe_auth URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from accounts import views as account_views
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenVerifyView,
    TokenRefreshView,
)

schema_view = get_schema_view(
    openapi.Info(
        title="nabe_authentication",
        default_version='0.1',
        description="nabe_project account API 문서",
        terms_of_service="",
        contact=openapi.Contact(email="kwh1019@koreatech.ac.kr"), # 부가정보
        license=openapi.License(name="mit"),     # 부가정보
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),
    # 이 아랫 부분은 우리가 사용하는 app들의 URL들을 넣습니다.
    path('admin/', admin.site.urls),
    path('accounts/', include('dj_rest_auth.urls')),
    path('accounts/', include('allauth.urls')),
    path('accounts/', include('accounts.urls')),
    path('token/drf/refresh/', TokenRefreshView.as_view(), name='drf_token_refresh'),
    path('token/drf/verify/', TokenVerifyView.as_view(), name='drf_token_verify'),
    path('token/kakao/refresh/', account_views.KakaoTokenRefresh.as_view(), name='kakao_token_refresh'),
]
