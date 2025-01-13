from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

##########
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# API Documentation Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Library Management System API",
        default_version='v1',
        description="A REST API for managing library operations including books, users, and loans",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@library.local"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Endpoints
    path('api/v1/', include('library_api.urls')),
    
    # Authentication Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # Optional: Include auth URLs for browsable API
    path('api-auth/', include('rest_framework.urls')),
]

# Custom 404 and 500 handlers
handler404 = 'library_api.views.custom_404'
handler500 = 'library_api.views.custom_500'

# Debug toolbar URLs (only loaded in debug mode)
from django.conf import settings
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns