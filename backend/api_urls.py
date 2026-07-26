from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from accounts.api_views import RegisterView, CustomTokenView
from items.api_views import LostItemViewSet, FoundItemViewSet
from claims.api_views import ClaimViewSet

router = DefaultRouter()
router.register(r'lost-items', LostItemViewSet, basename='lost-items')
router.register(r'found-items', FoundItemViewSet, basename='found-items')
router.register(r'claims', ClaimViewSet, basename='claims')

urlpatterns = [
    path('token/', CustomTokenView.as_view(), name='token-obtain'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
]